import time
import pytest
from fastapi.testclient import TestClient
from backend.app import create_app
from backend.ai import AI
from backend.store import SQLiteStore


@pytest.fixture
def firebase_client(tmp_path, monkeypatch):
    import firebase_admin
    from firebase_admin import auth
    monkeypatch.setenv('AUTH_MODE', 'firebase')
    monkeypatch.setenv('FIREBASE_WEB_API_KEY', 'public-test-key')
    monkeypatch.setenv('GEMINI_API_KEY', 'must-not-be-exposed')
    monkeypatch.setattr(firebase_admin, '_apps', {'test': object()})
    member = {'uid':'alice', 'contextos_role':'qa', 'contextos_workspace':'team-a', 'auth_time':int(time.time())}
    def verify(token, check_revoked):
        assert check_revoked is True
        if token == 'expired-token':
            raise ValueError('Revoked token')
        claims = dict(member)
        if token == 'unprovisioned': claims.pop('contextos_role')
        if token == 'old-login': claims['auth_time'] -= 600
        return claims
    monkeypatch.setattr(auth, 'verify_id_token', verify)
    monkeypatch.setattr(auth, 'verify_session_cookie', verify)
    monkeypatch.setattr(auth, 'create_session_cookie', lambda token, expires_in: 'signed-session')
    client = TestClient(create_app(SQLiteStore(tmp_path/'auth.db'), AI(mode='offline')),
                        headers={'x-contextos-client':'workspace'})
    return client


def csrf(client):
    config = client.get('/api/auth/config').json()
    client.headers['x-contextos-csrf'] = config['csrf_token']
    return config


def test_session_sign_in_refresh_identity_and_logout(firebase_client):
    c = firebase_client
    config = csrf(c)
    assert config['auth_mode']=='firebase' and config['login_ready']
    assert config['firebase_api_key']=='public-test-key'
    assert 'must-not-be-exposed' not in str(config)
    assert c.get('/api/workspace').status_code==401
    response = c.post('/api/auth/session',json={'id_token':'recent-valid'})
    assert response.status_code==200
    cookie = response.headers['set-cookie']
    assert 'HttpOnly' in cookie and 'SameSite=strict' in cookie and 'Max-Age=28800' in cookie
    state = c.get('/api/workspace').json()
    assert state['actor']=='alice' and state['role']=='qa'
    assert c.post('/api/persona',json={'role':'security'}).status_code==403
    assert c.post('/api/auth/logout',json={}).status_code==200
    assert c.get('/api/workspace').status_code==401
    csrf(c)
    assert c.post('/api/auth/logout',json={}).status_code==200


@pytest.mark.parametrize('token,status',[('expired-token',401),('unprovisioned',403),('old-login',401)])
def test_rejects_bad_sign_in_without_issuing_session(firebase_client,token,status):
    c=firebase_client;csrf(c)
    response=c.post('/api/auth/session',json={'id_token':token})
    assert response.status_code==status
    assert 'contextos_auth' not in c.cookies


def test_csrf_origin_and_claim_injection_are_rejected(firebase_client):
    c=firebase_client
    assert c.post('/api/auth/session',json={'id_token':'recent-valid'}).status_code==403
    csrf(c)
    assert c.post('/api/auth/session',json={'id_token':'recent-valid'},headers={'origin':'https://attacker.example'}).status_code==403
    assert c.post('/api/auth/session',json={'id_token':'recent-valid','role':'security'}).status_code==422
    c.headers['x-contextos-csrf']='wrong'
    assert c.post('/api/auth/session',json={'id_token':'recent-valid'}).status_code==403


def test_revoked_cookie_and_explicit_invalid_bearer_fail_closed(firebase_client):
    c=firebase_client;csrf(c)
    c.post('/api/auth/session',json={'id_token':'recent-valid'})
    c.headers['Authorization']='Bearer expired-token'
    assert c.get('/api/workspace').status_code==401
    c.headers.pop('Authorization')
    c.cookies.set('contextos_auth','expired-token')
    assert c.get('/api/workspace').status_code==401


def test_https_session_cookie_is_secure(firebase_client):
    c=firebase_client
    c.base_url='https://testserver'
    csrf(c)
    response=c.post('/api/auth/session',json={'id_token':'recent-valid'})
    assert '; Secure' in response.headers['set-cookie']


def test_demo_never_exposes_firebase_login(tmp_path,monkeypatch):
    monkeypatch.setenv('AUTH_MODE','demo')
    c=TestClient(create_app(SQLiteStore(tmp_path/'demo.db'),AI(mode='offline')),headers={'x-contextos-client':'workspace'})
    config=csrf(c)
    assert config['auth_mode']=='demo' and not config['login_ready']
    assert config['firebase_api_key'] is None
    assert c.post('/api/auth/session',json={'id_token':'recent-valid'}).status_code==403
