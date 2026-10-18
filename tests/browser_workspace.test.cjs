const test = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const source = fs.readFileSync('web/app.js','utf8');

// Run the shipped controller with DOM sinks and API fixtures, without a browser.
function workspace(fixture) {
  const elements = new Map(), handlers = {document:{},window:{}}, storage = new Map(), calls = [];
  function element(selector) {
    if (!elements.has(selector)) elements.set(selector, {
      innerHTML:'',textContent:'',value:'',open:false,classList:{add(){},remove(){},toggle(){}},
      addEventListener(){},replaceChildren(){this.innerHTML='';},close(){this.open=false;},
      showModal(){this.open=true;},focus(){},scrollIntoView(){}
    });
    return elements.get(selector);
  }
  const context = vm.createContext({
    document:{querySelector:element,addEventListener:(name,fn)=>handlers.document[name]=fn,
      body:element('body'),getElementById:id=>element(`#${id}`)},
    window:{addEventListener:(name,fn)=>handlers.window[name]=fn,scrollTo(){},
      contextosIdentity:{configuration:()=>new Promise(()=>{})}},
    location:{hash:''},sessionStorage:{getItem:key=>storage.get(key)??null,
      setItem:(key,value)=>storage.set(key,String(value)),removeItem:key=>storage.delete(key)},
    requestAnimationFrame:fn=>fn(),setTimeout:()=>1,clearTimeout(){},
    fetch:async (url,options)=>{
      calls.push({url,options});
      const body = url==='/api/workspace' ? context.fixture : {recorded:true};
      return {ok:true,json:async()=>body};
    },fixture
  });
  vm.runInContext(source,context);
  return {element,handlers,storage,calls,context,
    run:code=>vm.runInContext(code,context),
    render:(route='',runId=null)=>{
      context.route=route;context.runId=runId;
      vm.runInContext('state=fixture;currentView=resolveView(route);activeRun=state.tasks.find(t=>t.id===runId);render();',context);
    }};
}

function state() {
  return {actor:'architect-me',role:'architect',auth_mode:'firebase',ai_mode:'offline',
    project:{name:'Test project'},contexts:[],proposals:[],tasks:[],events:[],usage:[],
    next_actions:[{kind:'task',query:'Review the accepted design'}]};
}
function run(id,actor,query) {
  return {id,actor,role:'architect',query,stale:true,output:'Existing answer',created_at:'2026-10-18T12:00:00Z',
    manifest:{sources:[],budget:6000,estimated_tokens:1,estimator:'test'},usage:{model:null,total_tokens:0}};
}

