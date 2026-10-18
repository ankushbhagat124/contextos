import pytest
from backend import store


def test_unknown_backend_fails_instead_of_falling_back(monkeypatch):
    monkeypatch.setenv('STORE_BACKEND','firestrore')
    with pytest.raises(RuntimeError,match='STORE_BACKEND'):
        store.make_store()


def test_real_accounts_start_empty_but_demo_keeps_synthetic_seed(tmp_path,monkeypatch):
    monkeypatch.delenv('K_SERVICE',raising=False)
    monkeypatch.setenv('STORE_BACKEND','sqlite')
    monkeypatch.setenv('DATABASE_PATH',str(tmp_path/'state.db'))
    monkeypatch.setenv('AUTH_MODE','firebase')
    real=store.make_store().read('real-team')
    assert not real['contexts'] and not real['proposals'] and not real['tasks']
    assert real['project']['name']=='Your workspace'
    monkeypatch.setenv('AUTH_MODE','demo')
    demo=store.make_store().read('synthetic-demo')
    assert 'REQ-001' in demo['contexts']
    # Initializer changes never reset existing state.
    assert not store.make_store().read('real-team')['contexts']


def test_cloud_run_refuses_ephemeral_sqlite(monkeypatch):
    monkeypatch.setenv('K_SERVICE','contextos')
    monkeypatch.setenv('STORE_BACKEND','sqlite')
    with pytest.raises(RuntimeError,match='Firestore|firestore'):
        store.make_store()


def test_firestore_requires_explicit_project(monkeypatch):
    monkeypatch.setenv('STORE_BACKEND','firestore')
    monkeypatch.delenv('GOOGLE_CLOUD_PROJECT',raising=False)
    with pytest.raises(RuntimeError,match='GOOGLE_CLOUD_PROJECT'):
        store.make_store()


def test_firestore_factory_selects_real_initializer(monkeypatch):
    monkeypatch.setenv('AUTH_MODE','firebase')
    monkeypatch.setenv('STORE_BACKEND','firestore')
    monkeypatch.setenv('GOOGLE_CLOUD_PROJECT','test-project')
    captured=[]
    class FakeFirestore:
        def __init__(self,initializer): captured.append(initializer())
    monkeypatch.setattr(store,'FirestoreStore',FakeFirestore)
    store.make_store()
    assert captured[0]['contexts']=={}
