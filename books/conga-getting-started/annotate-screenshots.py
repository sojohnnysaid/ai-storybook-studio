#!/usr/bin/env python3
"""
Conga Getting Started - Screenshot Annotator
=============================================
Annotates screenshots with callout boxes, highlights, and arrows
using the Google Gemini image generation API.

Backs up originals to images/raw/ before overwriting.

Usage:
    export GEMINI_IMAGE_API_KEY="your-api-key-here"
    python3 annotate-screenshots.py           # annotate all
    python3 annotate-screenshots.py --force   # re-annotate even if already done
    python3 annotate-screenshots.py --restore # restore originals from raw/

Requires:
    pip install google-genai Pillow
"""

import os
import sys
import time
import shutil
from pathlib import Path

try:
    from google import genai
    from google.genai import types
    from PIL import Image
except ImportError:
    print("ERROR: Required packages not installed.")
    print("Run: pip install google-genai Pillow")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

API_KEY = os.environ.get("GEMINI_IMAGE_API_KEY")
IMAGES_DIR = Path(__file__).parent / "images"
RAW_DIR = IMAGES_DIR / "raw"

# Gemini model that supports image input + image output (editing)
MODEL = os.environ.get("GEMINI_EDIT_MODEL", "gemini-3-pro-image-preview")
DELAY_BETWEEN_REQUESTS = 5  # seconds, respect rate limits

# ---------------------------------------------------------------------------
# Annotation Style (shared across all annotations)
# ---------------------------------------------------------------------------

STYLE = (
    "You are a precise screenshot annotation tool. "
    "Add ONLY the described annotation overlay onto this existing screenshot. "
    "Annotation visual style: "
    "- Rounded-rectangle callout box with solid blue gradient fill (#0052CC to #003D99) "
    "- Subtle drop shadow behind the box "
    "- Thin light border on the box (#4A90D9, 1px) "
    "- White bold sans-serif text inside (like Arial/Helvetica, ~14px equivalent) "
    "- When an arrow is needed: solid blue triangle/arrow pointing from the callout to the target "
    "- For highlight borders: 3px solid #0052CC rounded rectangle drawn around the target element "
    "\n"
    "CRITICAL RULES: "
    "1. Do NOT redraw, regenerate, or alter ANY part of the original screenshot. "
    "2. The output must be the EXACT same screenshot with ONLY the overlay annotations added on top. "
    "3. Preserve the original image dimensions, colors, and content exactly. "
    "4. Keep annotations clean, professional, and minimal. "
)

# ---------------------------------------------------------------------------
# Annotation Manifest
# ---------------------------------------------------------------------------
# Each entry describes one image and what annotation it needs.
# "style" is informational — the instruction does the real work.
#
# Styles:
#   "callout"   — blue box with text + arrow pointing to target
#   "highlight"  — blue border around target element + optional small label
#   "none"       — skip, no annotation needed
# ---------------------------------------------------------------------------

ANNOTATIONS = [
    {
        "filename": "01-dashboard.png",
        "style": "callout",
        "description": "Arrow pointing to Admin Console tile",
        "instruction": (
            "Find the 'Admin Console' tile in the top row of application tiles "
            "(it has a gear/rocket icon and sits between 'Billing Apps' and 'Dev Console'). "
            "Place a blue callout box ABOVE and slightly to the left of it, with white text: "
            "'Click Admin Console'. "
            "Draw a downward-pointing arrow from the bottom of the callout box "
            "directly to the Admin Console tile."
        ),
    },
    {
        "filename": "02-admin-console.png",
        "style": "none",
        "description": "Contextual overview — no annotation needed",
        "instruction": "",
    },
    {
        "filename": "03-users-list.png",
        "style": "callout",
        "description": "Arrow pointing to the Add button",
        "instruction": (
            "Find the blue 'Add' button in the upper-right area of the page "
            "(it's a solid blue button with white text 'Add', next to 'Bulk Import'). "
            "Place a blue callout box ABOVE the button with white text: "
            "'Click Add to create a new user'. "
            "Draw a downward-pointing arrow from the callout to the Add button."
        ),
    },
    {
        "filename": "04-add-user-form.png",
        "style": "highlight",
        "description": "Highlight the User Type dropdown",
        "instruction": (
            "Find the 'User Type' dropdown in the upper-left of the form — "
            "it currently shows the value 'Internal' with an X and dropdown arrow. "
            "Draw a blue highlight border (3px, rounded) around the entire User Type dropdown field. "
            "Place a small blue callout to the RIGHT of the dropdown with white text: "
            "'Change to Integration'. "
            "Do NOT annotate any other fields."
        ),
    },
    {
        "filename": "05-user-type-dropdown.png",
        "style": "highlight",
        "description": "Highlight the Integration option in dropdown",
        "instruction": (
            "The User Type dropdown is open showing two options: "
            "'Internal' (highlighted/selected at top) and 'Integration' (below it). "
            "Draw a blue highlight border (3px, rounded) around ONLY the 'Integration' text/row. "
            "Optionally add a small blue arrow or pointer aimed at 'Integration'. "
            "Do NOT highlight 'Internal'."
        ),
    },
    {
        "filename": "06-user-type-integration.png",
        "style": "none",
        "description": "Shows form after Integration selected — no annotation needed",
        "instruction": "",
    },
    {
        "filename": "07-role-search.png",
        "style": "none",
        "description": "Shows role search results — not used in book",
        "instruction": "",
    },
    {
        "filename": "08-form-filled.png",
        "style": "callout",
        "description": "Arrow pointing to the Save button",
        "instruction": (
            "Find the 'Save' button at the bottom-center of the form "
            "(it's a white button with blue text and blue border, next to 'Cancel'). "
            "Place a blue callout box ABOVE the Save button with white text: "
            "'Click Save to generate credentials'. "
            "Draw a downward-pointing arrow from the callout to the Save button."
        ),
    },
    {
        "filename": "09-credentials-popup.png",
        "style": "highlight",
        "description": "Highlight Client ID, Client Secret fields, and Copy buttons",
        "instruction": (
            "Find the 'Credentials' popup dialog in the center of the screen. "
            "It contains a 'Client ID' field and a 'Client Secret' field, "
            "each with a yellow 'Copy' button to their right. "
            "Draw blue highlight borders (3px, rounded) around: "
            "1. The Client ID input field AND its Copy button (as one group) "
            "2. The Client Secret input field AND its Copy button (as one group) "
            "Place a small blue callout ABOVE the popup with white text: "
            "'Copy both values — the Secret is shown only once!'"
        ),
    },
    {
        "filename": "10-credentials-closeup.png",
        "style": "none",
        "description": "Close-up detail — not used in book",
        "instruction": "",
    },
]

