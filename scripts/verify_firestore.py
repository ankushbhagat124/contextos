"""Explicit live/emulator verification. Creates and retains one synthetic workspace."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import os
import sys
from pathlib import Path
from uuid import uuid4
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend import domain as d
from backend.store import FirestoreStore


def verify(project):
    os.environ['GOOGLE_CLOUD_PROJECT'] = project
    workspace = 'verification-' + uuid4().hex
    first, second = FirestoreStore(initializer=d.seed), FirestoreStore(initializer=d.seed)
    first.read(workspace)
    print(f'Synthetic verification workspace (retained): {workspace}')
    def setup(s):
        manifest = d.assemble(s, 'developer', 'payment retry architecture', 6000)
        s['tasks']['verification-run'] = {'manifest':manifest, 'stale':False}
        return [d.propose(s, 'verification-developer', 'developer', {
            'context_id':'ARC-001','base_revision':1,'body':f'Retry {count} times using the original idempotency key.',
            'reason':'Synthetic storage verification.','sources':['Verification fixture']}) for count in (1,2)]
    proposals = first.mutate(workspace, setup)
    def approve(p):
        try:
            first.mutate(workspace, lambda s: d.review(s,'verification-architect','architect',p['id'],p['hash'],'approve'))
            return 'published'
        except d.Problem as exc:
            if exc.status != 409:
                raise
            return 'conflict'
    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(approve, proposals))
    assert sorted(outcomes) == ['conflict','published'], outcomes
    state = second.read(workspace)
    assert state['contexts']['ARC-001']['revision'] == 2
    assert state['tasks']['verification-run']['stale']
    assert next(s for s in state['tasks']['verification-run']['manifest']['sources'] if s['id']=='ARC-001')['revision']==1
    assert FirestoreStore().read(workspace)==state
    print('PASS: concurrent publication has one winner; second client/recreated client sees v2; old snapshot remains v1 and stale.')
    print('This verifies shared database clients, not deployed Cloud Run instance behavior or backup restoration.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project',required=True,help='Explicit Firebase/Google Cloud project ID; uses existing ADC or emulator configuration.')
    verify(parser.parse_args().project)
