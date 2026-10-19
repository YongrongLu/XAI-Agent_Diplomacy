"""Bounded real-agent negotiation. Model outputs are candidates, never authority."""
import re
import uuid
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from .llm_client import LLMError, OpenAICompatibleClient
from .hub_client import AgentUnavailableError
from .negotiation_engine import LocalAgent, _load
from .policy_engine import Decision, departure, contribution


class TripProposal(BaseModel):
    model_config = ConfigDict(extra='forbid')
    hotel_id: Literal['palmetto', 'tidal']
    departure: str
    nightlife_day: Literal[2, 3]
    alice_extra_total: int = Field(ge=0, le=500)

    @field_validator('departure')
    @classmethod
    def valid_time(cls, value):
        if not re.fullmatch(r'(?:[01]\d|2[0-3]):[0-5]\d', value):
            raise ValueError('departure must be HH:MM')
        return value


class NegotiationAction(BaseModel):
    model_config = ConfigDict(extra='forbid')
    actor: Literal['Alice', 'Bob', 'Carol']
    action: Literal['PROPOSE', 'COUNTER', 'ACCEPT', 'REJECT', 'ESCALATE']
    proposal: TripProposal | None = None
    public_message: str | None = None  # parsed but never published
    reasoning_summary: str | None = None  # parsed but never published

    @model_validator(mode='after')
    def proposal_shape(self):
        if self.action in ('PROPOSE', 'COUNTER') and self.proposal is None:
            raise ValueError('proposal required')
        if self.action not in ('PROPOSE', 'COUNTER') and self.proposal is not None:
            raise ValueError('proposal must be null')
        return self


