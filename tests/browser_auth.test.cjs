const test = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const source = fs.readFileSync('web/auth.js','utf8');

function browser(replies) {
  const calls = [];
  const context = {window:{},fetch:async (url,options={})=>{
    calls.push({url,options});
    const reply = replies.shift();
    if (!reply) throw new Error('Unexpected network request');
    return {ok:reply.status<400,status:reply.status,json:async()=>reply.body};
  }};
  // No localStorage/sessionStorage provided: any attempted token persistence fails.
  vm.runInNewContext(source,context);
  return {auth:context.window.contextosIdentity,calls};
}
const config = {auth_mode:'firebase',login_ready:true,firebase_api_key:'public-key',csrf_token:'nonce'};
const ok = body=>({status:200,body});

test('password goes only to Firebase; session exchange carries CSRF and ID token',async()=>{
  const {auth,calls}=browser([ok(config),ok({idToken:'signed-id',refreshToken:'never-persist'}),ok(config),ok({role:'qa'})]);
  await auth.signIn('test@example.invalid','synthetic-password');
  const provider=calls[1];
  assert.match(provider.url,/^https:\/\/identitytoolkit.googleapis.com\/v1\/accounts:signInWithPassword\?/);
  assert.equal(provider.options.credentials,'omit');
  assert.equal(JSON.parse(provider.options.body).password,'synthetic-password');
  const session=calls[3];
  assert.equal(session.url,'/api/auth/session');
  assert.equal(session.options.headers['X-ContextOS-CSRF'],'nonce');
  assert.deepEqual(JSON.parse(session.options.body),{id_token:'signed-id'});
  assert.ok(!session.options.body.includes('never-persist'));
});

test('configuration missing prevents credential submission',async()=>{
  const {auth,calls}=browser([ok({...config,login_ready:false})]);
  await assert.rejects(auth.signIn('test@example.invalid','synthetic-password'),/administrator/);
  assert.equal(calls.length,1);
});

test('provider rejection stays generic and does not mint a session',async()=>{
  const {auth,calls}=browser([ok(config),{status:400,body:{error:{message:'EMAIL_NOT_FOUND'}}}]);
  await assert.rejects(auth.signIn('test@example.invalid','synthetic-password'),/Check your credentials/);
  assert.equal(calls.length,2);
});

test('logout obtains nonce and posts only to same-origin backend',async()=>{
  const {auth,calls}=browser([ok(config),ok({signed_out:true})]);
  await auth.signOut();
  assert.equal(calls[1].url,'/api/auth/logout');
  assert.equal(calls[1].options.headers['X-ContextOS-CSRF'],'nonce');
  assert.equal(calls[1].options.credentials,'same-origin');
});
