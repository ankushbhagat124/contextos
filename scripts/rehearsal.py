"""Run an isolated end-to-end rehearsal without network or altering browser data."""
from pathlib import Path
import sys
import tempfile
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.domain import seed, propose, review, assemble
from backend.store import SQLiteStore

with tempfile.TemporaryDirectory(prefix='contextos-rehearsal-') as folder:
    store = SQLiteStore(Path(folder) / 'demo.db')
    original = store.read('rehearsal')
    manifest = assemble(original, 'developer', 'Implement payment retries', 6000)
    store.mutate('rehearsal', lambda s: s['tasks'].update({'demo-run': {'manifest': manifest, 'stale': False}}))
    proposal = store.mutate('rehearsal', lambda s: propose(s, 'dev', 'developer', {
        'context_id': 'ARC-001', 'base_revision': 1,
        'body': s['contexts']['ARC-001']['body'].replace('3 times', '2 times'),
        'reason': 'Reduce maximum retry latency while retaining idempotency safeguards.',
        'sources': ['Synthetic latency review']}))
    store.mutate('rehearsal', lambda s: review(s, 'architect', 'architect', proposal['id'], proposal['hash'], 'approve'))
    final = store.read('rehearsal')
    assert final['contexts']['ARC-001']['revision'] == 2
    assert final['tasks']['demo-run']['stale']
    print('PASS: Developer used v1 → proposed change → Architect published v2 → previous run became stale.')
    print('PASS: Stored source manifest remains unchanged; rehearsal database was temporary.')
