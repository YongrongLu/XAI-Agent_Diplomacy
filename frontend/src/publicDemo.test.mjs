import assert from 'node:assert/strict';
import test from 'node:test';
import { createPublicDemo } from './publicDemo.ts';

function advanceToApproval(demo) {
  demo.request('/api/session/start', 'POST');
  for (let index = 0; index < 5; index += 1) demo.request('/api/session/next', 'POST');
  const state = demo.request('/api/session');
  assert.equal(state.status, 'pending_approval');
  return state.pending_approval.id;
}

test('a public demo starts locally and pauses at Alice’s $150 request', () => {
  const demo = createPublicDemo();
  assert.equal(demo.request('/api/session').status, 'idle');
  const requestId = advanceToApproval(demo);
  const paused = demo.request('/api/session/next', 'POST');
  assert.equal(paused.status, 'pending_approval');
  assert.equal(paused.pending_approval.id, requestId);
  assert.equal(paused.events.some(event => event.action === 'FINALIZE'), false);
});

test('approval applies only the matching request and cannot be replayed', () => {
  const demo = createPublicDemo();
  const requestId = advanceToApproval(demo);
  assert.deepEqual(demo.request('/api/approvals/other/decide', 'POST', { choice: 'approve' }), { error: 'No matching pending request' });
  assert.equal(demo.request(`/api/approvals/${requestId}/decide`, 'POST', { choice: 'approve' }).decision, 'approve');
  assert.deepEqual(demo.request(`/api/approvals/${requestId}/decide`, 'POST', { choice: 'approve' }), { error: 'No matching pending request' });
  const complete = demo.request('/api/session/next', 'POST');
  assert.equal(complete.status, 'complete');
  assert.equal(complete.outcome.alice_extra, 150);
});

test('rejection keeps the permitted $60 proposal, and reset clears the session', () => {
  const demo = createPublicDemo();
  const requestId = advanceToApproval(demo);
  demo.request(`/api/approvals/${requestId}/decide`, 'POST', { choice: 'reject' });
  const complete = demo.request('/api/session/next', 'POST');
  assert.equal(complete.outcome.alice_extra, 60);
  assert.equal(complete.outcome.hotel.id, 'palmetto');
  const reset = demo.request('/api/session/reset', 'POST');
  assert.equal(reset.status, 'idle');
  assert.equal(reset.events.length, 0);
});
