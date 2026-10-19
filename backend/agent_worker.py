"""Standalone personal-agent process. Each instance loads one local profile only."""
import argparse
import asyncio
import json
import logging
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

from pydantic import ValidationError

from .live_engine import NegotiationAction, TripProposal
from .llm_client import LLMError, OpenAICompatibleClient
from .policy_engine import Decision, contribution, departure
from .protocol import AgentMessage

DATA = Path(__file__).parent / 'data'
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger('agent-worker')


def load_owned_profile(agent):
    name = agent.lower()
    if name not in {'alice', 'bob', 'carol'}:
        raise ValueError('Agent must be alice, bob, or carol')
    profile = json.loads((DATA / f'{name}.json').read_text(encoding='utf-8'))
    if profile.get('name', '').lower() != name:
        raise ValueError('Local profile owner does not match this agent process')
    return profile


def trusted_public_message(actor, action, proposal, outcome):
    if outcome.status == 'blocked':
        return f'{actor}’s suggested plan was blocked by a local policy boundary.'
    if action.action in ('PROPOSE', 'COUNTER'):
        return (f'{actor} suggests {proposal.hotel_id.title()}, a {proposal.departure} Key West departure, '
                f'and nightlife on Day {proposal.nightlife_day}. Alice adds ${proposal.alice_extra_total} above equal hotel share.')
    if action.action == 'ACCEPT':
        return f'{actor} accepts the current trip proposal. This is agreement only; nothing is booked.'
    if action.action == 'REJECT':
        return f'{actor} declines the current proposal.'
    return f'{actor} cannot settle the current plan within delegated authority.'


class PersonalAgent:
    def __init__(self, agent, client=None, profile=None):
        self.name = agent.title()
        self.profile = profile if profile is not None else load_owned_profile(agent)
        if self.profile['name'].lower() != agent.lower():
            raise ValueError('Profile ownership mismatch')
        self.client = client or OpenAICompatibleClient()
        self.pending_approvals = {}
        self.sessions = {}

    def decide(self, candidate, current):
        action = candidate.action
        proposal = candidate.proposal if action in ('PROPOSE', 'COUNTER') else (TripProposal.model_validate(current) if action == 'ACCEPT' and current else None)
        if action == 'ACCEPT' and proposal is None:
            return Decision('blocked', 'NO_ACTIVE_PROPOSAL', 'There is no active proposal to accept.')
        if proposal:
            if self.name == 'Carol':
                result = departure(proposal.departure)
                if result.status == 'blocked':
                    return result
            if self.name == 'Bob' and proposal.nightlife_day == 2:
                return Decision('blocked', 'BOB_UNAVAILABLE', 'Bob is unavailable on Day 2 evening; Day 3 remains possible.')
            if self.name == 'Alice':
                result = contribution(proposal.alice_extra_total)
                if result.status == 'approval_required':
                    return result if action in ('PROPOSE', 'COUNTER') else Decision('blocked', 'APPROVAL_REQUIRED', 'Alice must approve this exact contribution before accepting.')
                return result
        return Decision('allowed', 'LOCAL_BOUNDARIES_PASSED', 'This action fits the agent’s local policy.')

    async def handle(self, message):
        if message.type == 'APPROVAL_DECISION':
            payload = message.payload
            request = self.pending_approvals.pop(payload.get('request_id'), None)
            exact = bool(request and request['session_id'] == message.session_id
                         and request['proposal'] == payload.get('proposal')
                         and request['amount'] == payload.get('amount'))
            approved = exact and payload.get('choice') == 'approve'
            result = {'authorized': bool(approved), 'request_id': payload.get('request_id'),
                      'code': 'EXACT_ONE_TIME_APPROVAL' if approved else 'APPROVAL_REJECTED'}
            return self.reply(message, 'POLICY_EVENT', result)

        if message.type != 'NEGOTIATION_REQUEST':
            return self.reply(message, 'POLICY_EVENT', {'status': 'blocked', 'code': 'UNSUPPORTED_REQUEST'})
        try:
            payload = message.payload
            local_state = self.sessions.setdefault(message.session_id, {'turns': 0, 'current_proposal': None})
            raw = await asyncio.to_thread(self.client.generate, self.name, self.profile,
                                          payload.get('history', []), payload.get('current_proposal'))
            candidate = NegotiationAction.model_validate(raw)
            if candidate.actor != self.name:
                raise ValueError('Actor mismatch')
            result = self.decide(candidate, payload.get('current_proposal'))
        except (LLMError, ValidationError, ValueError, TypeError) as exc:
            logger.warning('%s produced no action (%s)', self.name, type(exc).__name__)
            return self.reply(message, 'POLICY_EVENT', {'error': 'Agent could not produce a valid action. No action was applied.'})
        safe = candidate.model_dump()
        safe['public_message'] = None
        safe['reasoning_summary'] = None
        # Private text is never copied from the model into the transport message.
        response_type = 'APPROVAL_REQUIRED' if result.status == 'approval_required' else ('POLICY_EVENT' if result.status == 'blocked' else 'NEGOTIATION_ACTION')
        request_id = None
        if result.status == 'approval_required':
            request_id = f'{message.session_id}:{uuid.uuid4()}'
            self.pending_approvals[request_id] = {'session_id': message.session_id,
                'proposal': candidate.proposal.model_dump(), 'amount': candidate.proposal.alice_extra_total}
        if result.status in {'allowed', 'approval_required'}:
            local_state['turns'] += 1
            local_state['last_action'] = candidate.action
            local_state['current_proposal'] = (candidate.proposal.model_dump() if candidate.action in ('PROPOSE', 'COUNTER')
                                               else payload.get('current_proposal'))
        policy = {'status': result.status, 'code': result.code, 'explanation': result.explanation}
        if result.status == 'blocked':
            return self.reply(message, response_type, {'policy': policy})
        return self.reply(message, response_type, {'action': safe, 'policy': policy, 'request_id': request_id})

    @staticmethod
    def reply(request, kind, payload):
        return AgentMessage(session_id=request.session_id, message_id=str(uuid.uuid4()), sender=request.recipient,
                            recipient=request.sender, type=kind, timestamp=datetime.now(timezone.utc),
                            correlation_id=request.correlation_id, payload=payload)


