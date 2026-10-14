from copy import deepcopy
import os
from pathlib import Path
import re
import secrets
from typing import Literal
from fastapi import FastAPI, Request, Response
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, ConfigDict
from backend import domain as d
from backend.ai import AI
from backend.store import make_store

ROOT = Path(__file__).resolve().parent.parent


class Input(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)


class ProposalInput(Input):
    context_id: str | None = None
    base_revision: int = Field(default=0, ge=0)
    title: str = Field(default='New requirement', min_length=1, max_length=120)
    domain: Literal['Requirements', 'Architecture', 'Implementation', 'Quality', 'Security'] = 'Requirements'
    body: str = Field(min_length=1, max_length=10000)
    reason: str = Field(min_length=1, max_length=1500)
    sources: list[str] = Field(default_factory=list, max_length=10)


class ReviewInput(Input):
    hash: str = Field(min_length=64, max_length=64)
    decision: Literal['approve', 'reject']


class TaskInput(Input):
    query: str = Field(min_length=3, max_length=2000)
    budget: int = Field(default=6000, ge=200, le=16000)


class IngestInput(Input):
    notes: str = Field(min_length=10, max_length=8000)
    source: str = Field(min_length=1, max_length=200)


class RoleInput(Input):
    role: Literal['pm', 'architect', 'developer', 'qa', 'security']