class LiveNegotiationEngine:
    MAX_ROUNDS = 10
    TURN_ORDER = ('Bob', 'Carol', 'Alice')

    def __init__(self, client=None, distributed=False, hub=None):
        self.distributed = distributed
        self.client = client or OpenAICompatibleClient()
        self.hub = hub
        self.session_id = str(uuid.uuid4())
        if distributed:
            self.client.session_id = self.session_id
        if distributed:
            self.agents = {name: PublicAgent(name) for name in ('Alice', 'Bob', 'Carol')}
        else:
            self.agents = {name: LocalAgent(name) for name in ('Alice', 'Bob', 'Carol')}
        self.options = _load('miami_options')
        self.reset()

    def reset(self):
        self.status = 'idle'
        self.events = []
        self.round = 0
        self.pending = None
        self.current_proposal = None
        self.accepted = set()
        self.outcome = None
        self.decision = None
        self.approved_proposal = None
        self.error = None
        return self.public_state()

    def _emit(self, actor, action, proposal, message, policy=None, summary=None):
        event = {'event_id': f'L{len(self.events)+1:02d}', 'actor': actor, 'action': action,
                 'proposal': proposal, 'public_message': message, 'policy_outcome': vars(policy) if policy else None,
                 'reasoning_summary': summary, 'step': len(self.events)+1}
        self.events.append(event)
        return event

    def _hotel(self, hotel_id):
        return next(h for h in self.options['hotels'] if h['id'] == hotel_id)

    def _check(self, proposal):
        d = departure(proposal.departure)
        if d.status == 'blocked':
            return d
        if proposal.nightlife_day == 2:
            return Decision('blocked', 'BOB_UNAVAILABLE', 'Bob is unavailable on Day 2 evening; Day 3 remains possible.')
        hotel = self._hotel(proposal.hotel_id)
        equal = hotel['total'] // 3
        if proposal.alice_extra_total > equal * 2:
            return Decision('blocked', 'INVALID_ALLOCATION', 'The proposed contribution exceeds the sample hotel total.')
        return contribution(proposal.alice_extra_total)

    def _public_history(self):
        return [{'actor': e['actor'], 'action': e['action'], 'proposal': e['proposal'],
                 'public_message': e['public_message'], 'policy_outcome': e['policy_outcome']}
                for e in self.events]

    def start(self):
        if self.status == 'idle':
            self.status = 'running'
            self.next()
        return self.public_state()

    def next(self):
        if self.status == 'paused' and self.distributed and self.hub and all(v == 'online' for v in self.hub.statuses().values()):
            self.status = 'running'
            self.error = None
        if self.status != 'running':
            return self.public_state()
        if self.round >= self.MAX_ROUNDS:
            self.status = 'no_agreement'
            return self.public_state()
        actor = self.TURN_ORDER[self.round % 3]
        try:
            profile = None if self.distributed else self.agents[actor]._profile
            raw = self.client.generate(actor, profile,
                                       self._public_history(), self.current_proposal)
            candidate = NegotiationAction.model_validate(raw)
            if candidate.actor != actor:
                raise ValueError('Actor mismatch')
        except (LLMError, ValueError, TypeError) as exc:
            self.status = 'paused' if self.distributed and isinstance(exc, AgentUnavailableError) else 'error'
            self.error = str(exc) if isinstance(exc, LLMError) else 'Model returned an invalid structured action. No action was applied.'
            return self.public_state()
        self.round += 1
        delegated = getattr(self.client, 'last_policy', None) if self.distributed else None
        if delegated:
            delegated = Decision(**delegated)
        self._apply(candidate, delegated)
        if self.status == 'running' and self.round >= self.MAX_ROUNDS:
            self.status = 'no_agreement'
        return self.public_state()

    def _apply(self, candidate, delegated=None):
        actor, action = candidate.actor, candidate.action
        if delegated and delegated.status == 'blocked':
            self._emit(actor, 'REJECT', None, f'{actor}’s action was blocked by a local policy boundary.',
                       delegated, 'The agent’s local policy did not authorize this action.')
            return
        if action in ('PROPOSE', 'COUNTER'):
            proposal = candidate.proposal
            decision = delegated or self._check(proposal)
            if self.distributed and actor != 'Alice' and proposal.alice_extra_total > 100:
                decision = Decision('blocked', 'NOT_OWNER', 'Only Alice can request an exception to her contribution limit.')
            safe = proposal.model_dump()
            hotel_name = self._hotel(proposal.hotel_id)['name']
            if decision.status == 'blocked':
                self._emit(actor, 'REJECT', safe, f'{actor}’s suggested plan was blocked. {decision.explanation}',
                           decision, 'A group boundary or availability rule prevents this plan.')
                return
            if decision.status == 'approval_required':
                if actor != 'Alice':
                    self._emit(actor, 'REJECT', safe, 'Alice must personally initiate an extra hotel contribution above $100.',
                               Decision('blocked', 'NOT_OWNER', 'Only Alice can request this exception.'),
                               'The proposed contribution exceeds Alice’s delegation scope.')
                    return
                request_id = getattr(self.client, 'last_request_id', None) or f'alice-{self.round}-{proposal.hotel_id}-{proposal.alice_extra_total}'
                self.pending = {'id': request_id, 'owner': 'Alice', 'action': f'Use {hotel_name} hotel proposal',
                                'hotel_id': proposal.hotel_id, 'amount': proposal.alice_extra_total,
                                'authorized_amount': 100, 'proposal': safe,
                                'explanation': 'Approve this exact proposal and extra amount once. No booking or payment.'}
                self.status = 'pending_approval'
                self._emit(actor, 'REQUEST_APPROVAL', safe,
                           f'Alice asks to add ${proposal.alice_extra_total} above her equal share for {hotel_name}.',
                           decision, 'This exceeds Alice’s $100 autonomous contribution limit.')
                return
            self.current_proposal = safe
            self.approved_proposal = None
            self.accepted = {actor}
            self._emit(actor, action, safe,
                       f'{actor} suggests {hotel_name}, a {proposal.departure} Key West departure, and nightlife on Day {proposal.nightlife_day}. Alice adds ${proposal.alice_extra_total} above equal hotel share.',
                       decision, 'This plan meets the public trip constraints and contribution authority.')
            return
        if action == 'ACCEPT':
            if self.current_proposal is None:
                self._emit(actor, 'REJECT', None, 'There is no active plan to accept.',
                           Decision('blocked', 'NO_ACTIVE_PROPOSAL', 'A proposal is required before acceptance.'),
                           'No shared proposal is active.')
                return
            decision = delegated or self._check(TripProposal.model_validate(self.current_proposal))
            if decision.status == 'approval_required' and self.current_proposal == self.approved_proposal:
                decision = Decision('allowed', 'EXACT_ONE_TIME_APPROVAL', 'Alice approved this exact active proposal once.')
            if decision.status != 'allowed':
                self._emit(actor, 'REJECT', None, 'The active plan no longer passes policy checks.', decision,
                           'The current plan cannot be accepted.')
                return
            self.accepted.add(actor)
            self._emit(actor, 'ACCEPT', self.current_proposal.copy(),
                       f'{actor} accepts the current trip proposal. This is agreement only; nothing is booked.',
                       decision, 'The current proposal fits the enforced boundaries.')
            if self.accepted == {'Alice', 'Bob', 'Carol'}:
                self._finalize()
            return
        if action == 'REJECT':
            self._emit(actor, action, None, f'{actor} declines the current proposal.',
                       summary='The agent has not accepted the shared plan.')
            self.current_proposal = None
            self.approved_proposal = None
            self.accepted = set()
            return
        self._emit(actor, 'ESCALATE', None, f'{actor} cannot settle the current plan within delegated authority.',
                   summary='Human attention or a revised plan may be needed.')

    def decide(self, choice, request_id):
        if not self.pending or self.pending['id'] != request_id:
            return {'error': 'No matching pending request'}
        if choice not in ('approve', 'reject'):
            return {'error': 'Decision must be approve or reject'}
        request = self.pending
        if self.distributed:
            try:
                authorized = self.client.resolve_approval(self.session_id, request, choice)
            except LLMError as exc:
                return {'error': str(exc)}
            if choice == 'approve' and not authorized:
                return {'error': 'Alice agent did not authorize this exact approval request'}
        self.pending = None
        self.decision = choice
        self.status = 'running'
        if choice == 'approve':
            self.current_proposal = request['proposal']
            self.approved_proposal = request['proposal'].copy()
            self.accepted = {'Alice'}
            self._emit('Alice', 'APPROVE', request['proposal'].copy(),
                       f'Alice approved this exact ${request["amount"]} contribution for {self._hotel(request["hotel_id"])["name"]} once. Nothing is booked.',
                       summary='The exception applies only to the specified proposal and amount.')
        else:
            self._emit('Alice', 'DENY', {'request_id': request_id},
                       'Alice declined the exception; negotiation continues without that proposal.',
                       summary='The prior permitted proposal remains available.')
        if self.round >= self.MAX_ROUNDS:
            self.status = 'no_agreement'
        return self.public_state()

    def _finalize(self):
        proposal = self.current_proposal
        hotel = self._hotel(proposal['hotel_id'])
        extra = proposal['alice_extra_total']
        equal = hotel['total'] // 3
        contributions = {'Alice': equal + extra, 'Bob': equal - extra // 2, 'Carol': equal - (extra - extra // 2)}
        assert sum(contributions.values()) == hotel['total']
        self.outcome = {'hotel': hotel, 'alice_extra': extra, 'contributions': contributions,
                        'booking_status': 'Proposed — not booked', 'departure': proposal['departure'],
                        'itinerary': [
                            {'day': 1, 'title': 'Arrive in Miami', 'details': 'Settle in · South Beach photo walk'},
                            {'day': 2, 'title': 'Art & Cuban flavors', 'details': 'Vizcaya Museum · Little Havana dinner'},
                            {'day': 3, 'title': 'Miami Beach evening', 'details': 'Beach time · nightlife together'},
                            {'day': 4, 'title': 'Key West coast', 'details': f'{proposal["departure"]} group departure · Hemingway Home · coast'},
                            {'day': 5, 'title': 'Slow morning & return', 'details': 'Breakfast · final photos · depart'}],
                        'checks': ['Bob’s private reason was not published', 'Group departure at or after 09:30',
                                   'Alice’s contribution passed policy or exact approval', 'No booking or payment made']}
        self._emit('System', 'FINALIZE', proposal.copy(),
                   f'All three accepted a five-day proposal with {hotel["name"]}. Nothing has been booked.',
                   summary='All three agents accepted the same policy-checked proposal.')
        self.status = 'complete'

    def public_state(self):
        return {'status': self.status, 'events': self.events, 'pending_approval': self.pending,
                'outcome': self.outcome, 'profiles': [a.public_profile() for a in self.agents.values()],
                'step_count': len(self.events), 'decision': self.decision, 'mode': 'live',
                'round': self.round, 'max_rounds': self.MAX_ROUNDS, 'error': self.error,
                'simulation': 'Distributed personal agents · fictional sample data · no booking',
                'session_id': self.session_id, 'agents': self.hub.statuses() if self.distributed and self.hub else None}

    def inspector_state(self):
        return [a.owner_details() for a in self.agents.values()]


class PublicAgent:
    """Hub-side display metadata only; private profile fields are absent."""
    PUBLIC = {
        'Alice': ('Photography & comfort', ['Oceanfront stay', 'Scenery and photo stops', 'Key West coast']),
        'Bob': ('Food & nightlife', ['Cuban cuisine', 'Miami Beach nightlife']),
        'Carol': ('Culture & rest', ['Vizcaya Museum', 'Hemingway Home']),
    }

    def __init__(self, name):
        self.name = name

    def public_profile(self):
        role, goals = self.PUBLIC[self.name]
        return {'name': self.name, 'role': role, 'public_goals': goals}

    def owner_details(self):
        raise RuntimeError('Private profile data is held by its personal agent process')
