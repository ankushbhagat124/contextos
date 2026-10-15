"""Repeatable, isolated demonstrations using the same domain rules as the workspace."""
from copy import deepcopy
from backend import domain as d
from backend.ai import AI

SCENARIOS = [
    {'id':'handoff','title':'One decision, every role','category':'Collaboration','roles':['pm','architect','developer','qa'],'summary':'Follow accepted product intent into architecture, implementation and test planning.','query':'Plan safe payment retries without duplicate charges','role':'developer','view':'tasks'},
    {'id':'ingestion','title':'Notes become reviewed knowledge','category':'Knowledge','roles':['architect','pm'],'summary':'Preserve a stakeholder note as a candidate, then publish through independent product review.','query':'Define acceptance criteria for declined-card messages','role':'architect','view':'knowledge'},
    {'id':'manual','title':'Write a topic directly','category':'Knowledge','roles':['developer','architect'],'summary':'Create a named architecture topic without a model call, keeping the same review gate.','query':'Design a payment timeout policy','role':'developer','view':'knowledge'},
    {'id':'review','title':'Agents propose. Owners decide.','category':'Governance','roles':['developer','architect'],'summary':'Try an unauthorized approval, then publish the exact proposal as its designated owner.','query':'Review the retry architecture','role':'developer','view':'knowledge'},
    {'id':'impact','title':'A changed decision flags the work','category':'Change awareness','roles':['developer','architect','qa'],'summary':'Publish a new retry limit and inspect the old stale snapshot alongside a fresh run.','query':'Implement payment retry architecture','role':'developer','view':'tasks'},
    {'id':'restricted','title':'Keep restricted context restricted','category':'Security','roles':['security','developer'],'summary':'Compare authorized sources and confirm that restricted outputs and activity are also filtered.','query':'Review internal security findings','role':'security','view':'knowledge'},
    {'id':'conflict','title':'Two proposals, one accepted base','category':'Governance','roles':['developer','architect'],'summary':'Publish one competing change and watch a stale-base proposal fail without an overwrite.','query':'Review concurrent retry design proposals','role':'developer','view':'knowledge'},
    {'id':'rollback','title':'Restore content, preserve history','category':'Change awareness','roles':['developer','architect'],'summary':'Restore an earlier architecture body through a new reviewed revision, preserving v1 and v2.','query':'Review architecture revision history','role':'developer','view':'knowledge'},
    {'id':'budget','title':'Small context, mandatory guardrails','category':'Retrieval','roles':['developer','security'],'summary':'Assemble a bounded package, then prove a too-small budget fails rather than dropping required rules.','query':'idempotency','role':'developer','view':'tasks'},
    {'id':'rejection','title':'A rejected change stays a proposal','category':'Governance','roles':['developer','architect'],'summary':'Reject an unsafe design suggestion and confirm that accepted knowledge is untouched.','query':'Review payment safety constraints','role':'architect','view':'reviews'},
    {'id':'audit','title':'Every change has a receipt','category':'Traceability','roles':['pm','architect','developer','qa','security'],'summary':'Inspect an exact proposal hash, attributed publication, preserved history and source revision manifest.','query':'Inspect accepted payment architecture','role':'architect','view':'insights'},
    {'id':'usage','title':'Measurements without invented savings','category':'Measurement','roles':['pm','developer'],'summary':'Compare full and selected context estimates and show zero provider usage for an offline rehearsal.','query':'idempotency','role':'developer','view':'insights'},
]


