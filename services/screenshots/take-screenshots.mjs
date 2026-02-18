#!/usr/bin/env node
/**
 * Screenshot Service
 * ==================
 * Takes screenshots of authenticated web pages using saved auth state.
 * Designed for the Conga Advantage Platform (Shadow DOM heavy).
 *
 * Usage:
 *   node take-screenshots.mjs                        # Run all defined shots
 *   node take-screenshots.mjs --url <url>            # Single URL screenshot
 *   node take-screenshots.mjs --config shots.json    # From config file
 *
 * Requires auth.json (run capture-auth.mjs first)
 */

import { chromium } from 'playwright';
import { existsSync, readFileSync, mkdirSync } from 'fs';
import { resolve, dirname, join } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const AUTH_FILE = resolve(__dirname, 'auth.json');
const DEFAULT_OUTPUT_DIR = resolve(__dirname, 'output');

// ─────────────────────────────────────────────────────
// Configuration
// ─────────────────────────────────────────────────────

const BASE_URL = 'https://preview-rls09.congacloud.com';

const VIEWPORT = { width: 1440, height: 900 };

// Default screenshot manifest - customize per book
const DEFAULT_SHOTS = [
  {
    name: 'dashboard',
    url: '/',
    description: 'Main dashboard / home page',
    fullPage: false,
  },
  {
    name: 'admin-settings',
    url: '/admin',
    description: 'Admin settings page',
    fullPage: false,
  },
];

// ─────────────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────────────

function parseArgs() {
  const args = process.argv.slice(2);
  const config = {
    url: null,
    configFile: null,
    outputDir: DEFAULT_OUTPUT_DIR,
    fullPage: false,
    waitFor: null,
  };

  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--url':
        config.url = args[++i];
        break;
      case '--config':
        config.configFile = args[++i];
        break;
      case '--output':
        config.outputDir = resolve(args[++i]);
        break;
      case '--full-page':
        config.fullPage = true;
        break;
      case '--wait-for':
        config.waitFor = args[++i];
        break;
    }
  }

  return config;
}

async function waitForPageReady(page, options = {}) {
  // Wait for network to settle
  await page.waitForLoadState('networkidle').catch(() => {});

  // Extra wait for Shadow DOM components to render
  await page.waitForTimeout(2000);

  // If a specific selector is requested, wait for it
  if (options.waitFor) {
    await page.waitForSelector(options.waitFor, { timeout: 10000 }).catch(() => {
      console.log(`    Warning: waitFor selector "${options.waitFor}" not found`);
    });
  }
}

async function takeScreenshot(page, shot, outputDir) {
  const url = shot.url.startsWith('http') ? shot.url : `${BASE_URL}${shot.url}`;
  const filename = `${shot.name}.png`;
  const filepath = join(outputDir, filename);

  console.log(`  → ${shot.name}`);
  console.log(`    URL: ${url}`);

  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
  await waitForPageReady(page, shot);

  // Take the screenshot
  const screenshotOptions = {
    path: filepath,
    type: 'png',
    fullPage: shot.fullPage || false,
  };

  // Element-specific screenshot
  if (shot.selector) {
    const element = page.locator(shot.selector).first();
    await element.screenshot({ path: filepath, type: 'png' });
  }
  // Clip region screenshot
  else if (shot.clip) {
    screenshotOptions.clip = shot.clip;
    await page.screenshot(screenshotOptions);
  }
  // Full or viewport screenshot
  else {
    await page.screenshot(screenshotOptions);
  }

  console.log(`    ✓ Saved: ${filepath}`);
  return filepath;
}

// ─────────────────────────────────────────────────────
// Main
// ─────────────────────────────────────────────────────

async function main() {
  console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log('  Screenshot Service');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

  // Check auth file
  if (!existsSync(AUTH_FILE)) {
    console.error('  ✗ Auth file not found:', AUTH_FILE);
    console.error('  → Run: node capture-auth.mjs <url>');
    process.exit(1);
  }
  console.log('  ✓ Auth file found');

  const config = parseArgs();

  // Ensure output directory exists
  mkdirSync(config.outputDir, { recursive: true });
  console.log(`  Output: ${config.outputDir}\n`);

  // Determine shots to take
  let shots;
  if (config.url) {
    // Single URL mode
    const name = config.url
      .replace(BASE_URL, '')
      .replace(/^\//, '')
      .replace(/\//g, '-') || 'page';
    shots = [{
      name,
      url: config.url,
      description: `Screenshot of ${config.url}`,
      fullPage: config.fullPage,
      waitFor: config.waitFor,
    }];
  } else if (config.configFile) {
    // Config file mode
    shots = JSON.parse(readFileSync(config.configFile, 'utf-8'));
  } else {
    // Default shots
    shots = DEFAULT_SHOTS;
  }

  console.log(`  Taking ${shots.length} screenshot(s)...\n`);

  // Launch browser with auth
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    storageState: AUTH_FILE,
    viewport: VIEWPORT,
  });
  const page = await context.newPage();

  const results = [];
  for (const shot of shots) {
    try {
      const filepath = await takeScreenshot(page, shot, config.outputDir);
      results.push({ ...shot, filepath, success: true });
    } catch (err) {
      console.log(`    ✗ Error: ${err.message}`);
      results.push({ ...shot, success: false, error: err.message });
    }
  }

  await browser.close();

  // Summary
  const succeeded = results.filter((r) => r.success).length;
  const failed = results.filter((r) => !r.success).length;
  console.log(`\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
  console.log(`  Done! ${succeeded} succeeded, ${failed} failed`);
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
}

main().catch((err) => {
  console.error('Fatal error:', err);
  process.exit(1);
});
