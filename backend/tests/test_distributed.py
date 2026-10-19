import asyncio
import json
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from backend.agent_worker import PersonalAgent, load_owned_profile
from backend.app import app, hub
from backend.hub import WebSocketHub
from backend.hub_client import AgentUnavailableError
from backend.live_engine import LiveNegotiationEngine
from backend.protocol import AgentMessage


BASE = {'hotel_id': 'palmetto', 'departure': '09:30', 'nightlife_day': 3, 'alice_extra_total': 60}


class MockClient:
    def __init__(self, response): self.response = response
    def generate(self, actor, profile, history, current): return self.response


def action(actor, verb, proposal=None, private='must not leak'):
    return {'actor': actor, 'action': verb, 'proposal': proposal,
            'public_message': private, 'reasoning_summary': private}


def test_workers_load_only_their_owned_profile():
    bob = load_owned_profile('bob')
    assert bob['name'] == 'Bob' and 'reserved_evening_reason' in bob['private']
    assert 'Alice' not in json.dumps(bob) and 'Carol' not in json.dumps(bob)
    try:
        load_owned_profile('../alice')
        assert False, 'invalid agent should not load a profile'
    except ValueError:
        pass


def test_worker_returns_structured_action_and_never_forwards_model_free_text():
    worker = PersonalAgent('bob', MockClient(action('Bob', 'PROPOSE', BASE, 'private evening reason')))
    request = AgentMessage(session_id='s1', message_id='m1', sender='hub', recipient='bob',
        type='NEGOTIATION_REQUEST', timestamp=datetime.now(timezone.utc), payload={'history': [], 'current_proposal': None})
    response = asyncio.run(worker.handle(request))
    assert response.type == 'NEGOTIATION_ACTION'
    assert 'private' not in json.dumps(response.model_dump(mode='json')).lower()
    assert response.payload['action']['public_message'] is None


def test_worker_policy_blocks_carol_departure_and_alice_requires_approval():
    request = AgentMessage(session_id='s1', message_id='m1', sender='hub', recipient='carol',
        type='NEGOTIATION_REQUEST', timestamp=datetime.now(timezone.utc), payload={'history': [], 'current_proposal': None})
    carol = PersonalAgent('carol', MockClient(action('Carol', 'PROPOSE', {**BASE, 'departure': '07:00'})))
    blocked = asyncio.run(carol.handle(request))
    assert blocked.payload['policy']['status'] == 'blocked'
    assert 'action' not in blocked.payload
    premium = {**BASE, 'alice_extra_total': 150}
    request = request.model_copy(update={'sender': 'hub', 'recipient': 'alice'})
    alice = PersonalAgent('alice', MockClient(action('Alice', 'COUNTER', premium)))
    result = asyncio.run(alice.handle(request))
    assert result.type == 'APPROVAL_REQUIRED'
    assert result.payload['policy']['code'] == 'DELEGATION_LIMIT'


def test_hub_register_routes_request_and_updates_disconnect_status():
    async def exercise():
        local_hub = WebSocketHub()
        class Socket:
            async def send_json(self, raw):
                message = AgentMessage.model_validate(raw)
                response = AgentMessage(session_id=message.session_id, message_id='response-1', sender='bob',
                    recipient='hub', type='NEGOTIATION_ACTION', timestamp=datetime.now(timezone.utc),
                    correlation_id=message.correlation_id, payload={'ok': True})
                await local_hub.route_agent_message(response.model_dump(mode='json'), self)
            async def close(self): pass
        socket = Socket()
        register = AgentMessage(session_id='registration', message_id='r1', sender='bob', recipient='hub',
            type='AGENT_REGISTER', timestamp=datetime.now(timezone.utc), payload={'agent': 'bob'})
        await local_hub.route_agent_message(register.model_dump(mode='json'), socket)
        response = await local_hub.request_agent('Bob', 'session-1', 'NEGOTIATION_REQUEST', {}, timeout=1)
        assert response.payload == {'ok': True}
        assert local_hub.statuses()['bob'] == 'online'
        await local_hub.unregister(socket)
        assert local_hub.statuses()['bob'] == 'offline'
    asyncio.run(exercise())


