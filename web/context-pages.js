'use strict';
window.contextPages = (() => {
  const escape = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
  const roles = ['pm','architect','developer','qa','security'];
  const button = (label, action, attrs = '', primary = false) => '<button type="button" class="btn '+(primary?'primary':'')+'" data-cp-action="'+action+'" '+attrs+'>'+label+'</button>';
  const options = (items, value, label, selected) => items.map(item=>'<option value="'+escape(value(item))+'" '+(value(item)===selected?'selected':'')+'>'+escape(label(item))+'</option>').join('');
  const badge = status => '<span class="tag '+(status==='stale'?'amber':'green')+'">'+escape(status==='up_to_date'?'Up to date':status)+'</span>';
  let root, onProposal, onUnauthorized, template, projects, project, page, parts, status, history, proposals, selectedProposal;
  let generation=0, loadVersion=0, mode='page', mapView=null, mapControls=null, mapOpen=true;
  const projectPath = () => '/projects/'+encodeURIComponent(project.project.id);
  const contextPath = () => projectPath()+'/contexts/'+encodeURIComponent(page.id);
  const markdown = content => {
    if(!window.marked || !window.DOMPurify)return '<pre class="cp-markdown">'+escape(content)+'</pre>';
    return window.DOMPurify.sanitize(window.marked.parse(content), {
      ALLOWED_TAGS:['p','h1','h2','h3','h4','h5','h6','ul','ol','li','strong','em','del','code','pre','blockquote','a','hr','br','table','thead','tbody','tr','th','td'],
      ALLOWED_ATTR:['href','title'], ALLOW_DATA_ATTR:false, ALLOW_ARIA_ATTR:false
    });
  };
  async function request(path, method='GET', body) {
    const current=generation;
    const response=await fetch('/api/context'+path,{method,credentials:'same-origin',headers:{'Content-Type':'application/json','X-ContextOS-Client':'workspace'},...(body===undefined?{}:{body:JSON.stringify(body)})});
    const result=await response.json();
    if(response.status===401 && current===generation)onUnauthorized?.(result.detail||'Sign in to continue.');
    if(!response.ok)throw new Error(Array.isArray(result.detail)?result.detail.map(item=>item.msg).join('; '):result.detail||'Request failed');
    return result;
  }
  function message(text) {
    const output=root?.querySelector('#context-message');
    if(output){output.textContent=text;output.hidden=!text;}
  }
  async function load(projectId=project?.project.id, contextId=page?.id, nextMode='page') {
    const current=generation, container=root, selection=++loadVersion;
    const active=()=>current===generation && selection===loadVersion && container?.isConnected;
    const list=await request('/projects?include_archived=true');
    if(!active())return;
    const chosen=list.find(item=>item.id===projectId)||list.find(item=>!item.archived)||list[0];
    if(!chosen){projects=list;project=page=parts=status=null;history=proposals=[];mode='page';render();return;}
    const base='/projects/'+encodeURIComponent(chosen.id);
    const [nextProject,nextProposals]=await Promise.all([request(base),request(base+'/proposals')]);
    if(!active())return;
    const selected=nextProject.contexts.find(item=>item.id===contextId)||nextProject.contexts[0];
    const path=base+'/contexts/'+encodeURIComponent(selected?.id||'');
    const detail=selected?await Promise.all([request(path),request(path+'/sections'),request(path+'/status'),request(path+'/versions')]):[null,null,null,[]];
    if(!active())return;
    if(project?.project.id!==nextProject.project.id)mapView=null;
    projects=list;project=nextProject;proposals=nextProposals;[page,parts,status,history]=detail;mode=nextMode;selectedProposal=null;render();
  }
  const panel = (title, body) => '<section class="panel"><div class="panel-head"><h2>'+escape(title)+'</h2></div><div class="panel-body">'+body+'</div></section>';
  const reasonField = '<label class="field">Reason for change<textarea name="reason" required maxlength="1500" rows="2"></textarea></label>';
  const controls = label => '<div class="button-group"><button class="btn primary" type="submit">'+label+'</button>'+button('Cancel','cancel')+'</div>';
  function projectEditor(isNew) {
    const item=isNew?{}:project.project;
    return panel(isNew?'Create project':'Edit project',
      '<form id="context-project-form" data-new="'+isNew+'"><label class="field">Project name<input name="name" required maxlength="120" value="'+escape(item.name)+'"></label>'+
      '<label class="field">Project type<input name="project_type" required maxlength="80" placeholder="Software, research, content…" value="'+escape(item.project_type)+'"></label>'+
      '<label class="field">Description<textarea name="description" maxlength="1500" rows="3">'+escape(item.description)+'</textarea></label>'+
      (isNew?'<p class="muted">You become the project admin. Creation date and time are recorded automatically. The project starts with no files.</p>':
        '<label class="field">Admin user ID<input name="admin" required maxlength="128" value="'+escape(item.admin)+'"></label><p class="muted">Created '+escape(item.created_at)+' · v'+item.version+'</p>')+
      controls(isNew?'Create empty project':'Save project')+'</form>');
  }
  function contextEditor(isNew) {
    const item=isNew?{content:template.content,relationships:[],owner:'',owner_type:'pm'}:page;
    const links=project.contexts.filter(doc=>doc.id!==item.id);
    return panel(isNew?'Propose new context':'Propose context update',
      '<form id="context-page-form" data-new="'+isNew+'"><div class="cp-fields"><label class="field">File name<input name="filename" required maxlength="100" placeholder="architecture.md" value="'+escape(item.filename)+'"></label>'+
      '<label class="field">Owner<input name="owner" required maxlength="128" placeholder="Person or team" value="'+escape(item.owner)+'"></label>'+
      '<label class="field">Owner type<select name="owner_type" aria-label="Owner type">'+options(roles,value=>value,value=>value,item.owner_type)+'</select></label></div>'+
      '<label class="field">Markdown content<textarea name="content" aria-label="Markdown content" rows="17" maxlength="10000" required>'+escape(item.content)+'</textarea></label>'+
      '<p class="muted">Keep the three section headings: Overview, Details and Next steps. Use ### for subheadings.</p>'+
      '<fieldset class="cp-relationships"><legend>Relationships</legend>'+(links.map(doc=>{
        const kind=item.relationships.find(link=>link.target_id===doc.id)?.kind||'';
        return '<label class="field">'+escape(doc.filename)+'<select name="link:'+escape(doc.id)+'">'+options(['','depends_on','references'],value=>value,value=>value===''?'No relationship':value==='depends_on'?'Depends on':'References',kind)+'</select></label>';
      }).join('')||'<p class="muted">Approve another context first to connect it.</p>')+'</fieldset>'+
      reasonField+'<p class="muted">An independent '+escape(isNew?'designated owner-role':page.owner_type)+' reviewer must approve publication. An owner-type transfer is reviewed by the current owner role.</p>'+controls('Submit proposal')+'</form>');
  }
  function pageList(items) {
    return items.map(item=>'<button type="button" class="context-row '+(page?.id===item.id?'cp-active':'')+'" data-cp-action="select" data-id="'+escape(item.id)+'"><span class="row-main"><strong>'+escape(item.filename)+'</strong><small>'+escape(item.owner_type)+' · v'+item.version+' · '+escape(item.status==='up_to_date'?'Up to date':item.status)+'</small></span></button>').join('')||'<p class="panel-body muted">No approved contexts.</p>';
  }
  function pageView() {
    if(!page)return panel('No approved contexts yet','<p>Add a context proposal, then ask an independent owner-role reviewer to approve it.</p>'+(!project.project.archived?button('New context','new','',true):''));
    const outgoing=project.relationships.filter(link=>link.source_id===page.id);
    const incoming=project.relationships.filter(link=>link.target_id===page.id);
    const linkRow=(link,inbound)=>{
      const id=inbound?link.source_id:link.target_id,doc=project.contexts.find(item=>item.id===id);
      return '<li>'+escape(inbound?(link.kind==='depends_on'?'Used by':'Referenced by'):(link.kind==='depends_on'?'Depends on':'References'))+' '+button(escape(doc?.filename||id),'select','data-id="'+escape(id)+'"')+'</li>';
    };
    return '<section class="panel"><div class="panel-head"><div>'+badge(status.status)+' <span class="tag">Approved · v'+page.version+'</span>'+
      (status.pending_proposals?'<span class="tag amber">'+status.pending_proposals+' pending</span>':'')+
      '<h2>'+escape(page.filename)+'</h2><p class="muted">Owner: '+escape(page.owner)+' · '+escape(page.owner_type)+' · Updated '+escape(page.updated_at)+'</p></div>'+
      (!project.project.archived?button('Propose edit','edit','',true):'')+'</div><div class="panel-body">'+
      (status.status==='stale'?'<p class="note amber">An approved dependency changed. Review the content and propose an update to refresh this context.</p>':'')+
      '<article class="cp-rendered">'+markdown(page.content)+'</article><details><summary>Markdown source</summary><pre class="cp-markdown">'+escape(page.content)+'</pre></details>'+
      '<div class="button-group cp-page-actions">'+button('Download .md','download')+(!project.project.archived?button('Propose deletion','delete'):'')+'</div></div></section>'+
      panel('Relationships','<ul class="cp-related">'+(outgoing.map(link=>linkRow(link,false)).join('')+incoming.map(link=>linkRow(link,true)).join('')||'<li>No relationships yet.</li>')+'</ul>')+
      panel('Extract content','<form id="context-extract-form"><label class="field">Section<select name="section_key"><option value="">All sections</option>'+options(parts.sections,item=>item.key,item=>item.heading)+'</select></label><label class="field">Containing text<input name="query" maxlength="500"></label><button type="submit" class="btn">Extract</button><pre id="context-extract-result" class="cp-markdown" hidden></pre></form>')+
      '<details class="panel cp-history"><summary>Version history · '+history.length+' revisions</summary>'+history.map(item=>'<p>'+button('Version '+item.version,'version','data-version="'+item.version+'"')+' · '+escape(item.reason)+' · '+escape(item.approved_by)+'</p>').join('')+'</details>';
  }
  function proposalList() {
    return panel('Project proposals', proposals.map(item=>'<button type="button" class="context-row" data-cp-action="proposal" data-id="'+escape(item.id)+'"><span class="row-main"><strong>'+escape(item.action)+' · '+escape(item.filename||item.context_id)+'</strong><small>'+escape(item.status)+' · '+escape(item.author)+' → '+escape(item.reviewer_type)+' reviewer</small><small>'+escape(item.reason)+'</small></span></button>').join('')||'<p>No proposals yet.</p>');
  }
  function candidateView(item) {
    return '<p><strong>'+escape(item.filename)+'</strong> · '+escape(item.owner)+' · '+escape(item.owner_type)+'</p><p class="muted">Relationships: '+escape(item.relationships.map(link=>(project.contexts.find(doc=>doc.id===link.target_id)?.filename||link.target_id)+' ('+link.kind+')').join(', ')||'None')+'</p><article class="cp-rendered">'+markdown(item.content)+'</article><details><summary>Exact Markdown source</summary><pre class="cp-markdown">'+escape(item.content)+'</pre></details>';
  }
  function proposalView() {
    const item=selectedProposal,canReview=item.status==='pending' && project.actor!==item.author && project.role===item.reviewer_type;
    return panel(item.action==='delete'?'Review context deletion':'Review proposed context',
      '<p>'+badge(item.status)+' · '+escape(item.author)+' · '+escape(item.reason)+'</p>'+
      '<p class="muted">Required reviewer: '+escape(item.reviewer_type)+' · Base version '+item.base_version+'</p>'+
      (item.action==='delete'?'<p class="note amber">Approval removes this context from the active project. Historical versions are retained.</p>':'')+
      (item.before?'<details><summary>Accepted version '+item.base_version+'</summary>'+candidateView(item.before)+'</details>':'')+
      '<h3>Proposed '+(item.action==='delete'?'deletion':'version')+'</h3>'+candidateView(item.candidate)+
      (canReview?'<div class="button-group">'+button('Approve','approve','',true)+button('Reject','reject')+'</div>':
      item.status==='pending'?'<p class="note amber">An independent '+escape(item.reviewer_type)+' reviewer must decide this change. In demo mode, use the persona selector to switch to that reviewer.</p>':'')+
      button('All proposals','reviews'));
  }
  function detail() {
    if(mode==='project-new'||mode==='project-edit')return projectEditor(mode==='project-new');
    if(mode==='context-new'||mode==='context-edit')return contextEditor(mode==='context-new');
    if(mode==='reviews')return proposalList();
    if(mode==='proposal')return proposalView();
    if(mode==='delete'||mode==='archive')return panel(mode==='delete'?'Propose context deletion':'Archive project',
      '<form id="context-delete-form" data-kind="'+mode+'"><p>'+escape(mode==='delete'?page.filename:project.project.name)+'</p><p class="muted">'+(mode==='delete'?'Deletion requires owner-role approval.':'Archiving hides the project from active lists. You can restore it; history is retained.')+'</p>'+reasonField+controls(mode==='delete'?'Submit deletion proposal':'Archive project')+'</form>');
    return pageView();
  }
  function render() {
    mapControls?.destroy(); mapControls=null;
    const focused=root.querySelector('[data-cp-action="select"]:focus');
    const focus=focused?{id:focused.dataset.id,map:focused.dataset.cpMapNode!==undefined}:null;
    mapOpen=root.querySelector('[data-context-map]')?.open??mapOpen;
    const meta=project?.project;
    const toolbar='<div class="cp-toolbar">'+(projects.length?'<label class="field">Project<select id="context-project-select">'+options(projects,item=>item.id,item=>item.name+(item.archived?' (archived)':''),meta?.id)+'</select></label>':'')+
      button('New project','project-new')+(meta?button('Project details','project-details')+button('Proposals ('+proposals.filter(item=>item.status==='pending').length+')','reviews')+(!meta.archived?button('New context','new','',true):''):'')+'</div>';
    const graph=meta?window.contextMap.render(project.contexts.map(item=>({...item,title:item.filename,domain:item.owner_type+(item.status==='stale'?' · stale':''),revision:item.version})),project.relationships,page?.id,mapView?.zoom??1,mapOpen):'';
    root.innerHTML='<div id="context-message" class="note amber" role="status" hidden></div>'+toolbar+
      (meta?'<div class="cp-project-meta"><span class="tag">'+escape(meta.project_type)+'</span><span>'+escape(meta.description)+'</span>'+(meta.archived?badge('archived'):'')+'</div>':'')+
      graph+(meta?'<div class="cp-layout"><aside class="panel cp-list"><form id="context-search-form" class="panel-body"><label class="field">Find context<input name="query" type="search" maxlength="500"></label><button class="btn small" type="submit">Search</button></form><div id="context-page-list">'+pageList(project.contexts)+'</div></aside><div id="context-detail">'+detail()+'</div></div>':
      '<div id="context-detail">'+(mode==='project-new'?projectEditor(true):panel('Create your first project','<p>Start with a project name, type and description. Add Markdown contexts when you are ready.</p>'+button('Create project','project-new','',true)))+'</div>');
    mapControls=window.contextMap.mount(root,mapView,view=>{mapView=view;});
    if(focus){const cards=root.querySelectorAll(focus.map?'[data-cp-map-node]':'#context-page-list [data-cp-action="select"]');[...cards].find(card=>card.dataset.id===focus.id)?.focus({preventScroll:true});}
  }
  async function action(target) {
    const action=target.dataset.cpAction,current=generation,selection=loadVersion;
    if(action.startsWith('map-'))return mapControls?.command(action);
    if(action==='select'){target.focus({preventScroll:true});return load(project.project.id,target.dataset.id);}
    if(action==='project-new'){mode='project-new';render();return;}
    if(action==='new'||action==='edit'){mode=action==='new'?'context-new':'context-edit';render();return;}
    if(action==='cancel'){mode='page';render();return;}
    if(action==='reviews'){mode='reviews';render();return;}
    if(action==='delete'){mode='delete';render();return;}
    if(action==='project-details'){
      mode='project-edit';
      render();
      if(project.actor!==project.project.admin){
        root.querySelector('#context-project-form').querySelectorAll('input,textarea,button[type="submit"]').forEach(input=>input.disabled=true);
        message('Only '+project.project.admin+' can edit project metadata.');
      } else {
        root.querySelector('#context-project-form').insertAdjacentHTML('beforeend',button(project.project.archived?'Restore project':'Archive project',project.project.archived?'restore':'archive'));
      }
      return;
    }
    if(action==='archive'){mode='archive';render();return;}
    if(action==='restore'){
      const item=project.project;
      await request(projectPath(),'PUT',{name:item.name,project_type:item.project_type,description:item.description,admin:item.admin,expected_version:item.version,archived:false});
      if(current===generation)await load();
      return;
    }
    if(action==='proposal'){
      const result=await request(projectPath()+'/proposals/'+encodeURIComponent(target.dataset.id));
      if(current!==generation||selection!==loadVersion||!root?.isConnected)return;
      selectedProposal=result;mode='proposal';render();return;
    }
    if(action==='approve'||action==='reject'){
      target.disabled=true;
      try{
        await request(projectPath()+'/proposals/'+encodeURIComponent(selectedProposal.id)+'/review','POST',{hash:selectedProposal.hash,decision:action==='approve'?'approve':'reject'});
        if(current===generation){await load(project.project.id,selectedProposal.context_id,action==='approve'?'page':'reviews');message(action==='approve'?'Proposal approved.':'Proposal rejected.');}
      }finally{target.disabled=false;}
      return;
    }
    if(action==='version'){
      const result=await request(contextPath()+'/versions/'+encodeURIComponent(target.dataset.version));
      if(current===generation&&selection===loadVersion&&root?.isConnected)root.querySelector('#context-detail').innerHTML=panel('Historical version '+result.version,candidateView(result)+button('Back to current','cancel'));
      return;
    }
    if(action==='download'){
      const blob=new Blob([page.content],{type:'text/markdown;charset=utf-8'}),url=URL.createObjectURL(blob),link=document.createElement('a');
      link.href=url;link.download=page.filename;link.click();URL.revokeObjectURL(url);
    }
  }
  async function submit(form) {
    const current=generation,selection=loadVersion,input=Object.fromEntries(new FormData(form));
    const active=()=>current===generation && selection===loadVersion && root?.isConnected;
    if(form.id==='context-project-form'){
      const isNew=form.dataset.new==='true';
      const data={name:input.name,project_type:input.project_type,description:input.description};
      if(!isNew)Object.assign(data,{admin:input.admin,expected_version:project.project.version,archived:project.project.archived});
      const result=await request(isNew?'/projects':projectPath(),isNew?'POST':'PUT',data);
      if(active())await load(result.id,null);
    }
    if(form.id==='context-page-form'){
      const isNew=form.dataset.new==='true';
      const data={filename:input.filename,content:input.content,owner:input.owner,owner_type:input.owner_type,reason:input.reason,relationships:Object.entries(input).filter(([key,value])=>key.startsWith('link:')&&value).map(([key,kind])=>({target_id:key.slice(5),kind}))};
      if(!isNew)data.expected_version=page.version;
      await request(isNew?projectPath()+'/contexts':contextPath(),isNew?'POST':'PUT',data);
      if(active()){await load(project.project.id,page?.id,'reviews');await onProposal?.();}
    }
    if(form.id==='context-delete-form'){
      await request(form.dataset.kind==='archive'?projectPath():contextPath(),'DELETE',{expected_version:form.dataset.kind==='archive'?project.project.version:page.version,reason:input.reason});
      if(active())await load(project.project.id,page?.id,form.dataset.kind==='archive'?'page':'reviews');
    }
    if(form.id==='context-search-form'){
      const result=await request(projectPath()+'/search?q='+encodeURIComponent(input.query));
      if(active())root.querySelector('#context-page-list').innerHTML=pageList(result.items);
    }
    if(form.id==='context-extract-form'){
      const result=await request(contextPath()+'/extract','POST',{section_keys:input.section_key?[input.section_key]:[],query:input.query,max_chars:8000});
      if(!active())return;
      const output=root.querySelector('#context-extract-result');
      output.textContent='Approved version '+result.version+'\n\n'+(result.content||'No matching content.');output.hidden=false;
    }
  }
  async function run(operation) {const current=generation;try{message('');await operation();}catch(error){if(current===generation)message(error.message);}}
  function clear() {
    mapControls?.destroy();mapControls=null;
    generation++;loadVersion++;mapView=null;mapOpen=true;mode='page';
    root=onProposal=onUnauthorized=template=projects=project=page=parts=status=history=proposals=selectedProposal=null;
  }
  async function mount(element, afterProposal, onExpired) {
    clear();const current=generation;root=element;onProposal=afterProposal;onUnauthorized=onExpired;
    root.addEventListener('click',event=>{const target=event.target.closest('[data-cp-action]');if(target)run(()=>action(target));});
    root.addEventListener('change',event=>{if(event.target.id==='context-project-select')run(()=>load(event.target.value,null));});
    root.addEventListener('submit',event=>{
      event.preventDefault();const submitButton=event.target.querySelector('[type="submit"]');
      if(submitButton?.disabled)return;if(submitButton)submitButton.disabled=true;
      run(()=>submit(event.target)).finally(()=>{if(submitButton)submitButton.disabled=false;});
    });
    root.addEventListener('keydown',event=>{
      if(!event.target.matches('[data-cp-map-node]'))return;
      if(event.key==='Enter'||event.key===' '){event.preventDefault();run(()=>action(event.target));return;}
      const direction={ArrowRight:[1,0],ArrowLeft:[-1,0],ArrowDown:[0,1],ArrowUp:[0,-1]}[event.key];
      if(!direction)return;
      event.preventDefault();
      const distance=card=>{const x=Number(card.dataset.mapX)-Number(event.target.dataset.mapX),y=Number(card.dataset.mapY)-Number(event.target.dataset.mapY);const forward=x*direction[0]+y*direction[1];return forward>0?forward+3*Math.abs(x*direction[1]-y*direction[0]):Infinity;};
      [...root.querySelectorAll('[data-cp-map-node]')].filter(card=>Number.isFinite(distance(card))).sort((a,b)=>distance(a)-distance(b))[0]?.focus();
    });
    try{
      const result=await request('/template');
      if(current!==generation||!element.isConnected)return;
      template=result;await load();
    }catch(error){if(current===generation&&element.isConnected)element.textContent=error.message;}
  }
  return {mount,clear};
})();
