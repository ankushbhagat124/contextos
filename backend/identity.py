"""Firebase login exchange and verified browser sessions; demo identity stays separate."""
from datetime import timedelta
import os
import re
import secrets
import time
from fastapi import Request, Response
from pydantic import BaseModel, ConfigDict, Field
from backend import domain as d

SESSION_COOKIE = 'contextos_auth'
CSRF_COOKIE = 'contextos_csrf'
SESSION_SECONDS = 8 * 60 * 60


class SessionInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    id_token: str = Field(min_length=8, max_length=16000, repr=False)


def member_identity(claims):
    """Claims must already have been verified by Firebase Admin."""
    role, workspace, actor = claims.get('contextos_role'), claims.get('contextos_workspace'), claims.get('uid')
    if (role not in d.ROLES or not isinstance(workspace, str)
            or not re.fullmatch(r'[a-zA-Z0-9_-]{1,80}', workspace)
            or not isinstance(actor, str) or not 1 <= len(actor) <= 128):
        raise d.Problem('Your account needs a workspace and role assigned by an administrator.', 403)
    return workspace, actor, role


def verified_identity(request):
    from firebase_admin import auth
    authorization = request.headers.get('authorization')
    try:
        if authorization is not None:
            if not authorization.startswith('Bearer '):
                raise ValueError('Invalid authorization scheme')
            claims = auth.verify_id_token(authorization[7:], check_revoked=True)
        else:
            cookie = request.cookies.get(SESSION_COOKIE)
            if not cookie:
                raise ValueError('No session')
            claims = auth.verify_session_cookie(cookie, check_revoked=True)
    except Exception as exc:
        raise d.Problem('Sign in to continue. Your session may have expired.', 401) from exc
    return member_identity(claims)


def secure_cookie(request):
    return request.url.scheme == 'https' or bool(os.getenv('K_SERVICE'))


def require_csrf(request):
    cookie = request.cookies.get(CSRF_COOKIE, '')
    header = request.headers.get('x-contextos-csrf', '')
    if not cookie or not header or not secrets.compare_digest(cookie, header):
        raise d.Problem('Reload the sign-in page and try again.', 403)


def register_auth_routes(app, auth_mode):
    @app.get('/api/auth/config')
    def config(request: Request, response: Response):
        # This key identifies the Firebase web app. It grants no backend role.
        api_key = os.getenv('FIREBASE_WEB_API_KEY') if auth_mode == 'firebase' else None
        nonce = request.cookies.get(CSRF_COOKIE)
        if not nonce or not re.fullmatch(r'[a-f0-9]{64}', nonce):
            nonce = secrets.token_hex(32)
        response.set_cookie(CSRF_COOKIE, nonce, httponly=True, secure=secure_cookie(request),
                            samesite='strict', max_age=SESSION_SECONDS)
        return {'auth_mode': auth_mode, 'login_ready': bool(api_key),
                'firebase_api_key': api_key, 'csrf_token': nonce,
                'session_seconds': SESSION_SECONDS}

    @app.post('/api/auth/session')
    def login(data: SessionInput, request: Request, response: Response):
        if auth_mode != 'firebase':
            raise d.Problem('Use the synthetic workspace in demo mode.', 403)
        require_csrf(request)
        from firebase_admin import auth
        try:
            claims = auth.verify_id_token(data.id_token, check_revoked=True)
        except Exception as exc:
            raise d.Problem('Sign in again to start a session.', 401) from exc
        wid, actor, role = member_identity(claims)
        authenticated_at = claims.get('auth_time')
        if not isinstance(authenticated_at, (int, float)) or not 0 <= time.time() - authenticated_at <= 300:
            raise d.Problem('Please sign in again. A recent sign-in is required.', 401)
        try:
            cookie = auth.create_session_cookie(data.id_token, expires_in=timedelta(seconds=SESSION_SECONDS))
        except Exception as exc:
            raise d.Problem('Sign-in is temporarily unavailable. Please retry.', 503) from exc
        # Record a successful exchange before returning a usable cookie.
        app.state.store.mutate(wid, lambda s: d.audit(s, actor, 'Signed in', None,
                                                     'Browser session started.', role=role, private_role=role))
        response.set_cookie(SESSION_COOKIE, cookie, httponly=True, secure=secure_cookie(request),
                            samesite='strict', max_age=SESSION_SECONDS)
        return {'actor': actor, 'role': role, 'expires_in': SESSION_SECONDS}

    @app.post('/api/auth/logout')
    def logout(request: Request, response: Response):
        require_csrf(request)
        if auth_mode == 'firebase':
            try:
                wid, actor, role = verified_identity(request)
            except d.Problem:
                pass  # Expired/revoked sessions can still clear their local cookie.
            else:
                try:
                    app.state.store.mutate(wid, lambda s: d.audit(s, actor, 'Signed out', None,
                                                                 'This browser session ended.', role=role, private_role=role))
                except Exception:
                    import logging
                    logging.getLogger(__name__).warning('Sign-out audit unavailable; clearing browser session.')
        response.delete_cookie(SESSION_COOKIE, httponly=True, secure=secure_cookie(request), samesite='strict')
        response.delete_cookie(CSRF_COOKIE, httponly=True, secure=secure_cookie(request), samesite='strict')
        return {'signed_out': True}
