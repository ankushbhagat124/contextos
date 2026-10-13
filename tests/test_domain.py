import pytest
from backend.domain import Problem, seed, propose, review, assemble, snapshot
from backend.store import SQLiteStore


def change(s, body='Retry transient failures up to 2 times.'):
    return propose(s, 'dev-user', 'developer', {'context_id': 'ARC-001', 'base_revision': s['contexts']['ARC-001']['revision'], 'body': body, 'reason': 'Reduce latency', 'sources': ['Task observation']})


def test_restricted_content_never_in_derived_views():
    s = seed()
    p = propose(s, 'security-author', 'security', {'context_id': 'RES-001', 'base_revision': 1, 'body': 'Private changed finding.', 'reason': 'Private reason', 'sources': []})
    view = snapshot(s, 'developer')
    assert 'RES-001' not in str(view)
    assert p['id'] not in str(view)
    assert 'INTERNAL-SEC-42' not in str(assemble(s, 'developer', 'security finding', 8000))
    assert 'RES-001' in str(snapshot(s, 'security'))


def test_propose_does_not_publish_and_review_enforces_owner():
    s = seed(); p = change(s)
    assert s['contexts']['ARC-001']['revision'] == 1
    with pytest.raises(Problem) as e:
        review(s, 'other-dev', 'developer', p['id'], p['hash'], 'approve')
    assert e.value.status == 403
    review(s, 'architect-user', 'architect', p['id'], p['hash'], 'approve')
    assert s['contexts']['ARC-001']['revision'] == 2
    assert len(s['contexts']['ARC-001']['history']) == 2


def test_self_review_hash_and_duplicate_rejected():
    s = seed(); p = change(s)
    for actor, hash_value in [('dev-user', p['hash']), ('reviewer', 'tampered')]:
        with pytest.raises(Problem):
            review(s, actor, 'architect', p['id'], hash_value, 'approve')
    review(s, 'reviewer', 'architect', p['id'], p['hash'], 'approve')
    with pytest.raises(Problem):
        review(s, 'reviewer', 'architect', p['id'], p['hash'], 'approve')


def test_stale_base_does_not_overwrite():
    s = seed(); a = change(s); b = change(s, 'Conflicting update')
    review(s, 'architect-user', 'architect', a['id'], a['hash'], 'approve')
    with pytest.raises(Problem) as e:
        review(s, 'architect-user', 'architect', b['id'], b['hash'], 'approve')
    assert e.value.status == 409
    assert s['contexts']['ARC-001']['body'] == a['body']


def test_budget_and_exact_payload():
    import json
    s = seed()
    m = assemble(s, 'developer', 'payment retry', 4000)
    assert m['estimated_tokens'] <= 4000
    assert {'REQ-001', 'SEC-001'} <= {x['id'] for x in m['sources']}
    assert json.loads(m['context_payload']) == m['sources']
    with pytest.raises(Problem):
        assemble(s, 'developer', 'payment', 10)


def test_transitive_impact_and_immutable_manifest():
    s = seed(); manifest = assemble(s, 'qa', 'acceptance checkout', 6000)
    s['tasks']['task'] = {'manifest': manifest, 'stale': False}
    old = str(manifest)
    p = change(s); review(s, 'reviewer', 'architect', p['id'], p['hash'], 'approve')
    assert s['tasks']['task']['stale']
    assert str(s['tasks']['task']['manifest']) == old


def test_sqlite_persistence_and_workspace_isolation(tmp_path):
    path = tmp_path / 'state.db'; db = SQLiteStore(path)
    p = db.mutate('a', lambda s: change(s))
    assert p['id'] in SQLiteStore(path).read('a')['proposals']
    assert not db.read('b')['proposals']
    with pytest.raises(Problem):
        db.mutate('a', lambda s: review(s, 'x', 'developer', p['id'], p['hash'], 'approve'))
    assert db.read('a')['contexts']['ARC-001']['revision'] == 1


def test_rollback_is_new_reviewed_revision():
    s = seed(); original = s['contexts']['ARC-001']['body']
    p = change(s); review(s, 'arch', 'architect', p['id'], p['hash'], 'approve')
    rollback = change(s, original)
    review(s, 'arch', 'architect', rollback['id'], rollback['hash'], 'approve')
    assert s['contexts']['ARC-001']['revision'] == 3
    assert s['contexts']['ARC-001']['body'] == original
    assert len(s['contexts']['ARC-001']['history']) == 3


def test_simultaneous_publication_has_exactly_one_winner(tmp_path):
    from concurrent.futures import ThreadPoolExecutor
    db = SQLiteStore(tmp_path / 'race.db')
    a = db.mutate('shared', lambda s: change(s, 'First candidate'))
    b = db.mutate('shared', lambda s: change(s, 'Second candidate'))
    def publish(p):
        try:
            db.mutate('shared', lambda s: review(s, 'architect', 'architect', p['id'], p['hash'], 'approve'))
            return 200
        except Problem as e:
            return e.status
    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(publish, [a,b])) == [200,409]
    assert db.read('shared')['contexts']['ARC-001']['revision'] == 2


def test_storage_limit_rolls_back_without_losing_history(tmp_path):
    db = SQLiteStore(tmp_path / 'limit.db')
    before = db.read('limited')
    with pytest.raises(Problem) as e:
        db.mutate('limited', lambda s: s.update(oversized='x' * 800000))
    assert e.value.status == 413
    assert db.read('limited') == before


def test_new_context_publication_preserves_proposal_hash():
    from backend.domain import digest
    s = seed()
    p = propose(s, 'dev', 'developer', {'title':'New topic','domain':'Requirements','body':'New requirement','reason':'Workshop','sources':[]})
    review(s, 'pm', 'pm', p['id'], p['hash'], 'approve')
    published = s['proposals'][p['id']]
    assert digest(published) == p['hash']
    assert published['published_context_id'] in s['contexts']
