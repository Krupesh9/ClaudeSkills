#!/usr/bin/env node
// Auto-discovers Power Platform connections via `pac connection list`,
// prompts the user to select one per connector, then runs
// `npx power-apps add-data-source` for each list / resource.
// Updates .env with the chosen connection IDs.
//
// Usage: npm run connect

import { spawnSync } from 'node:child_process';
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { parseEnv, serializeEnv } from './lib/env-parser.js';
import { listConnections } from './lib/pac-connections.js';
import { promptSelect } from './lib/prompt.js';
import { CONNECTORS } from './connectors/registry.js';

const envPath = '.env';
if (!existsSync(envPath)) {
  console.error('❌ .env not found.');
  process.exit(1);
}

const env = parseEnv(readFileSync(envPath, 'utf8'));

console.log('▶ Discovering Power Platform connections...');
const allConnections = await listConnections();
if (allConnections.length === 0) {
  console.error('❌ No connections found. Run `pac auth create --environment <ID>` and create connections in make.powerapps.com first.');
  process.exit(1);
}

for (const connector of CONNECTORS) {
  if (!connector.isConfigured(env)) {
    console.log(`⏭  ${connector.name}: not enabled (skipping)`);
    continue;
  }

  console.log(`\n▶ ${connector.name}`);

  const candidates = allConnections.filter((c) => c.connectorName === connector.apiId);
  if (candidates.length === 0) {
    console.warn(`⚠ No ${connector.name} connections found in this environment. Create one in make.powerapps.com → Connections.`);
    continue;
  }

  let chosen;
  if (candidates.length === 1) {
    chosen = candidates[0];
    console.log(`  Auto-selected: ${chosen.displayName} (${chosen.connectionId})`);
  } else {
    const labels = candidates.map((c) => `${c.displayName}  ·  ${c.connectionId}`);
    const idx = await promptSelect(`  Choose ${connector.name} connection:`, labels);
    chosen = candidates[idx];
  }

  // Persist connection ID to .env
  env[connector.envConnectionIdKey] = chosen.connectionId;

  // Wire each resource via `npx power-apps add-data-source`
  const resources = connector.getResources(env);
  const dataset = connector.getDataset(env);
  for (const resource of resources) {
    console.log(`  ▶ Adding data source: ${resource}`);
    const args = connector.buildArgs(chosen.connectionId, dataset, resource);
    const result = spawnSync('npx', args, { stdio: 'inherit', shell: true });
    if (result.status !== 0 && result.status !== null) {
      console.warn(`  ⚠ add-data-source exited with status ${result.status}`);
    }
  }
}

writeFileSync(envPath, serializeEnv(env));
console.log('\n✓ .env updated with connection IDs.');
console.log('  Next: npm run build && npm run push');
