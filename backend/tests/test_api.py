from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)


def test_public_api_and_exact_approval():
    client.post('/api/session/reset')
    client.post('/api/session/start')
    for _ in range(10):
        state = client.post('/api/session/next').json()
        if state['status'] == 'pending_approval':
            break
    assert state['status'] == 'pending_approval'
    assert 'date' not in str(state).lower()
    assert client.post('/api/approvals/other/decide', json={'choice': 'approve'}).status_code == 409
    assert client.post('/api/approvals/alice-tidal-150/decide', json={'choice': 'approve'}).status_code == 200
    assert client.post('/api/approvals/alice-tidal-150/decide', json={'choice': 'approve'}).status_code == 409
    final = client.post('/api/session/next').json()
    assert final['status'] == 'complete'
    assert final['outcome']['hotel']['name'] == 'The Tidal House'


def test_mode_selection_and_missing_key_safe_failure(monkeypatch):
    monkeypatch.delenv('AGENT_DIPLOMACY_API_KEY', raising=False)
    state = client.post('/api/session/reset', json={'mode': 'live'}).json()
    assert state['mode'] == 'live' and state['status'] == 'idle'
    state = client.post('/api/session/start').json()
    assert state['status'] == 'error'
    assert state['events'] == []
    assert 'AGENT_DIPLOMACY_API_KEY' in state['error']
    state = client.post('/api/session/reset', json={'mode': 'scripted'}).json()
    assert state['status'] == 'idle' and state['mode'] == 'scripted'
