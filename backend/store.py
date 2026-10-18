"""Bounded atomic workspace persistence for local and Cloud Run deployments."""
import json
import os
from pathlib import Path
import sqlite3
from backend.domain import Problem, seed, empty_workspace

MAX_BYTES = 750_000


def encode(state):
    raw = json.dumps(state, ensure_ascii=False)
    if len(raw.encode()) > MAX_BYTES:
        raise Problem('This demo workspace has reached its storage limit. Export it and start a new sandbox.', 413)
    return raw


class SQLiteStore:
    def __init__(self, path, initializer=seed):
        self.initializer = initializer
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.path = str(path)
        with self.connect() as db:
            db.execute('CREATE TABLE IF NOT EXISTS workspaces (id TEXT PRIMARY KEY, data TEXT NOT NULL)')

    def connect(self):
        return sqlite3.connect(self.path, timeout=15)

    def mutate(self, workspace, fn):
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row = db.execute('SELECT data FROM workspaces WHERE id=?', (workspace,)).fetchone()
            state = json.loads(row[0]) if row else self.initializer()
            result = fn(state)
            db.execute('INSERT INTO workspaces VALUES (?,?) ON CONFLICT(id) DO UPDATE SET data=excluded.data', (workspace, encode(state)))
            return result

    def read(self, workspace):
        return self.mutate(workspace, lambda state: state)


class FirestoreStore:
    def __init__(self, initializer=seed):
        self.initializer = initializer
        project = os.getenv('GOOGLE_CLOUD_PROJECT')
        if not project:
            raise RuntimeError('GOOGLE_CLOUD_PROJECT is required for Firestore.')
        from google.cloud import firestore
        self.fs = firestore
        self.client = firestore.Client(project=project)

    def mutate(self, workspace, fn):
        ref = self.client.collection('contextos_workspaces').document(workspace)
        @self.fs.transactional
        def transaction(tx):
            snap = ref.get(transaction=tx)
            state = json.loads(snap.get('payload')) if snap.exists else self.initializer()
            result = fn(state)
            tx.set(ref, {'payload': encode(state)})
            return result
        return transaction(self.client.transaction())

    def read(self, workspace):
        ref = self.client.collection('contextos_workspaces').document(workspace)
        snap = ref.get()
        return json.loads(snap.get('payload')) if snap.exists else self.mutate(workspace, lambda s: s)


def make_store():
    backend = os.getenv('STORE_BACKEND', 'sqlite')
    if backend not in ('sqlite', 'firestore'):
        raise RuntimeError('STORE_BACKEND must be sqlite or firestore.')
    initializer = empty_workspace if os.getenv('AUTH_MODE', 'demo') == 'firebase' else seed
    if backend == 'firestore':
        return FirestoreStore(initializer=initializer)
    if os.getenv('K_SERVICE'):
        raise RuntimeError('Cloud Run requires STORE_BACKEND=firestore; ephemeral SQLite is not supported.')
    return SQLiteStore(os.getenv('DATABASE_PATH', '.data/contextos.db'), initializer=initializer)
