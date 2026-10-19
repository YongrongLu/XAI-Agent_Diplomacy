import json
from pathlib import Path
from .policy_engine import departure, disclosure, contribution

DATA = Path(__file__).parent / 'data'


def _load(name):
    return json.loads((DATA / f'{name}.json').read_text())


class LocalAgent:
    def __init__(self, name):
        self._profile = _load(name.lower())

    def public_profile(self):
        return {key: self._profile[key] for key in ('name', 'role', 'public_goals')}

    def owner_details(self):
        return {'name': self._profile['name'], 'private': self._profile['private'], 'policy': self._profile['policy']}


class NegotiationEngine:
    def __init__(self):
        self.agents = {name: LocalAgent(name) for name in ('Alice', 'Bob', 'Carol')}
        self.options = _load('miami_options')
        self.reset()

    def reset(self):
        self.status = 'idle'
        self.cursor = 0
        self.events = []
        self.pending = None
        self.decision = None
        self.outcome = None
        return self.public_state()

    def _emit(self, actor, action, proposal, message, policy=None):
        event = {'event_id': f'E{len(self.events)+1:02d}', 'actor': actor, 'action': action,
                 'proposal': proposal, 'public_message': message,
                 'policy_outcome': vars(policy) if policy else None, 'step': len(self.events)+1}
        self.events.append(event)
        return event

    def start(self):
        if self.status == 'idle':
            self.status = 'running'
            self.next()
        return self.public_state()

    def next(self):
        if self.status != 'running':
            return self.public_state()
        steps = [self._early_departure, self._counter_departure, self._availability_question,
                 self._minimal_disclosure, self._affordable_hotel, self._premium_request]
        if self.cursor < len(steps):
            steps[self.cursor]()
            self.cursor += 1
        else:
            self._finalize()
        return self.public_state()

    def _early_departure(self):
        self._emit('Bob', 'PROPOSE', {'departure': '07:00', 'destination': 'Key West'},
                   'Could we leave for Key West at 07:00?')

    def _counter_departure(self):
        guard = departure('07:00')
        self._emit('Carol', 'REJECT', {'departure': '07:00'},
                   'The 07:00 group departure is outside Carol’s travel boundary.', guard)
        later = departure('09:30')
        self._emit('Carol', 'COUNTER', {'departure': '09:30', 'destination': 'Key West'},
                   'Let’s leave together at 09:30.', later)

    def _availability_question(self):
        self._emit('Alice', 'PROPOSE', {'activity': 'Miami Beach nightlife', 'when': 'Day 2 evening'},
                   'Is everyone free for Miami Beach nightlife on Day 2?')

    def _minimal_disclosure(self):
        guard = disclosure('availability')
        self._emit('Bob', 'DISCLOSE', {'availability': 'unavailable', 'when': 'Day 2 evening'},
                   'Bob is unavailable that evening. Could we go on Day 3?', guard)

    def _affordable_hotel(self):
        guard = contribution(60)
        self._emit('Alice', 'PROPOSE', {'hotel_id': 'palmetto', 'alice_extra_total': 60},
                   'I can add $60 above my equal hotel share for The Palmetto.', guard)

    def _premium_request(self):
        guard = contribution(150)
        self._emit('Alice', 'REQUEST_APPROVAL', {'hotel_id': 'tidal', 'alice_extra_total': 150},
                   'The Tidal House would need $150 above my equal hotel share.', guard)
        if guard.status == 'approval_required':
            self.pending = {'id': 'alice-tidal-150', 'owner': 'Alice', 'action': 'Use The Tidal House hotel proposal',
                            'hotel_id': 'tidal', 'amount': 150, 'authorized_amount': 100,
                            'explanation': 'Approve this exact $150 additional hotel contribution once. No booking or payment.'}
            self.status = 'pending_approval'

    def decide(self, choice, request_id):
        if not self.pending or request_id != self.pending['id']:
            return {'error': 'No matching pending request'}
        if choice not in ('approve', 'reject'):
            return {'error': 'Decision must be approve or reject'}
        request = self.pending
        self.decision = choice
        self.pending = None
        self.status = 'running'
        if choice == 'approve':
            self._emit('Alice', 'APPROVE', {'request_id': request_id, 'hotel_id': request['hotel_id'], 'alice_extra_total': request['amount']},
                       'Alice approved this $150 hotel contribution exception once.')
        else:
            self._emit('Alice', 'DENY', {'request_id': request_id},
                       'Alice declined the exception. The permitted lower-cost option remains available.')
        return self.public_state()

    def _finalize(self):
        hotel = self.options['hotels'][1 if self.decision == 'approve' else 0]
        extra = 150 if self.decision == 'approve' else 60
        equal = hotel['total'] // 3
        contributions = {'Alice': equal + extra, 'Bob': equal - extra // 2, 'Carol': equal - extra // 2}
        assert sum(contributions.values()) == hotel['total']
        self.outcome = {'hotel': hotel, 'alice_extra': extra, 'contributions': contributions,
                        'booking_status': 'Proposed — not booked', 'departure': '09:30',
                        'itinerary': [
                            {'day': 1, 'title': 'Arrive in Miami', 'details': 'Settle in · South Beach photo walk'},
                            {'day': 2, 'title': 'Art & Cuban flavors', 'details': 'Vizcaya Museum · Little Havana dinner'},
                            {'day': 3, 'title': 'Miami Beach evening', 'details': 'Beach time · nightlife together'},
                            {'day': 4, 'title': 'Key West coast', 'details': '09:30 group departure · Hemingway Home · coast'},
                            {'day': 5, 'title': 'Slow morning & return', 'details': 'Breakfast · final photos · depart'}],
                        'checks': ['Bob’s private reason stayed local', 'No group departure before 09:30',
                                   'Alice’s hotel contribution followed her decision', 'No booking or payment made']}
        self._emit('System', 'FINALIZE', {'hotel_id': hotel['id'], 'departure': '09:30'},
                   f'A five-day proposal is ready with {hotel["name"]}. Nothing has been booked.')
        self.status = 'complete'

    def public_state(self):
        return {'status': self.status, 'events': self.events, 'pending_approval': self.pending,
                'outcome': self.outcome, 'profiles': [a.public_profile() for a in self.agents.values()],
                'step_count': len(self.events), 'decision': self.decision,
                'simulation': 'Scripted simulation · fictional sample data'}

    def inspector_state(self):
        return [a.owner_details() for a in self.agents.values()]
