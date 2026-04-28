// Minimal .env parser/serializer that preserves order, comments, and blank lines.

export function parseEnv(text) {
  const env = {};
  Object.defineProperty(env, '__lines', { value: text.split(/\r?\n/), enumerable: false });
  for (const line of env.__lines) {
    const m = line.match(/^([A-Z0-9_]+)=(.*)$/);
    if (m) env[m[1]] = m[2];
  }
  return env;
}

export function serializeEnv(env) {
  const lines = env.__lines ? [...env.__lines] : [];
  const written = new Set();

  for (let i = 0; i < lines.length; i++) {
    const m = lines[i].match(/^([A-Z0-9_]+)=(.*)$/);
    if (m) {
      const key = m[1];
      if (key in env) {
        lines[i] = `${key}=${env[key]}`;
        written.add(key);
      }
    }
  }

  // Append any keys not already present
  for (const key of Object.keys(env)) {
    if (!written.has(key)) lines.push(`${key}=${env[key]}`);
  }

  return lines.join('\n');
}
