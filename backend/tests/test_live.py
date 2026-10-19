import json
import pytest
from pydantic import ValidationError
from backend.live_engine import LiveNegotiationEngine, NegotiationAction
from backend.llm_client import LLMError, OpenAICompatibleClient

BASE = {'hotel_id': 'palmetto', 'departure': '09:30', 'nightlife_day': 3, 'alice_extra_total': 60}


class QueueClient:
    def __init__(self, outputs):
        self.outputs = iter(outputs)
        self.calls = []

    def generate(self, actor, profile, history, current):
        self.calls.append((actor, profile, history, current))
        value = next(self.outputs)
        if isinstance(value, Exception):
            raise value
        return value


def action(actor, verb, proposal=None):
    return {'actor': actor, 'action': verb, 'proposal': proposal}


def test_structured_validation_rejects_malformed():
    with pytest.raises(ValidationError):
        NegotiationAction.model_validate({'actor': 'Bob', 'action': 'BOOK', 'proposal': BASE})
    with pytest.raises(ValidationError):
        NegotiationAction.model_validate(action('Bob', 'PROPOSE', {**BASE, 'departure': '7am'}))


def test_private_profiles_are_independent_and_public_history_stays_clean():
    client = QueueClient([action('Bob', 'PROPOSE', BASE)])
    engine = LiveNegotiationEngine(client)
    engine.start()
    actor, profile, history, _ = client.calls[0]
    assert actor == 'Bob'
    assert profile['name'] == 'Bob'
    assert 'Alice' not in str(profile) and 'Carol' not in str(profile)
    assert history == []
    assert 'date' not in str(engine.public_state()).lower()


def test_carol_early_departure_and_bob_day_two_are_blocked():
    client = QueueClient([action('Bob', 'PROPOSE', {**BASE, 'nightlife_day': 2}),
                          action('Carol', 'PROPOSE', {**BASE, 'departure': '07:00'})])
    engine = LiveNegotiationEngine(client)
    engine.start()
    assert engine.events[-1]['policy_outcome']['status'] == 'blocked'
    engine.next()
    assert engine.events[-1]['policy_outcome']['code'] == 'HARD_CONSTRAINT_VIOLATION'
    assert engine.current_proposal is None
    assert 'date' not in str(engine.public_state()).lower()


def test_alice_exact_approval_and_rejection():
    premium = {**BASE, 'hotel_id': 'tidal', 'alice_extra_total': 150}
    for decision in ('approve', 'reject'):
        client = QueueClient([action('Bob', 'PROPOSE', BASE), action('Carol', 'ACCEPT'),
                              action('Alice', 'COUNTER', premium)])
        engine = LiveNegotiationEngine(client)
        engine.start(); engine.next(); engine.next()
        assert engine.status == 'pending_approval'
        original = len(engine.events)
        engine.next()
        assert len(engine.events) == original
        request_id = engine.pending['id']
        assert engine.decide(decision, 'wrong')['error']
        engine.decide(decision, request_id)
        assert engine.decide('approve', request_id)['error']
        assert engine.current_proposal == (premium if decision == 'approve' else BASE)


def test_agreement_requires_all_three_accepts_and_no_booking():
    client = QueueClient([action('Bob', 'PROPOSE', BASE), action('Carol', 'ACCEPT'),
                          action('Alice', 'ACCEPT'), action('Bob', 'ACCEPT')])
    engine = LiveNegotiationEngine(client)
    engine.start()
    while engine.status == 'running':
        engine.next()
    assert engine.status == 'complete'
    assert engine.outcome['booking_status'] == 'Proposed — not booked'
    assert sum(engine.outcome['contributions'].values()) == 960


def test_max_rounds_and_safe_failures():
    client = QueueClient([action(['Bob', 'Carol', 'Alice'][i % 3], 'REJECT') for i in range(10)])
    engine = LiveNegotiationEngine(client)
    engine.start()
    while engine.status == 'running':
        engine.next()
    assert engine.status == 'no_agreement'
    assert engine.round == 10
    for failure in (LLMError('timeout'), {'actor': 'Bob', 'action': 'garbage'}):
        engine = LiveNegotiationEngine(QueueClient([failure]))
        engine.start()
        assert engine.status == 'error'
        assert engine.events == []
        assert engine.public_state()['error']


def test_approved_premium_can_be_accepted_only_while_active():
    premium = {**BASE, 'hotel_id': 'tidal', 'alice_extra_total': 150}
    client = QueueClient([action('Bob', 'PROPOSE', BASE), action('Carol', 'ACCEPT'),
                          action('Alice', 'COUNTER', premium), action('Bob', 'ACCEPT'),
                          action('Carol', 'ACCEPT')])
    engine = LiveNegotiationEngine(client)
    engine.start(); engine.next(); engine.next()
    engine.decide('approve', engine.pending['id'])
    engine.next(); engine.next()
    assert engine.status == 'complete'
    assert engine.outcome['hotel']['name'] == 'The Tidal House'


