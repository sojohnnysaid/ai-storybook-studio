#!/usr/bin/env node
/**
 * Conga Integration User Walkthrough
 * ====================================
 * Creates an Integration User on the Conga Advantage Platform and captures
 * screenshots at each step for the "Getting Started with APIs" guidebook.
 *
 * Usage:
 *   node conga-walkthrough.mjs [--headed] [--output <dir>] [--dry-run]
 */

import { chromium } from 'playwright';
import { existsSync, mkdirSync } from 'fs';
import { resolve, dirname, join } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const AUTH_FILE = resolve(__dirname, 'auth.json');
const BASE_URL = 'https://preview-rls09.congacloud.com';
const VIEWPORT = { width: 1440, height: 900 };

const args = process.argv.slice(2);
const headed = args.includes('--headed');
const dryRun = args.includes('--dry-run');
const outputIdx = args.indexOf('--output');
const OUTPUT_DIR = outputIdx !== -1
  ? resolve(args[outputIdx + 1])
  : resolve(__dirname, 'output', 'conga-walkthrough');

let stepNum = 0;

async function shot(page, name, description) {
  stepNum++;
  const filename = `${String(stepNum).padStart(2, '0')}-${name}.png`;
  const filepath = join(OUTPUT_DIR, filename);
  await page.screenshot({ path: filepath, type: 'png' });
  console.log(`  ${stepNum}. ✓ ${description}`);
  console.log(`     → ${filepath}`);
  return filepath;
}

async function wait(page, ms = 3000) {
  await page.waitForLoadState('networkidle').catch(() => {});
  await page.waitForTimeout(ms);
}

