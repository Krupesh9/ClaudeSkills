#!/usr/bin/env node
// Wraps `npx power-apps init` with sensible defaults from .env / power.config.json.
// Usage: npm run setup

import { spawnSync } from 'node:child_process';
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { parseEnv } from './lib/env-parser.js';

const envPath = '.env';
const cfgPath = 'power.config.json';

if (!existsSync(envPath)) {
  console.error('❌ .env not found. Copy .env.example → .env and fill in values first.');
  process.exit(1);
}
if (!existsSync(cfgPath)) {
  console.error('❌ power.config.json not found.');
  process.exit(1);
}

const env = parseEnv(readFileSync(envPath, 'utf8'));
const cfg = JSON.parse(readFileSync(cfgPath, 'utf8'));

const displayName = env.VITE_APP_DISPLAY_NAME || cfg.appName || 'My Code App';
const environmentId = env.VITE_PP_ENVIRONMENT_ID || cfg.environmentId;

if (!environmentId) {
  console.error('❌ VITE_PP_ENVIRONMENT_ID missing in .env (and environmentId missing in power.config.json).');
  process.exit(1);
}

console.log(`▶ Initializing app "${displayName}" in environment ${environmentId}...`);

const args = [
  'power-apps',
  'init',
  '--display-name', displayName,
  '--environment-id', environmentId,
];

const result = spawnSync('npx', args, { stdio: 'inherit', shell: true });

// Windows libuv assertion errors after success are cosmetic.
if (result.status !== 0 && result.status !== null) {
  console.warn(`⚠ npx exited with status ${result.status}. Check power.config.json for the generated appId before retrying.`);
}

// Best-effort: re-read power.config.json and patch .env with the new appId
try {
  const updated = JSON.parse(readFileSync(cfgPath, 'utf8'));
  if (updated.appId && env.VITE_APP_ID !== updated.appId) {
    const newEnv = readFileSync(envPath, 'utf8').replace(
      /VITE_APP_ID=.*/,
      `VITE_APP_ID=${updated.appId}`,
    );
    writeFileSync(envPath, newEnv);
    console.log(`✓ Patched .env with VITE_APP_ID=${updated.appId}`);
  }
} catch {
  /* skip — user can patch manually */
}