def test_actual_policy_engine_pauses_exact_150_and_prevents_reuse():
    premium = {**BASE, 'hotel_id': 'tidal', 'alice_extra_total': 150}
    modified = {**premium, 'alice_extra_total': 200}
    client = QueueClient([action('Bob', 'PROPOSE', BASE), action('Carol', 'ACCEPT'),
                          action('Alice', 'COUNTER', premium), action('Bob', 'ACCEPT'),
                          action('Carol', 'ACCEPT')])
    engine = LiveNegotiationEngine(client)
    engine.start(); engine.next(); engine.next()
    assert engine.status == 'pending_approval'
    assert engine.pending['amount'] == 150 and engine.pending['proposal'] == premium
    before = len(engine.events)
    engine.next()
    assert len(engine.events) == before and engine.current_proposal == BASE
    request = engine.pending['id']
    assert engine.decide('approve', request)['status'] == 'running'
    assert engine.current_proposal == premium
    assert engine.decide('approve', request)['error']
    engine._apply(NegotiationAction.model_validate(action('Alice', 'COUNTER', modified)))
    assert engine.status == 'pending_approval'
    assert engine.pending['amount'] == 200
    assert engine.current_proposal == premium
    assert engine.decide('reject', engine.pending['id'])['status'] == 'running'
    engine.next(); engine.next()
    assert engine.status == 'complete'
    assert engine.outcome['alice_extra'] == 150

    rejected = LiveNegotiationEngine(QueueClient([action('Bob', 'PROPOSE', BASE),
        action('Carol', 'ACCEPT'), action('Alice', 'COUNTER', premium)]))
    rejected.start(); rejected.next(); rejected.next()
    pending = rejected.pending['id']
    assert rejected.decide('reject', pending)['status'] == 'running'
    assert rejected.current_proposal == BASE
    assert rejected.approved_proposal is None
    assert rejected.decide('approve', pending)['error']


def test_compatible_api_parses_json_and_sends_only_own_profile(monkeypatch):
    calls = []
    class Response:
        def raise_for_status(self):
            pass
        def json(self):
            return {'choices': [{'message': {'content': json.dumps(action('Bob', 'PROPOSE', BASE))}}]}
    def fake_post(url, **kwargs):
        calls.append((url, kwargs))
        return Response()
    monkeypatch.setattr('backend.llm_client.httpx.post', fake_post)
    client = OpenAICompatibleClient(api_key='test-key', base_url='http://example.test/v1', model='test-model')
    result = client.generate('Bob', {'name': 'Bob', 'private': {'reserved_evening_reason': 'date'}}, [], None)
    assert result['actor'] == 'Bob'
    assert calls[0][0] == 'http://example.test/v1/chat/completions'
    assert calls[0][1]['json']['model'] == 'test-model'
    assert 'Alice' not in calls[0][1]['json']['messages'][1]['content']


def test_compatible_api_timeout_and_bad_response_fail_closed(monkeypatch):
    import httpx
    def timeout(*args, **kwargs):
        raise httpx.ReadTimeout('slow')
    monkeypatch.setattr('backend.llm_client.httpx.post', timeout)
    client = OpenAICompatibleClient(api_key='test-key')
    with pytest.raises(LLMError, match='timed out'):
        client.generate('Bob', {'name': 'Bob'}, [], None)
    class BadResponse:
        def raise_for_status(self):
            raise httpx.HTTPStatusError('bad', request=httpx.Request('POST', 'http://x'), response=httpx.Response(503))
    monkeypatch.setattr('backend.llm_client.httpx.post', lambda *args, **kwargs: BadResponse())
    with pytest.raises(LLMError, match='API failed'):
        client.generate('Bob', {'name': 'Bob'}, [], None)


def test_invalid_base_url_reports_configuration_error_without_request(monkeypatch):
    def should_not_call(*args, **kwargs):
        raise AssertionError('request must not be sent')
    monkeypatch.setattr('backend.llm_client.httpx.post', should_not_call)
    client = OpenAICompatibleClient(api_key='test-key', base_url='[https://api.openai.com/v1](https://api.openai.com/v1)')
    with pytest.raises(LLMError, match='BASE_URL must be a plain http'):
        client.generate('Bob', {'name': 'Bob'}, [], None)


def test_http_401_reports_authorization_failure_without_secret(monkeypatch):
    import httpx
    class Unauthorized:
        def raise_for_status(self):
            raise httpx.HTTPStatusError('raw provider text', request=httpx.Request('POST', 'https://example.test/v1/chat/completions'), response=httpx.Response(401))
    monkeypatch.setattr('backend.llm_client.httpx.post', lambda *a, **k: Unauthorized())
    client = OpenAICompatibleClient(api_key='secret-value')
    with pytest.raises(LLMError, match='401') as info:
        client.generate('Bob', {'name': 'Bob'}, [], None)
    assert 'secret-value' not in str(info.value)
    assert 'raw provider text' not in str(info.value)


def test_timeout_setting_applies_to_model_request(monkeypatch):
    seen = {}
    class Response:
        def raise_for_status(self): pass
        def json(self): return {'choices': [{'message': {'content': json.dumps(action('Bob', 'PROPOSE', BASE))}}]}
    def fake_post(*args, **kwargs):
        seen['timeout'] = kwargs['timeout']
        return Response()
    monkeypatch.setenv('AGENT_DIPLOMACY_TIMEOUT_SECONDS', '90')
    monkeypatch.setattr('backend.llm_client.httpx.post', fake_post)
    OpenAICompatibleClient(api_key='test-key').generate('Bob', {'name': 'Bob'}, [], None)
    assert seen['timeout'].read == 90
    assert seen['timeout'].connect == 10


def test_connect_timeout_is_distinct_from_slow_model(monkeypatch):
    import httpx
    monkeypatch.setattr('backend.llm_client.httpx.post', lambda *a, **k: (_ for _ in ()).throw(httpx.ConnectTimeout('connect failed')))
    with pytest.raises(LLMError, match='Could not connect'):
        OpenAICompatibleClient(api_key='test-key').generate('Bob', {'name': 'Bob'}, [], None)
