// Browser-local replay of states exported from the deterministic V0 engine.
import { publicDemoScenes } from './publicDemoScenes.ts';

type Snapshot = typeof publicDemoScenes.initial | (typeof publicDemoScenes.progression)[number]
  | (typeof publicDemoScenes.decisions.approve)[number] | (typeof publicDemoScenes.decisions.reject)[number];

export function createPublicDemo() {
  let current: Snapshot = publicDemoScenes.initial;
  let progressionIndex = -1;
  let decision: 'approve' | 'reject' | null = null;
  let decisionIndex = -1;

  return {
    request(path: string, method = 'GET', body?: { choice?: string }) {
      if (path === '/api/session' && method === 'GET') return current;
      if (path === '/api/session/reset' && method === 'POST') {
        current = publicDemoScenes.initial;
        progressionIndex = -1;
        decision = null;
        decisionIndex = -1;
        return current;
      }
      if (path === '/api/session/start' && method === 'POST') {
        if (current.status === 'idle') {
          progressionIndex = 0;
          current = publicDemoScenes.progression[progressionIndex];
        }
        return current;
      }
      if (path === '/api/session/next' && method === 'POST') {
        if (current.status !== 'running') return current;
        if (decision) {
          decisionIndex = Math.min(decisionIndex + 1, publicDemoScenes.decisions[decision].length - 1);
          current = publicDemoScenes.decisions[decision][decisionIndex];
        } else {
          progressionIndex = Math.min(progressionIndex + 1, publicDemoScenes.progression.length - 1);
          current = publicDemoScenes.progression[progressionIndex];
        }
        return current;
      }
      const match = /^\/api\/approvals\/([^/]+)\/decide$/.exec(path);
      if (match && method === 'POST') {
        if (!current.pending_approval || match[1] !== current.pending_approval.id)
          return { error: 'No matching pending request' };
        if (body?.choice !== 'approve' && body?.choice !== 'reject')
          return { error: 'Decision must be approve or reject' };
        decision = body.choice;
        decisionIndex = 0;
        current = publicDemoScenes.decisions[decision][decisionIndex];
        return current;
      }
      return { error: 'Unsupported browser demo request' };
    },
    inspector() { return publicDemoScenes.inspector; },
  };
}

export const publicDemo = createPublicDemo();