async def run_agent(agent, hub_url='ws://127.0.0.1:8000/ws/agents'):
    from websockets.asyncio.client import connect
    worker = PersonalAgent(agent)
    delay = 1
    while True:
        try:
            async with connect(hub_url, open_timeout=10, close_timeout=3) as socket:
                register = AgentMessage(session_id='registration', message_id=str(uuid.uuid4()), sender=agent,
                    recipient='hub', type='AGENT_REGISTER', timestamp=datetime.now(timezone.utc), payload={'agent': agent})
                await socket.send(register.model_dump_json())
                logger.info('%s connected to Hub', agent)
                delay = 1
                async for raw in socket:
                    try:
                        request = AgentMessage.model_validate_json(raw)
                        response = await worker.handle(request)
                        await socket.send(response.model_dump_json())
                    except Exception as exc:
                        logger.warning('Rejected Hub message (%s)', type(exc).__name__)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.warning('%s Hub connection unavailable (%s); retrying', agent, type(exc).__name__)
            await asyncio.sleep(delay)
            delay = min(delay * 2, 15)


def main():
    parser = argparse.ArgumentParser(description='Run one local Agent Diplomacy personal agent')
    parser.add_argument('--agent', required=True, choices=['alice', 'bob', 'carol'])
    parser.add_argument('--hub', default=os.getenv('AGENT_DIPLOMACY_HUB_URL', 'ws://127.0.0.1:8000/ws/agents'))
    args = parser.parse_args()
    try:
        asyncio.run(run_agent(args.agent, args.hub))
    except KeyboardInterrupt:
        logger.info('%s stopped', args.agent)


if __name__ == '__main__':
    main()
