import pytest
from backend.demo import SCENARIOS, run_scenario
from backend.domain import Problem
from backend.app import create_app
from backend.ai import AI
from backend.store import SQLiteStore
from fastapi.testclient import TestClient


@pytest.mark.parametrize('scenario', SCENARIOS, ids=lambda s:s['id'])
def test_demonstrated_invariants(scenario):
    result = run_scenario(scenario['id'])
    assert result['passed'], result['steps']
    assert len(result['steps']) >= 2
    assert result['mode'] == 'isolated-offline-rehearsal'


def test_scenarios_do_not_mutate_workspace_or_spend_model_calls(tmp_path, monkeypatch):
    monkeypatch.setenv('AUTH_MODE','demo')
    store = SQLiteStore(tmp_path / 'demo.db')
    client = TestClient(create_app(store, AI(mode='offline')),headers={'x-contextos-client':'workspace'})
    before = client.get('/api/workspace').json()
    for scenario in client.get('/api/demo/scenarios').json()['scenarios']:
        result = client.post('/api/demo/scenarios/' + scenario['id'], json={})
        assert result.status_code == 200
        assert result.json()['passed']
    assert client.get('/api/workspace').json() == before
    assert client.post('/api/demo/scenarios/unknown',json={}).status_code == 404


def test_unknown_scenario_does_not_succeed():
    with pytest.raises(Problem) as e:
        run_scenario('imaginary')
    assert e.value.status == 404
