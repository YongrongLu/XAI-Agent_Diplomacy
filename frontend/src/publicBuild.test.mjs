import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { readFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';
import test from 'node:test';

test('the public bundle runs without localhost or paid evaluation controls', () => {
  const frontend = new URL('..', import.meta.url).pathname;
  execFileSync('npm', ['run', 'build'], {
    cwd: frontend,
    env: { ...process.env, VITE_PUBLIC_DEMO: '1' },
    stdio: 'pipe',
  });
  const assets = join(frontend, 'dist', 'assets');
  const bundle = readdirSync(assets).filter(name => name.endsWith('.js'))
    .map(name => readFileSync(join(assets, name), 'utf8')).join('\n');
  assert.equal(bundle.includes('127.0.0.1:8000'), false);
  assert.equal(bundle.includes('Run benchmark'), false);
  assert.equal(bundle.includes('Separate local agent processes'), false);
});