async function main() {
  console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log('  Conga Integration User Walkthrough');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

  if (!existsSync(AUTH_FILE)) {
    console.error('  ✗ Auth file not found');
    process.exit(1);
  }

  mkdirSync(OUTPUT_DIR, { recursive: true });
  console.log(`  Output: ${OUTPUT_DIR}\n`);

  const browser = await chromium.launch({ headless: !headed });
  const context = await browser.newContext({
    storageState: AUTH_FILE,
    viewport: VIEWPORT,
  });
  const page = await context.newPage();

  try {
    // ───── 1. Dashboard ─────
    console.log('  [1] Dashboard...');
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await wait(page, 4000);
    await shot(page, 'dashboard', 'Dashboard - Launch your Conga Experience');

    // ───── 2. Admin Console ─────
    console.log('\n  [2] Admin Console...');
    await page.locator('text=Admin Console').first().click();
    await wait(page, 4000);
    await shot(page, 'admin-console', 'Admin Console - Platform Administration');

    // ───── 3. Users ─────
    console.log('\n  [3] Users...');
    // Click the Users tile/link - use the last match since sidebar labels
    // may have truncated or repeated text
    const usersLinks = page.getByText('Users');
    const count = await usersLinks.count();
    console.log(`    Found ${count} "Users" elements`);
    // Click the last one (should be the tile, not the sidebar icon)
    await usersLinks.nth(count - 1).click();
    await wait(page, 4000);
    await shot(page, 'users-list', 'User Management - Users list');

    // ───── 4. Add User ─────
    console.log('\n  [4] Add button...');
    await page.getByRole('button', { name: 'Add' }).click();
    await wait(page, 3000);
    await shot(page, 'add-user-form', 'User Details form (default: Internal)');

    // ───── 5. Change User Type to Integration ─────
    console.log('\n  [5] User Type → Integration...');
    // The User Type is a custom dropdown (cc-select) wrapping a hidden <select>.
    // The visible part shows "Internal" in a span/div with X and ▼ buttons.
    // We need to click the visible dropdown trigger, NOT the hidden <option>.

    // The custom dropdown (cc-select) wraps a hidden <select>.
    // Click the dropdown arrow to open, then click "Integration" by coordinates.
    const userTypeLabel = page.locator('text=User Type').first();
    const labelBox = await userTypeLabel.boundingBox();
    if (labelBox) {
      // Click the dropdown arrow (▼) - it's at the right side of the dropdown
      await page.mouse.click(labelBox.x + 370, labelBox.y + 40);
      await page.waitForTimeout(800);
    }

    // Screenshot with dropdown open
    await shot(page, 'user-type-dropdown', 'User Type dropdown showing options');

    // Click "Integration" - it's the second item in the dropdown, below "Internal"
    // "Internal" is at roughly labelBox.y + 70, "Integration" at labelBox.y + 105
    if (labelBox) {
      await page.mouse.click(labelBox.x + 180, labelBox.y + 108);
      console.log('    ✓ Clicked Integration option');
    }
    await page.waitForTimeout(1000);
    await shot(page, 'user-type-integration', 'User Type set to Integration');

    // ───── 6. Fill form ─────
    console.log('\n  [6] Filling form...');

    if (dryRun) {
      console.log('    [DRY RUN] Skipping form fill');
    } else {
      // Playwright identified the correct selectors via Shadow DOM piercing:
      //   getByRole('textbox', { name: '* First Name' })
      // The cc-input-field > cc-input > input chain all share the same ID.
      // getByRole targets the actual <input> element correctly.

      // Integration user form has: First Name, Last Name, Email, Role (required)
      // No Username or External Id fields for Integration type

      await page.getByRole('textbox', { name: '* First Name' }).fill('API');
      console.log('    ✓ First Name = API');

      await page.getByRole('textbox', { name: '* Last Name' }).fill('TestBot');
      console.log('    ✓ Last Name = TestBot');

      await page.getByRole('textbox', { name: '* Email' }).fill('api-testbot@example.com');
      console.log('    ✓ Email = api-testbot@example.com');

      // Role - cc-sl-input web component with search functionality
      // Can't use fill() on the custom element - click it and type instead
      const roleSearch = page.locator('cc-sl-input[name="Role"]').first();
      if (await roleSearch.isVisible({ timeout: 2000 }).catch(() => false)) {
        await roleSearch.click();
        await page.waitForTimeout(300);
        await page.keyboard.type('Admin');
        console.log('    Searching for Role "Admin"...');
        await page.waitForTimeout(3000);

        // Screenshot the role search results
        await shot(page, 'role-search', 'Role search results for "Admin"');

        // Click "Admin" from the results list
        // The results are custom elements - use getByText for the exact "Admin" match
        // but be careful since "Admin" appears in many places
        let roleSelected = false;

        // Try clicking by exact text match - the "Admin" option near bottom of list
        const adminOptions = page.getByText('Admin', { exact: true });
        const adminCount = await adminOptions.count();
        console.log(`    Found ${adminCount} "Admin" text matches`);
        // Click the last visible "Admin" text that's in the dropdown area
        for (let i = adminCount - 1; i >= 0; i--) {
          const opt = adminOptions.nth(i);
          const box = await opt.boundingBox().catch(() => null);
          // The role dropdown should be below the Role label and inside the form
          if (box && box.y > 400 && box.x < 700) {
            await opt.click();
            roleSelected = true;
            console.log(`    ✓ Role = Admin (match ${i})`);
            break;
          }
        }

        if (!roleSelected) {
          // Fallback: click by coordinates relative to the role search field
          const searchBox = await roleSearch.boundingBox();
          if (searchBox) {
            // "Admin" is near the bottom of the 9-result list
            // Each item is roughly 35px tall, "Admin" is item 8 of 9
            await page.mouse.click(searchBox.x + 100, searchBox.y + 35 * 8);
            console.log('    ✓ Role clicked by coordinates');
            roleSelected = true;
          }
        }
      } else {
        console.log('    ⚠ Role search component not found');
      }

      await page.waitForTimeout(500);
      await shot(page, 'form-filled', 'Form filled with test Integration user');

      // ───── 7. Save ─────
      console.log('\n  [7] Saving...');
      const saveBtn = page.getByRole('button', { name: 'Save' });
      const saveEnabled = await saveBtn.isEnabled({ timeout: 2000 }).catch(() => false);
      if (!saveEnabled) {
        console.log('    ⚠ Save button is disabled - required fields may be missing');
        await shot(page, 'save-disabled', 'Save disabled - check required fields');
      }
      await saveBtn.click({ force: true, timeout: 5000 }).catch(() => {
        console.log('    ⚠ Force click on Save');
      });
      console.log('    ✓ Clicked Save');
      await wait(page, 5000);
      await shot(page, 'after-save', 'After Save');

      // Check for credentials popup
      const credPopup = page.locator('[role="dialog"], [class*="modal"], [class*="dialog"], [class*="popup"]').first();
      if (await credPopup.isVisible({ timeout: 3000 }).catch(() => false)) {
        await credPopup.screenshot({
          path: join(OUTPUT_DIR, `${String(stepNum + 1).padStart(2, '0')}-credentials-popup.png`),
          type: 'png',
        });
        stepNum++;
        console.log(`  ${stepNum}. ✓ Credentials popup (Client ID & Secret)`);
      }

      // Take one more full page screenshot to capture any error/success messages
      await page.waitForTimeout(1000);
      await shot(page, 'final-state', 'Final page state');
    }

  } catch (err) {
    console.error(`\n  ✗ Error: ${err.message}`);
    await shot(page, 'error', 'Error state').catch(() => {});
  }

  await browser.close();

  console.log(`\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
  console.log(`  Done! ${stepNum} screenshots captured`);
  console.log(`  Output: ${OUTPUT_DIR}`);
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
}

main().catch((err) => {
  console.error('Fatal error:', err);
  process.exit(1);
});
