import pytest
from fastapi.testclient import TestClient
from backend.app import create_app
from backend.ai import AI
from backend.store import SQLiteStore


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv('AUTH_MODE', 'demo'); monkeypatch.setenv('AI_MODE', 'offline')
    return TestClient(create_app(SQLiteStore(tmp_path / 'test.db'), AI()), headers={'x-contextos-client': 'workspace'})


def test_full_cross_role_workflow(client):
    state = client.get('/api/workspace').json()
    assert state['role'] == 'developer'
    run = client.post('/api/tasks', json={'query': 'Implement payment retries', 'budget': 6000}).json()
    assert run['usage']['provider'] == 'offline'
    assert run['manifest']['sources']
    p = client.post('/api/proposals', json={'context_id': 'ARC-001', 'base_revision': 1, 'body': 'Retry at most two times, using the original idempotency key.', 'reason': 'Limit latency'}).json()
    assert client.post(f"/api/proposals/{p['id']}/review", json={'hash': p['hash'], 'decision': 'approve'}).status_code == 403
    client.post('/api/persona', json={'role': 'architect'})
    assert client.post(f"/api/proposals/{p['id']}/review", json={'hash': p['hash'], 'decision': 'approve'}).status_code == 200
    state = client.get('/api/workspace').json()
    assert state['tasks'][0]['stale']
    rerun = client.post('/api/tasks', json={'query': 'Implement payment retries', 'budget': 6000}).json()
    assert not rerun['stale']
    assert next(x for x in rerun['manifest']['sources'] if x['id'] == 'ARC-001')['revision'] == 2


def test_sessions_isolated_and_requests_validated(client):
    client.get('/api/workspace')
    client.post('/api/persona', json={'role': 'security'})
    assert 'RES-001' in client.get('/api/workspace').text
    client.cookies.clear()
    assert 'RES-001' not in client.get('/api/workspace').text
    assert client.post('/api/tasks', json={'query': '', 'role': 'security'}).status_code == 422
    assert client.post('/api/persona', json={'role': 'admin'}).status_code == 422
    assert client.post('/api/persona', json={'role': 'pm'}, headers={'origin': 'https://evil.example'}).status_code == 403


def test_ingest_candidate_requires_independent_review(client):
    p = client.post('/api/ingest', json={'notes': 'Customers need clear error messages after a declined card.', 'source': 'Workshop'}).json()
    assert p['status'] == 'pending'
    # Seven seeded items exist; Developer cannot see restricted RES-001.
    assert len(client.get('/api/workspace').json()['contexts']) == 6
    client.post('/api/persona', json={'role': 'pm'})
    assert client.post(f"/api/proposals/{p['id']}/review", json={'hash': p['hash'], 'decision': 'approve'}).status_code == 200
    assert len(client.get('/api/workspace').json()['contexts']) == 7


def test_restricted_task_output_hidden_after_switch(client):
    client.post('/api/persona', json={'role': 'security'})
    response = client.post('/api/tasks', json={'query': 'Internal security finding diagnostic endpoint', 'budget': 10000})
    assert 'INTERNAL-SEC-42' in response.text
    client.post('/api/persona', json={'role': 'developer'})
    state = client.get('/api/workspace')
    assert 'INTERNAL-SEC-42' not in state.text
    assert not state.json()['tasks']


def test_budget_overflow_and_model_error_visible(client, monkeypatch):
    assert client.post('/api/tasks', json={'query': 'payment', 'budget': 200}).status_code == 422
    from backend.domain import Problem
    def fail(*args):
        raise Problem('Model unavailable', 502)
    monkeypatch.setattr(client.app.state.ai, 'task', fail)
    result = client.post('/api/tasks', json={'query': 'payment', 'budget': 6000})
    assert result.status_code == 502
    assert client.get('/api/workspace').json()['usage'][0]['status'] == 'failed'


def test_rate_limit(client):
    for _ in range(6):
        assert client.post('/api/tasks', json={'query': 'payment', 'budget': 6000}).status_code == 200
    assert client.post('/api/tasks', json={'query': 'payment', 'budget': 6000}).status_code == 429
