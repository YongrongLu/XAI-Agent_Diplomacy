from backend.negotiation_engine import NegotiationEngine
from backend.policy_engine import departure, disclosure, contribution


def test_policies():
    assert departure('07:00').code == 'HARD_CONSTRAINT_VIOLATION'
    assert departure('09:30').status == 'allowed'
    assert disclosure('date_reason').status == 'blocked'
    assert disclosure('availability').status == 'allowed'
    assert contribution(60).status == 'allowed'
    assert contribution(150).status == 'approval_required'


def test_branches_and_replay():
    for choice, hotel, amount in [('approve', 'The Tidal House', 150), ('reject', 'The Palmetto', 60)]:
        engine = NegotiationEngine()
        engine.start()
        while engine.status == 'running':
            engine.next()
        assert engine.status == 'pending_approval'
        before = len(engine.events)
        engine.next()
        assert len(engine.events) == before
        request_id = engine.pending['id']
        assert engine.decide('approve' if choice == 'approve' else 'reject', request_id)['status'] == 'running'
        while engine.status == 'running':
            engine.next()
        state = engine.public_state()
        assert state['outcome']['hotel']['name'] == hotel
        assert state['outcome']['alice_extra'] == amount
        assert sum(state['outcome']['contributions'].values()) == state['outcome']['hotel']['total']
        assert state['outcome']['booking_status'] == 'Proposed — not booked'
        assert 'date' not in str(state).lower()
        assert engine.decide('approve', request_id)['error'] == 'No matching pending request'
        replay = NegotiationEngine()
        replay.start()
        assert replay.events == NegotiationEngine().start()['events']
