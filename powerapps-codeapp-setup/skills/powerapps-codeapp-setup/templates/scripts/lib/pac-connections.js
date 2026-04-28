// Wraps `pac connection list --json` and normalizes the output.

import { spawnSync } from 'node:child_process';

export async function listConnections() {
  const result = spawnSync('pac', ['connection', 'list', '--json'], { encoding: 'utf8', shell: true });
  if (result.status !== 0) {
    throw new Error(`pac connection list failed: ${result.stderr || result.stdout}`);
  }

  let data;
  try {
    data = JSON.parse(result.stdout);
  } catch {
    // pac sometimes prefixes status text — find the first { or [ and parse from there
    const idx = result.stdout.search(/[\[\{]/);
    if (idx >= 0) data = JSON.parse(result.stdout.slice(idx));
    else throw new Error('Could not parse pac connection list output');
  }

  // Normalize to { connectionId, displayName, connectorName, status }
  const arr = Array.isArray(data) ? data : data.connections ?? [];
  return arr
    .map((c) => ({
      connectionId: c.connectionId ?? c.ConnectionId ?? c.id ?? '',
      displayName: c.displayName ?? c.DisplayName ?? c.name ?? '',
      connectorName: c.connectorName ?? c.ConnectorName ?? c.apiName ?? '',
      status: c.status ?? c.Status ?? '',
    }))
    .filter((c) => c.connectionId && c.connectorName);
}