test('three primary destinations preserve old bookmarks and secondary demo access',()=>{
  const fixture=state();fixture.auth_mode='demo';
  const page=workspace(fixture);
  for (const route of ['', 'overview', 'tasks', 'work', 'constructor', 'unknown']) {
    page.render(route);
    assert.equal(page.element('#crumb').textContent,'Work');
    assert.equal((page.element('#main').innerHTML.match(/id="task-form"/g)||[]).length,1);
    assert.deepEqual([...page.element('#nav').innerHTML.matchAll(/href="#([^"]+)"/g)].map(m=>m[1]),['work','knowledge','inbox']);
  }
  page.render('reviews');assert.equal(page.element('#crumb').textContent,'Inbox');
  assert.match(page.element('#secondary-nav').innerHTML,/href="#demo"/);
  assert.match(page.element('#mobile-tools').innerHTML,/href="#insights"/);
  fixture.auth_mode='firebase';page.render('work');
  assert.doesNotMatch(page.element('#secondary-nav').innerHTML,/href="#demo"/);
});

test('Inbox counts owned reviews and affected personal runs without granting self-review',async()=>{
  const fixture=state();
  fixture.proposals=[
    {id:'reviewable',title:'Reviewable design',domain:'Architecture',author:'developer',status:'pending'},
    {id:'self',title:'My own proposal',domain:'Architecture',author:fixture.actor,status:'pending'},
    {id:'other-domain',title:'Product proposal',domain:'Requirements',author:'product',status:'pending'},
  ];
  fixture.tasks=[run('mine',fixture.actor,'My affected task'),run('someone-else','other-architect','Other user task')];
  const page=workspace(fixture);page.render('inbox');
  assert.match(page.element('#nav').innerHTML,/2 items need your attention/);
  assert.match(page.element('#main').innerHTML,/My affected task/);
  assert.doesNotMatch(page.element('#main').innerHTML,/Other user task/);
  assert.match(page.element('#main').innerHTML,/data-action="approve" data-id="reviewable"/);
  assert.doesNotMatch(page.element('#main').innerHTML,/data-action="approve" data-id="self"/);
  await page.run('action({dataset:{action:"inbox-filter",filter:"mine"}})');
  assert.match(page.element('#main').innerHTML,/id="proposal-reviewable"/);
  assert.doesNotMatch(page.element('#main').innerHTML,/id="proposal-(self|other-domain)"/);
});

test('opening an old run keeps its original source inspector after accepted content changes',async()=>{
  const fixture=state(), old=run('old',fixture.actor,'Earlier work');
  fixture.contexts=[{id:'ARC-1',body:'New accepted body',revision:2}];
  old.manifest.sources=[{id:'ARC-1',title:'Original <design>',body:'Original source body',revision:1}];
  fixture.tasks=[old];
  const page=workspace(fixture);page.render('inbox');
  await page.run('action({dataset:{action:"open-run",id:"old"}})');
  assert.equal(page.context.location.hash,'work');
  await page.handlers.window.hashchange();
  assert.match(page.element('#main').innerHTML,/Original &lt;design&gt;/);
  assert.match(page.element('#main').innerHTML,/ARC-1 · v1/);
  await page.run('action({dataset:{action:"manifest",id:"old"}})');
  assert.match(page.element('#dialog-content').innerHTML,/Original source body/);
  assert.doesNotMatch(page.element('#dialog-content').innerHTML,/New accepted body/);
  assert.equal(JSON.parse(page.calls.at(-1).options.body).target_id,'old');
});

test('task drafts and advanced budgets survive navigation and clear on sign-out',async()=>{
  const page=workspace(state());page.render('work');
  page.handlers.document.input({target:{id:'task-query',value:'Draft <work>'}});
  page.handlers.document.change({target:{id:'task-budget',value:'3000'}});
  page.context.location.hash='#knowledge';await page.handlers.window.hashchange();
  page.context.location.hash='#work';await page.handlers.window.hashchange();
  assert.match(page.element('#main').innerHTML,/Draft &lt;work&gt;/);
  assert.match(page.element('#main').innerHTML,/value="3000" selected/);
  page.run('clearProtectedView()');
  assert.equal(page.storage.size,0);
  for (const selector of ['#main','#nav','#secondary-nav','#mobile-tools']) assert.equal(page.element(selector).innerHTML,'');
});

test('entering Inbox refreshes shared changes and history never offers publication',async()=>{
  const fixture=state(),page=workspace(fixture);page.render('work');
  page.context.fixture={...fixture,proposals:[{id:'new',title:'A newly shared decision',domain:'Architecture',
    author:'developer',status:'published',reviewer:'architect-me'}]};
  page.context.location.hash='#reviews';await page.handlers.window.hashchange();
  assert.equal(page.calls.filter(c=>c.url==='/api/workspace').length,1);
  await page.run('action({dataset:{action:"inbox-filter",filter:"history"}})');
  assert.match(page.element('#main').innerHTML,/A newly shared decision/);
  assert.doesNotMatch(page.element('#main').innerHTML,/data-action="approve"/);
});

test('Knowledge search combines text and domain filters without replacing the search input',()=>{
  const fixture=state();
  fixture.contexts=[
    {id:'ARC-1',title:'Retry design',body:'Use idempotency',domain:'Architecture',owner:'architect',revision:1},
    {id:'REQ-1',title:'Payment requirement',body:'Retry transient failures',domain:'Requirements',owner:'pm',revision:1},
  ];
  const page=workspace(fixture);page.render('knowledge');
  const search=page.element('#search');
  page.handlers.document.input({target:{id:'search',value:'RETRY'}});
  assert.match(page.element('#knowledge-results').innerHTML,/Retry design/);
  assert.match(page.element('#knowledge-results').innerHTML,/Payment requirement/);
  page.handlers.document.change({target:{id:'domain-filter',value:'Architecture'}});
  assert.match(page.element('#knowledge-results').innerHTML,/Retry design/);
  assert.doesNotMatch(page.element('#knowledge-results').innerHTML,/Payment requirement/);
  assert.equal(page.element('#search'),search);
});

test('an Inbox response arriving after sign-out cannot restore protected content',async()=>{
  const page=workspace(state());page.render('work');
  let deliver;
  page.context.fixture=new Promise(resolve=>deliver=resolve);
  page.context.location.hash='#inbox';
  const navigation=page.handlers.window.hashchange();
  page.run('clearProtectedView()');
  deliver({...state(),project:{name:'Protected project'}});
  await navigation;
  assert.equal(page.run('state'),undefined);
  assert.equal(page.element('#main').innerHTML,'');
  assert.equal(page.element('#nav').innerHTML,'');
});