def test_distributed_coordinator_never_loads_profiles_and_uses_trusted_messages(monkeypatch):
    def forbidden(*args, **kwargs): raise AssertionError('Hub must not instantiate profile loader')
    monkeypatch.setattr('backend.live_engine.LocalAgent', forbidden)
    class Remote:
        last_policy = {'status': 'allowed', 'code': 'LOCAL_BOUNDARIES_PASSED', 'explanation': 'Passed.'}
        last_request_id = None
        def generate(self, actor, profile, history, current):
            assert profile is None
            return action(actor, 'PROPOSE', BASE, 'reserved evening reason')
    engine = LiveNegotiationEngine(Remote(), distributed=True)
    engine.start()
    assert engine.events[0]['public_message'].startswith('Bob suggests')
    assert 'reserved' not in json.dumps(engine.public_state()).lower()
    assert 'private' not in json.dumps(engine.public_state()).lower()


def test_distributed_exact_approval_routes_to_alice_and_completes_without_booking():
    premium = {**BASE, 'hotel_id': 'tidal', 'alice_extra_total': 150}
    class RPC:
        last_policy = None
        last_request_id = None
        def generate(self, actor, profile, history, current):
            assert profile is None
            if actor == 'Bob' and not history:
                result = action(actor, 'PROPOSE', BASE)
                self.last_policy = {'status': 'allowed', 'code': 'LOCAL', 'explanation': 'passed'}
            elif actor == 'Carol' and len(history) == 1:
                result = action(actor, 'ACCEPT')
                self.last_policy = {'status': 'allowed', 'code': 'LOCAL', 'explanation': 'passed'}
            elif actor == 'Alice' and len(history) == 2:
                result = action(actor, 'COUNTER', premium)
                self.last_policy = {'status': 'approval_required', 'code': 'DELEGATION_LIMIT', 'explanation': 'Approval required'}
                self.last_request_id = 'alice-exact-request'
            else:
                result = action(actor, 'ACCEPT')
                self.last_policy = {'status': 'allowed', 'code': 'LOCAL', 'explanation': 'passed'}
            return result
        def resolve_approval(self, session_id, request, choice):
            assert request['id'] == 'alice-exact-request'
            assert request['amount'] == 150 and request['proposal'] == premium
            return choice == 'approve'
    remote = RPC()
    engine = LiveNegotiationEngine(remote, distributed=True)
    engine.start(); engine.next(); engine.next()
    assert engine.status == 'pending_approval'
    engine.decide('approve', engine.pending['id'])
    engine.next(); engine.next()
    assert engine.status == 'complete'
    assert engine.outcome['booking_status'] == 'Proposed — not booked'


def test_distributed_disconnect_pauses_without_consuming_turn_and_resumes():
    class Status:
        agents = {'alice': 'offline', 'bob': 'offline', 'carol': 'offline'}
        def statuses(self): return self.agents
    class RPC:
        last_policy = {'status': 'allowed', 'code': 'LOCAL', 'explanation': 'passed'}
        last_request_id = None
        fails = True
        def generate(self, actor, profile, history, current):
            if self.fails:
                raise AgentUnavailableError('Bob agent is offline. No action was applied.')
            return action(actor, 'PROPOSE', BASE)
    remote, status = RPC(), Status()
    engine = LiveNegotiationEngine(remote, distributed=True, hub=status)
    engine.start()
    assert engine.status == 'paused' and engine.round == 0 and engine.events == []
    remote.fails = False; status.agents = {name: 'online' for name in status.agents}
    engine.next()
    assert engine.status == 'running' and engine.round == 1 and len(engine.events) == 1


def test_inspector_is_disabled_by_default(monkeypatch):
    monkeypatch.delenv('AGENT_DIPLOMACY_ENABLE_INSPECTOR', raising=False)
    with TestClient(app) as client:
        response = client.get('/api/inspector')
        assert response.status_code == 404


def test_distributed_api_pauses_offline_and_never_returns_private_profile():
    with TestClient(app) as client:
        state = client.post('/api/session/reset', json={'mode': 'distributed'}).json()
        assert state['mode'] == 'distributed'
        assert set(state['agents']) == {'alice', 'bob', 'carol'}
        assert 'reserved_evening_reason' not in json.dumps(state)
        state = client.post('/api/session/start').json()
        assert state['status'] == 'paused' and state['round'] == 0
        client.post('/api/session/reset', json={'mode': 'scripted'})


def test_dashboard_websocket_uses_structured_protocol_envelope():
    with TestClient(app) as client:
        with client.websocket_connect('/ws/dashboard') as socket:
            message = socket.receive_json()
            assert message['type'] == 'AGENT_STATUS'
            assert message['sender'] == 'hub' and message['recipient'] == 'dashboard'
            assert message['message_id'] and message['session_id'] and message['timestamp']