# ---------------------------------------------------------------------------
# Logic
# ---------------------------------------------------------------------------


def restore_originals():
    """Restore original screenshots from raw/ backups."""
    if not RAW_DIR.exists():
        print("No raw/ backup directory found. Nothing to restore.")
        return

    count = 0
    for raw_file in RAW_DIR.glob("*.png"):
        dest = IMAGES_DIR / raw_file.name
        shutil.copy2(raw_file, dest)
        print(f"  Restored: {raw_file.name}")
        count += 1

    print(f"\n  {count} files restored from {RAW_DIR}")


def annotate_images():
    """Annotate screenshots using the Gemini API."""
    if not API_KEY:
        print("ERROR: Set GEMINI_IMAGE_API_KEY environment variable.")
        print("  export GEMINI_IMAGE_API_KEY='your-key-here'")
        sys.exit(1)

    client = genai.Client(api_key=API_KEY)

    # Ensure backup directory exists
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    # Filter to only images that need annotation
    to_annotate = [a for a in ANNOTATIONS if a["style"] != "none"]
    total = len(to_annotate)
    annotated = 0
    skipped = 0
    failed = 0

    force = "--force" in sys.argv

    print(f"\n{'='*60}")
    print(f"  Conga Screenshot Annotator")
    print(f"  Model:   {MODEL}")
    print(f"  Images:  {total} to annotate ({len(ANNOTATIONS) - total} skipped)")
    print(f"  Source:  {IMAGES_DIR}")
    print(f"  Backups: {RAW_DIR}")
    print(f"{'='*60}\n")

    for i, ann in enumerate(to_annotate, 1):
        src_path = IMAGES_DIR / ann["filename"]
        raw_path = RAW_DIR / ann["filename"]

        # Check source exists
        if not src_path.exists():
            print(f"  [{i}/{total}] MISSING: {ann['filename']}")
            skipped += 1
            continue

        # Skip if already annotated (raw backup exists) unless --force
        if raw_path.exists() and not force:
            print(f"  [{i}/{total}] SKIP (done): {ann['filename']}")
            skipped += 1
            continue

        print(f"  [{i}/{total}] {ann['filename']}")
        print(f"           Style: {ann['style']}")
        print(f"           {ann['description']}")

        # Back up original (only if not already backed up)
        if not raw_path.exists():
            shutil.copy2(src_path, raw_path)
            print(f"           Backed up → raw/{ann['filename']}")

        # Always read from the raw original for annotation
        source_for_annotation = raw_path if raw_path.exists() else src_path

        try:
            image = Image.open(str(source_for_annotation))
            prompt = STYLE + "\nSpecific instruction for this image:\n" + ann["instruction"]

            response = client.models.generate_content(
                model=MODEL,
                contents=[image, prompt],
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE", "TEXT"],
                ),
            )

            # Extract annotated image from response
            saved = False
            if response.candidates:
                for part in response.candidates[0].content.parts:
                    if part.inline_data is not None:
                        result_image = part.as_image()
                        result_image.save(str(src_path))
                        size_kb = src_path.stat().st_size / 1024
                        print(f"           SAVED ({size_kb:.0f} KB)")
                        annotated += 1
                        saved = True
                        break

            if not saved:
                print(f"           WARNING: No image in response")
                # Log any text the model returned
                if response.candidates:
                    for part in response.candidates[0].content.parts:
                        if hasattr(part, "text") and part.text:
                            print(f"           Model: {part.text[:200]}")
                    if response.candidates[0].finish_reason:
                        print(f"           Finish: {response.candidates[0].finish_reason}")
                failed += 1

        except Exception as e:
            print(f"           ERROR: {e}")
            failed += 1

        # Rate limit
        if i < total:
            print(f"           Waiting {DELAY_BETWEEN_REQUESTS}s...")
            time.sleep(DELAY_BETWEEN_REQUESTS)

    # Summary
    print(f"\n{'='*60}")
    print(f"  Annotation Complete!")
    print(f"  Annotated: {annotated}")
    print(f"  Skipped:   {skipped}")
    print(f"  Failed:    {failed}")
    print(f"{'='*60}")
    print(f"\n  Originals in: {RAW_DIR}")
    print(f"  To undo:  python3 {Path(__file__).name} --restore\n")

    return failed == 0


if __name__ == "__main__":
    if "--restore" in sys.argv:
        restore_originals()
    else:
        success = annotate_images()
        sys.exit(0 if success else 1)
