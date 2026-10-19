"""Synchronous adapter from the existing coordinator to the async WebSocket Hub."""
import asyncio
from concurrent.futures import TimeoutError

from .llm_client import LLMError
from .hub import HubError
from .protocol import AgentMessage


class AgentUnavailableError(LLMError):
    pass


class HubAgentClient:
    def __init__(self, hub, loop, timeout=120):
        self.hub = hub
        self.loop = loop
        self.timeout = timeout
        self.last_policy = None
        self.last_request_id = None

    def _request(self, agent, session_id, kind, payload):
        if self.loop is None or not self.loop.is_running():
            raise LLMError('Negotiation Hub is not ready. No action was applied.')
        future = asyncio.run_coroutine_threadsafe(
            self.hub.request_agent(agent, session_id, kind, payload, timeout=self.timeout), self.loop)
        try:
            return future.result(timeout=self.timeout + 2)
        except TimeoutError as exc:
            future.cancel()
            raise LLMError('Agent request timed out. No action was applied.') from exc
        except HubError as exc:
            raise AgentUnavailableError(str(exc) or 'Personal agent is unavailable. No action was applied.') from exc
        except Exception as exc:
            raise LLMError(str(exc) or 'Personal agent request failed. No action was applied.') from exc

    def generate(self, actor, profile, history, current):
        if profile is not None:
            raise LLMError('Hub attempted to send a profile to an agent. No action was applied.')
        session_id = getattr(self, 'session_id', None)
        if not session_id:
            raise LLMError('Missing distributed session identifier.')
        response = self._request(actor, session_id, 'NEGOTIATION_REQUEST',
                                 {'history': history, 'current_proposal': current})
        payload = response.payload
        if payload.get('error'):
            raise LLMError(payload['error'])
        try:
            self.last_policy = payload['policy']
            self.last_request_id = payload.get('request_id')
            action = payload.get('action')
            if action is None and response.type == 'POLICY_EVENT' and self.last_policy.get('status') == 'blocked':
                return {'actor': actor, 'action': 'ESCALATE', 'proposal': None}
            if action is None:
                raise KeyError('action')
            # Model-generated public text and summaries are intentionally discarded.
            return {key: action.get(key) for key in ('actor', 'action', 'proposal')}
        except (KeyError, TypeError) as exc:
            raise LLMError('Personal agent returned an invalid structured action. No action was applied.') from exc

    def resolve_approval(self, session_id, request, choice):
        result = self._request('Alice', session_id, 'APPROVAL_DECISION', {
            'request_id': request['id'], 'choice': choice, 'proposal': request['proposal'], 'amount': request['amount']})
        return bool(result.payload.get('authorized'))