def run_scenario(scenario_id):
    scenario = next((x for x in SCENARIOS if x['id'] == scenario_id), None)
    if scenario is None:
        raise d.Problem('Demo scenario not found.', 404)
    state = d.seed()  # Never read or mutate the browser's persisted workspace.
    steps = []
    evidence = {}
    offline = AI(mode='offline')

    step_roles = {
        'handoff': ['pm', 'architect', 'developer', 'qa'],
        'ingestion': ['architect', 'architect', 'pm'],
        'manual': ['developer', 'architect'],
        'review': ['developer', 'developer', 'architect', 'architect'],
        'impact': ['qa', 'architect', 'qa'],
        'restricted': ['security', 'developer', 'developer', 'developer'],
        'conflict': ['developer', 'architect', 'architect'],
        'rollback': ['architect', 'architect', 'architect'],
        'budget': ['developer', 'developer', 'developer'],
        'rejection': ['architect', 'architect', 'architect'],
        'audit': ['architect', 'architect', 'developer'],
        'usage': ['developer', 'developer'],
    }

    def check(title, condition, detail):
        role = step_roles[scenario_id][len(steps)]
        # Capture each checkpoint immediately, before later mutations occur.
        checkpoint = {
            'accepted_context': [
                {'id': item['id'], 'title': item['title'], 'revision': item['revision'], 'body': item['body']}
                for item in state['contexts'].values() if d.visible(item, role)
            ],
            'proposals': [
                {'title': item['title'], 'status': item['status'], 'hash': item['hash']}
                for item in state['proposals'].values()
            ],
            'stale_runs': sum(bool(task.get('stale')) for task in state['tasks'].values()),
        }
        steps.append({'title': title, 'passed': bool(condition), 'detail': detail,
                      'role': role, 'actor': f'demo-{role}', 'at': d.now(), 'checkpoint': deepcopy(checkpoint)})

    def expect_block(title, operation, status):
        try:
            operation()
            check(title, False, 'The operation unexpectedly succeeded.')
        except d.Problem as exc:
            check(title, exc.status == status, f'HTTP-equivalent {exc.status}: {exc.message}')

    def change(body=None):
        return d.propose(state, 'demo-developer', 'developer', {'context_id':'ARC-001','base_revision':state['contexts']['ARC-001']['revision'], 'body':body or state['contexts']['ARC-001']['body'].replace('3 times','2 times'), 'reason':'Reduce retry latency while preserving safety.', 'sources':['Synthetic architecture review']})

    def publish(proposal):
        return d.review(state, 'demo-architect', 'architect', proposal['id'], proposal['hash'], 'approve')

    if scenario_id == 'handoff':
        accepted = state['contexts']['REQ-001']
        check('Product intent is accepted shared knowledge', accepted['revision'] == 1 and accepted['owner'] == 'pm', f"{accepted['id']} v1 · owned by Product manager")
        evidence['manifests'] = []
        for role in ('architect','developer','qa'):
            manifest = d.assemble(state, role, scenario['query'], 6000)
            output, usage = offline.task(role, scenario['query'], manifest)
            check(f"{'QA engineer' if role == 'qa' else role.title()} receives the same accepted requirement", any(x['id']=='REQ-001' and x['revision']==1 for x in manifest['sources']) and '[REQ-001 v1]' in output, 'The source briefing cites REQ-001 v1 without copying a previous persona’s conversation.')
            evidence['manifests'].append({'role':role,'sources':[{'id':s['id'],'revision':s['revision']} for s in manifest['sources']]})
    elif scenario_id in ('ingestion','manual'):
        if scenario_id == 'ingestion':
            notes = 'Customers must see a clear explanation when a card is declined. Never automatically retry a declined card.'
            candidate, usage = offline.extract(notes)
            check('Notes become an unaccepted candidate', candidate['body'] == notes and usage['total_tokens'] == 0, 'Offline mode preserves notes verbatim; this step does not claim Gemini extraction.')
        else:
            candidate = {'title':'Payment timeout policy','domain':'Architecture','body':'Use an explicit provider timeout and preserve the original idempotency key.','reason':'Make timeout behavior reviewable.'}
        author, reviewer = ('demo-architect','demo-pm') if scenario_id == 'ingestion' else ('demo-developer','demo-architect')
        author_role, reviewer_role = ('architect','pm') if scenario_id == 'ingestion' else ('developer','architect')
        before = len(state['contexts'])
        proposal = d.propose(state, author, author_role, {**candidate,'sources':['Synthetic stakeholder note']})
        check('A proposal leaves accepted context unchanged', proposal['status']=='pending' and len(state['contexts'])==before, 'New topic is pending; no accepted document was created.')
        result = d.review(state, reviewer, reviewer_role, proposal['id'], proposal['hash'], 'approve')
        check('An independent owner publishes version one', result['status']=='published' and len(state['contexts'])==before+1, f'{reviewer} published the exact proposed content.')
        evidence['published_context'] = state['contexts'][result['published_context_id']]
    elif scenario_id == 'review':
        proposal = change()
        check('Developer proposes a design change', state['contexts']['ARC-001']['revision']==1, 'Architecture remains v1 while review is pending.')
        expect_block('Developer cannot approve architecture', lambda: d.review(state,'another-developer','developer',proposal['id'],proposal['hash'],'approve'),403)
        expect_block('A mismatched review hash cannot publish', lambda: d.review(state,'demo-architect','architect',proposal['id'],'0'*64,'approve'),409)
        publish(proposal)
        check('Architect publishes the exact revision', state['contexts']['ARC-001']['body']==proposal['body'] and state['contexts']['ARC-001']['revision']==2, 'Owner approval atomically advances accepted architecture to v2.')
        evidence['proposal_hash'] = proposal['hash']
    elif scenario_id == 'impact':
        old = d.assemble(state,'qa',scenario['query'],6000)
        frozen = deepcopy(old)
        state['tasks']['qa-run'] = {'manifest':old,'stale':False}
        check('QA begins with architecture v1', any(s['id']=='ARC-001' and s['revision']==1 for s in old['sources']), 'The original manifest captures exact accepted bodies.')
        publish(change())
        check('Publishing v2 flags dependent work', state['tasks']['qa-run']['stale'], 'The old QA run now needs review.')
        new = d.assemble(state,'qa',scenario['query'],6000)
        check('Refresh adopts v2 without rewriting history', old==frozen and any(s['id']=='ARC-001' and s['revision']==2 for s in new['sources']), 'Old snapshot keeps v1; newly assembled context contains v2.')
        evidence.update(old_sources=old['sources'],new_sources=new['sources'])
    elif scenario_id == 'restricted':
        security = d.assemble(state,'security','internal security finding',10000)
        developer = d.assemble(state,'developer','internal security finding',10000)
        check('Security can retrieve its restricted finding', any(s['id']=='RES-001' for s in security['sources']), 'The explicitly authorized Security persona has access.')
        expect_block('Developer direct access is denied',lambda:d.context(state,'RES-001','developer'),404)
        check('Developer retrieval excludes the finding', all(s['id']!='RES-001' for s in developer['sources']), 'Filtering occurs before the context reaches the agent.')
        state['tasks']['security-run'] = {'manifest':security,'output':'Synthetic restricted result','stale':False}
        d.audit(state,'demo-security','Finding reviewed','RES-001','Restricted event detail')
        view = d.snapshot(state,'developer')
        check('Derived outputs and activity stay protected', not view['tasks'] and all(e['context_id']!='RES-001' for e in view['events']), 'The derived run and restricted audit event are absent from the developer view.')
        evidence.update(security_source_ids=[s['id'] for s in security['sources']],developer_source_ids=[s['id'] for s in developer['sources']])
    elif scenario_id == 'conflict':
        first, second = change(), change('A competing payment architecture proposal.')
        check('Both proposals reference the same base', first['base_revision']==second['base_revision']==1, 'Two edits were prepared against v1.')
        publish(first)
        expect_block('The competing stale proposal is rejected',lambda:publish(second),409)
        check('The winner is not silently overwritten', state['contexts']['ARC-001']['body']==first['body'] and state['contexts']['ARC-001']['revision']==2, 'Accepted state remains the first published change at v2.')
        evidence['history'] = state['contexts']['ARC-001']['history']
    elif scenario_id == 'rollback':
        original = state['contexts']['ARC-001']['body']
        publish(change())
        check('A changed design is accepted at v2', state['contexts']['ARC-001']['revision']==2, 'The original v1 history remains stored.')
        publish(change(original))
        item = state['contexts']['ARC-001']
        check('Restoration creates v3', item['body']==original and item['revision']==3, 'The restored body is a new accepted revision, not a history rewrite.')
        check('All three revisions remain attributable', [h['revision'] for h in item['history']]==[1,2,3], 'v1 → changed v2 → restored v3 are all preserved.')
        evidence['history'] = item['history']
    elif scenario_id == 'budget':
        manifest = d.assemble(state,'developer','idempotency',1200)
        check('Selected context fits the configured budget', manifest['estimated_tokens']<=1200, f"{manifest['estimated_tokens']} conservative estimated tokens out of 1,200.")
        check('Mandatory rules remain included', {'REQ-001','SEC-001'} <= {s['id'] for s in manifest['sources']}, 'Business safety and sensitive-data guardrails survive selection.')
        expect_block('An impossible budget fails explicitly',lambda:d.assemble(state,'developer','idempotency',10),422)
        evidence['manifest'] = manifest
    elif scenario_id == 'rejection':
        before = deepcopy(state['contexts']['ARC-001'])
        proposal = change('Retry every payment without an idempotency key.')
        d.review(state,'demo-architect','architect',proposal['id'],proposal['hash'],'reject')
        check('Reviewer rejects the unsafe suggestion',state['proposals'][proposal['id']]['status']=='rejected','The suggestion is recorded as rejected, never accepted.')
        check('Accepted architecture remains unchanged',state['contexts']['ARC-001']==before,'The original v1 body and history are untouched.')
        expect_block('A rejected proposal cannot be republished',lambda:publish(proposal),409)
    elif scenario_id == 'audit':
        proposal = change(); publish(proposal)
        item = state['contexts']['ARC-001']
        manifest = d.assemble(state,'developer','payment architecture',6000)
        check('The reviewed content hash stays stable',d.digest(state['proposals'][proposal['id']])==proposal['hash'],'Approval refers to the exact immutable proposal content.')
        check('Publication records the reviewer',item['history'][-1]['actor']=='demo-architect' and state['events'][-1]['actor']=='demo-architect','History and the publication event both attribute the decision.')
        check('The next manifest identifies the accepted revision',any(s['id']=='ARC-001' and s['revision']==2 and s['body']==item['body'] for s in manifest['sources']),'The source inspector can show precisely what the agent received.')
        evidence.update(proposal_hash=proposal['hash'],history=item['history'],events=state['events'])
    elif scenario_id == 'usage':
        manifest = d.assemble(state,'developer','idempotency',1200)
        _, usage = offline.task('developer','idempotency',manifest)
        check('Both estimates have the same measurement basis',manifest['estimated_tokens']<=manifest['baseline_estimated_tokens'],f"Selected {manifest['estimated_tokens']} vs all visible {manifest['baseline_estimated_tokens']} UTF-8-byte estimates.")
        check('Offline rehearsal reports zero model tokens',usage['provider']=='offline' and usage['total_tokens']==0,'No model was called. Context estimates are not billed tokens or measured cost savings.')
        evidence.update(usage=usage,estimator=manifest['estimator'],selected_estimate=manifest['estimated_tokens'],baseline_estimate=manifest['baseline_estimated_tokens'])
    return {'id':scenario_id,'title':scenario['title'],'passed':all(s['passed'] for s in steps),'steps':steps,'evidence':evidence,'mode':'isolated-offline-rehearsal','at':d.now()}
