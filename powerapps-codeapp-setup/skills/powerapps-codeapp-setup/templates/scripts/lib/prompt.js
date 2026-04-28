// Tiny readline-based interactive prompt. No external deps.

import readline from 'node:readline/promises';
import { stdin as input, stdout as output } from 'node:process';

export async function promptSelect(question, choices) {
  const rl = readline.createInterface({ input, output });
  console.log(question);
  choices.forEach((c, i) => console.log(`    [${i + 1}] ${c}`));
  while (true) {
    const ans = (await rl.question('  > ')).trim();
    const n = parseInt(ans, 10);
    if (!isNaN(n) && n >= 1 && n <= choices.length) {
      rl.close();
      return n - 1;
    }
    console.log('  ✗ invalid choice — enter a number from the list');
  }
}

export async function promptText(question, defaultValue = '') {
  const rl = readline.createInterface({ input, output });
  const suffix = defaultValue ? ` [${defaultValue}]` : '';
  const ans = (await rl.question(`${question}${suffix}: `)).trim();
  rl.close();
  return ans || defaultValue;
}
