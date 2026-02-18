#!/usr/bin/env node
/**
 * Auth Capture Script
 * ===================
 * Opens a browser window for you to manually log in.
 * Once logged in, press Enter in the terminal to save
 * the auth state (cookies, localStorage) to auth.json.
 *
 * Usage:
 *   node capture-auth.mjs <url>
 *   node capture-auth.mjs https://preview-rls09.congacloud.com/
 */

import { chromium } from 'playwright';
import { createInterface } from 'readline';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const AUTH_FILE = resolve(__dirname, 'auth.json');

const url = process.argv[2] || 'https://preview-rls09.congacloud.com/';

async function main() {
  console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log('  Auth Capture - Manual Login');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
  console.log(`  URL:       ${url}`);
  console.log(`  Auth file: ${AUTH_FILE}\n`);

  const browser = await chromium.launch({
    headless: false,
    args: ['--start-maximized'],
  });

  const context = await browser.newContext({
    viewport: null, // Use full window size
  });

  const page = await context.newPage();
  await page.goto(url, { waitUntil: 'networkidle' });

  console.log('  Browser is open. Please log in manually.');
  console.log('  Navigate to the dashboard or desired page.');
  console.log('  When ready, come back here and press ENTER to save auth.\n');

  const rl = createInterface({ input: process.stdin, output: process.stdout });

  await new Promise((resolve) => {
    rl.question('  Press ENTER to save auth state...', () => {
      rl.close();
      resolve();
    });
  });

  // Save storage state (cookies + localStorage)
  await context.storageState({ path: AUTH_FILE });
  console.log(`\n  ✓ Auth saved to ${AUTH_FILE}`);

  await browser.close();
  console.log('  ✓ Browser closed\n');
}

main().catch((err) => {
  console.error('Error:', err);
  process.exit(1);
});