def create_app(store=None, ai=None):
    app = FastAPI(title='ContextOS', docs_url='/api/docs', redoc_url=None)
    app.state.store = store or make_store()
    app.state.ai = ai or AI()
    auth_mode = os.getenv('AUTH_MODE', 'demo')
    if auth_mode not in ('demo', 'firebase'):
        raise RuntimeError('AUTH_MODE must be demo or firebase.')
    if auth_mode == 'firebase':
        import firebase_admin
        if not firebase_admin._apps:
            firebase_admin.initialize_app()

    @app.exception_handler(d.Problem)
    async def problem_handler(request, exc):
        return JSONResponse({'detail': exc.message}, status_code=exc.status)

    @app.middleware('http')
    async def boundary(request: Request, call_next):
        if request.method in ('POST', 'PUT', 'DELETE', 'PATCH'):
            if request.headers.get('x-contextos-client') != 'workspace':
                return JSONResponse({'detail': 'Missing same-origin client header.'}, status_code=403)
            origin = request.headers.get('origin')
            if origin and origin.rstrip('/') != str(request.base_url).rstrip('/'):
                return JSONResponse({'detail': 'Cross-origin writes are not allowed.'}, status_code=403)
            try:
                length = int(request.headers.get('content-length', '0'))
            except ValueError:
                return JSONResponse({'detail': 'Invalid request size.'}, status_code=400)
            if length > 40000:
                return JSONResponse({'detail': 'Request too large.'}, status_code=413)
            # Enforce the same cap when Content-Length is absent or inaccurate.
            body = await request.body()
            if len(body) > 40000:
                return JSONResponse({'detail': 'Request too large.'}, status_code=413)
        response = await call_next(request)
        if getattr(request.state, 'new_session', None):
            response.set_cookie('contextos_session', request.state.new_session, httponly=True, samesite='strict', secure=bool(os.getenv('K_SERVICE')), max_age=604800)
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'same-origin'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com data:; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
        if request.url.path.startswith('/api/'):
            response.headers['Cache-Control'] = 'no-store'
        return response

    def identity(request, response):
        if auth_mode == 'firebase':
            from firebase_admin import auth
            token = request.headers.get('authorization', '').removeprefix('Bearer ')
            try:
                claims = auth.verify_id_token(token, check_revoked=True)
                role, workspace = claims['contextos_role'], claims['contextos_workspace']
                if role not in d.ROLES or not isinstance(workspace, str) or not re.fullmatch(r'[a-zA-Z0-9_-]{1,80}', workspace):
                    raise ValueError()
                return workspace, claims['uid'], role
            except Exception as exc:
                raise d.Problem('Sign in with a provisioned Firebase workspace account.', 401) from exc
        workspace = request.cookies.get('contextos_session', '')
        if not re.fullmatch(r'[a-f0-9]{64}', workspace):
            workspace = secrets.token_hex(32)
            request.state.new_session = workspace
        state = app.state.store.read(workspace)
        role = state['role']
        return workspace, f'demo-{role}', role

    def reserve(workspace, role, sources, kind):
        run_id = d.uid('CALL')
        def mutation(s):
            # A bounded public-demo allowance also counts failed calls.
            if len(s['usage']) >= 50:
                raise d.Problem('This workspace has reached its 50-call demo allowance. Export and start a new sandbox.', 429)
            from datetime import datetime, timezone, timedelta
            cutoff = datetime.now(timezone.utc) - timedelta(seconds=60)
            recent = [u for u in s['usage'] if datetime.fromisoformat(u['at']) > cutoff]
            if len(recent) >= 6:
                raise d.Problem('Please wait a minute before making more model requests.', 429)
            s['usage'].append({'id': run_id, 'at': d.now(), 'kind': kind, 'status': 'pending', 'source_ids': sources, 'private_role': role if kind == 'extraction' else None})
        app.state.store.mutate(workspace, mutation)
        return run_id

    def finish_usage(state, call_id, usage=None, failed=False):
        entry = next(u for u in state['usage'] if u['id'] == call_id)
        entry.update(usage or {})
        entry['status'] = 'completed' if usage is not None and not failed else 'failed'

    @app.get('/api/demo/scenarios')
    def demo_scenarios(request: Request, response: Response):
        identity(request, response)
        if auth_mode != 'demo':
            raise d.Problem('Synthetic scenarios are available only in demo mode.', 403)
        from backend.demo import SCENARIOS
        return {'scenarios': SCENARIOS}

    @app.post('/api/demo/scenarios/{scenario_id}')
    def demo_scenario(scenario_id: str, request: Request, response: Response):
        identity(request, response)
        if auth_mode != 'demo':
            raise d.Problem('Synthetic scenarios are available only in demo mode.', 403)
        from backend.demo import run_scenario
        return run_scenario(scenario_id)

    @app.get('/api/health')
    def health():
        return {'status': 'ok', 'ai_mode': app.state.ai.mode, 'auth_mode': auth_mode}

    @app.get('/api/workspace')
    def workspace(request: Request, response: Response):
        wid, actor, role = identity(request, response)
        result = d.snapshot(app.state.store.read(wid), role)
        result.update(actor=actor, ai_mode=app.state.ai.mode, auth_mode=auth_mode)
        return result

    @app.post('/api/persona')
    def persona(data: RoleInput, request: Request, response: Response):
        wid, _, _ = identity(request, response)
        if auth_mode != 'demo':
            raise d.Problem('Persona switching is only available in the synthetic demo.', 403)
        app.state.store.mutate(wid, lambda s: s.update(role=data.role))
        return {'role': data.role}

    @app.post('/api/proposals')
    def proposals(data: ProposalInput, request: Request, response: Response):
        wid, actor, role = identity(request, response)
        if any(len(source) > 300 for source in data.sources):
            raise d.Problem('Source labels must be at most 300 characters.')
        return app.state.store.mutate(wid, lambda s: d.propose(s, actor, role, data.model_dump()))

    @app.post('/api/proposals/{pid}/review')
    def review(pid: str, data: ReviewInput, request: Request, response: Response):
        wid, actor, role = identity(request, response)
        return app.state.store.mutate(wid, lambda s: d.review(s, actor, role, pid, data.hash, data.decision))

    @app.post('/api/assemble')
    def assemble(data: TaskInput, request: Request, response: Response):
        wid, _, role = identity(request, response)
        return d.assemble(app.state.store.read(wid), role, data.query, data.budget)

    @app.post('/api/tasks')
    def task(data: TaskInput, request: Request, response: Response):
        wid, actor, role = identity(request, response)
        manifest = d.assemble(app.state.store.read(wid), role, data.query, data.budget)
        call_id = reserve(wid, role, [x['id'] for x in manifest['sources']], 'task')
        usage = None
        try:
            output, usage = app.state.ai.task(role, data.query, manifest)
            run = {'id': d.uid('RUN'), 'query': data.query, 'role': role, 'actor': actor, 'output': output, 'manifest': manifest, 'usage': usage, 'created_at': d.now(), 'stale': False}
            def save(s):
                run['stale'] = any(s['contexts'][x['id']]['revision'] != x['revision'] for x in manifest['sources'])
                s['tasks'][run['id']] = deepcopy(run)
                finish_usage(s, call_id, usage)
            app.state.store.mutate(wid, save)
            return run
        except Exception as exc:
            app.state.store.mutate(wid, lambda s: finish_usage(s, call_id, usage or getattr(exc, 'usage', None), failed=True))
            raise

    @app.post('/api/ingest')
    def ingest(data: IngestInput, request: Request, response: Response):
        wid, actor, role = identity(request, response)
        call_id = reserve(wid, role, [], 'extraction')
        usage = None
        try:
            candidate, usage = app.state.ai.extract(data.notes)
            # Domain validation remains independent of the model's structured output.
            validated = ProposalInput(**candidate, sources=[data.source])
            def save(s):
                result = d.propose(s, actor, role, validated.model_dump())
                finish_usage(s, call_id, usage)
                return result
            return app.state.store.mutate(wid, save)
        except Exception as exc:
            app.state.store.mutate(wid, lambda s: finish_usage(s, call_id, usage or getattr(exc, 'usage', None), failed=True))
            raise

    @app.get('/api/export')
    def export(request: Request, response: Response):
        wid, _, role = identity(request, response)
        return d.snapshot(app.state.store.read(wid), role)

    @app.get('/favicon.ico', include_in_schema=False)
    def favicon():
        return FileResponse(ROOT / 'web' / 'favicon.svg', media_type='image/svg+xml')

    @app.get('/')
    def index():
        return FileResponse(ROOT / 'web' / 'index.html')

    app.mount('/assets', StaticFiles(directory=ROOT / 'web'), name='assets')
    return app


app = create_app()
