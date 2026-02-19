# AI Storybook Studio

A toolkit for building print-ready PDF guidebooks using HTML/CSS and PrinceXML, with Playwright-powered screenshot automation for capturing live application walkthroughs.

## Project structure

```
├── build.sh                        # Main build script (images + PDF)
├── books/
│   ├── conga-getting-started/      # Conga API onboarding guide
│   │   ├── book.html               # HTML source (paged media CSS)
│   │   ├── images/                 # Screenshots + logo
│   │   ├── conga-brand-guidelines-prompt.md
│   │   └── generate-images.py      # Gemini image generation (optional)
│   ├── goldilocks/                 # Example children's book
│   └── goldilocks-funny/           # Example variant
└── services/
    └── screenshots/                # Playwright screenshot automation
        ├── capture-auth.mjs        # Step 1: Capture login session
        ├── conga-walkthrough.mjs   # Step 2: Automated walkthrough + screenshots
        ├── take-screenshots.mjs    # Generic URL-based screenshot tool
        ├── conga-shots.json        # Screenshot manifest (URL-based)
        └── auth.json               # Saved browser session (gitignored)
```

## Prerequisites

- **Python 3.8+** with `pymupdf` (`pip install pymupdf`)
- **PrinceXML** for HTML-to-PDF conversion ([princexml.com](https://www.princexml.com/download/) or `brew install prince`)
- **Node.js 18+** for Playwright screenshot automation
- **Gemini API key** (optional, only for AI image generation via `generate-images.py`)

## Quick start: Build a PDF

```bash
# List available books
./build.sh --list

# Build PDF only (skip image generation)
./build.sh conga-getting-started --pdf-only

# Build with AI image generation (requires GEMINI_IMAGE_API_KEY)
./build.sh conga-getting-started
```

The PDF outputs to `books/<book-name>/<book-name>.pdf` and opens automatically on macOS.

## How the books work

Each book is a single `book.html` file using CSS Paged Media:

- **Fixed page size**: 8.5in x 11in with `overflow: hidden` per page
- **CSS variables**: Colors, fonts, and spacing are defined as design tokens in `:root`
- **One `<div class="page">` per page**: Each page is a fixed-size container; content must fit within its bounds
- **PrinceXML** renders the HTML to a print-ready PDF with proper page breaks, headers, and footers

### Adding or editing pages

1. Edit `books/<book-name>/book.html`
2. Each page is a `<div class="page">` with a `<div class="page-content">` inside
3. Keep content within the 9.7in usable height (11in minus 0.65in top/bottom padding)
4. If a page overflows, split it into two pages
5. Rebuild with `./build.sh <book-name> --pdf-only`

## Playwright screenshot workflow

The `services/screenshots/` directory automates capturing screenshots from the live Conga platform for use in the guidebook.

### Step 1: Capture authentication

```bash
cd services/screenshots
npm install

# Opens a browser window for manual login
node capture-auth.mjs https://preview-rls09.congacloud.com/
```

1. A Chromium window opens to the Conga login page
2. Log in manually with your credentials
3. Navigate to the dashboard to confirm you're authenticated
4. Return to the terminal and press **Enter** to save the session
5. Auth state (cookies + localStorage) saves to `auth.json`

> `auth.json` is gitignored. Sessions expire, so you may need to re-capture periodically.

### Step 2: Run the automated walkthrough

```bash
# Headless (default) - captures screenshots without showing browser
node conga-walkthrough.mjs

# Headed mode - watch the browser as it runs
node conga-walkthrough.mjs --headed

# Custom output directory
node conga-walkthrough.mjs --output ../../books/conga-getting-started/images

# Dry run - navigates but skips form filling and saving
node conga-walkthrough.mjs --dry-run
```

The walkthrough script (`conga-walkthrough.mjs`) automates the full Integration User creation flow:

1. Opens the Conga dashboard
2. Navigates to Admin Console
3. Opens the Users page
4. Clicks Add to open the user form
5. Changes User Type from Internal to Integration
6. Fills in required fields (First Name, Last Name, Email, Role)
7. Clicks Save
8. Captures the credentials popup (Client ID and Client Secret)

Screenshots are numbered sequentially (`01-dashboard.png`, `02-admin-console.png`, etc.) and saved to `services/screenshots/output/conga-walkthrough/` by default.

### Step 3: Copy screenshots to the book

```bash
# Copy walkthrough output to the book's images directory
cp services/screenshots/output/conga-walkthrough/*.png books/conga-getting-started/images/
```

Then rebuild the PDF:

```bash
./build.sh conga-getting-started --pdf-only
```

### Alternative: URL-based screenshots

For simpler needs, `take-screenshots.mjs` captures screenshots by navigating directly to URLs:

```bash
# Single URL
node take-screenshots.mjs --url https://preview-rls09.congacloud.com/

# From a config file
node take-screenshots.mjs --config conga-shots.json --output ./output
```

The config file (`conga-shots.json`) defines a list of URLs and options:

```json
[
  {
    "name": "01-dashboard",
    "url": "/",
    "description": "Main dashboard after login",
    "fullPage": false
  }
]
```

## Conga Getting Started guide

The primary book in this repo is a 13-page guide for Conga API onboarding:

| Page | Content |
|------|---------|
| 1 | Cover |
| 2 | Overview and checklist |
| 3 | Step 1: App Launcher and Admin Console |
| 4 | Step 2: Navigate to Users |
| 5 | Step 3: Add an Integration User |
| 6 | Step 3 continued: Fill the form |
| 7 | Step 4: Save and capture credentials |
| 8 | Step 5: Request an access token |
| 9 | Step 5 continued: Call the API |
| 10 | Regional API endpoints (US, EU, AU) |
| 11 | Appendix A: Regenerating secrets |
| 12 | Appendix B: API Connections alternative |
| 13 | Summary |

Brand: Montserrat font, Conga Red (#E53535) / Charcoal (#474542) / Blue Harbor (#48A9C5) palette. See `conga-brand-guidelines-prompt.md` for full brand reference.
