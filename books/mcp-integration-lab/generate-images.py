#!/usr/bin/env python3
"""
MCP Integration Lab - AI Image Generator
==========================================
Generates all illustrations for the lab design document using the
Google Gemini image generation API (gemini-2.5-flash-image model).

Usage:
    export GEMINI_IMAGE_API_KEY="your-api-key-here"
    python3 generate-images.py

Requires:
    pip install google-genai Pillow
"""

import os
import sys
import time
import json
from pathlib import Path

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("ERROR: google-genai package not installed.")
    print("Run: pip install google-genai Pillow")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

API_KEY = os.environ.get("GEMINI_IMAGE_API_KEY")
if not API_KEY:
    print("ERROR: Set GEMINI_IMAGE_API_KEY environment variable.")
    sys.exit(1)

OUTPUT_DIR = Path(__file__).parent / "images"
OUTPUT_DIR.mkdir(exist_ok=True)

MODEL = "gemini-2.5-flash-image"  # Dedicated image generation model
DELAY_BETWEEN_REQUESTS = 6  # seconds, to respect rate limits

# ---------------------------------------------------------------------------
# Style guide - consistent across all illustrations
# ---------------------------------------------------------------------------

STYLE_PREFIX = (
    "Modern technical enterprise illustration in clean vector style with "
    "soft gradients and glowing accent elements. Color palette: deep indigo, "
    "electric cyan, emerald green, warm amber, and cool slate grays on white "
    "or near-white backgrounds. Professional, credible aesthetic suitable for "
    "enterprise technology buyers. Minimal detail, bold shapes, no text or "
    "labels in the image. Subtle depth-of-field effect. "
)

# ---------------------------------------------------------------------------
# Image Manifest
# ---------------------------------------------------------------------------
# Each entry defines one illustration for the document.
# Fields:
#   filename     - output filename in images/
#   prompt       - artistic scene description
#   aspect_ratio - Gemini aspect ratio string
#   resolution   - "1K" or "2K"
#   placement    - notes on where/how image is used in the book layout
# ---------------------------------------------------------------------------

IMAGE_MANIFEST = [
    {
        "filename": "cover.png",
        "prompt": (
            STYLE_PREFIX
            + "A hero illustration showing a three-layer architecture concept: "
            "at the bottom, a row of enterprise system icons (databases, cloud "
            "services, document stores) rendered as glowing indigo cubes. In the "
            "middle layer, a radiant cyan hexagonal node representing a protocol "
            "gateway with connection lines radiating outward. At the top, an "
            "abstract AI agent represented as a luminous sphere with neural "
            "network patterns. Flowing data streams connect all three layers "
            "with particle trails in cyan and emerald. Dark slate background "
            "with subtle grid lines. The composition conveys connectivity, "
            "intelligence, and enterprise scale."
        ),
        "aspect_ratio": "4:5",
        "resolution": "2K",
        "placement": "Cover page hero image behind gradient overlay.",
    },
    {
        "filename": "architecture_diagram.png",
        "prompt": (
            STYLE_PREFIX
            + "A detailed technical architecture visualization showing four "
            "connected nodes arranged left to right: (1) a glowing user/agent "
            "icon on the left with neural network patterns, (2) a client node "
            "with bidirectional arrows, (3) a server node depicted as a "
            "hexagonal hub with tool icons orbiting it, (4) an enterprise "
            "API endpoint on the right shown as a secure vault with data "
            "streams flowing out. Connecting lines between nodes pulse with "
            "cyan energy. Each node sits on a subtle platform. Clean white "
            "background with soft shadow beneath each element."
        ),
        "aspect_ratio": "3:2",
        "resolution": "2K",
        "placement": "Architecture page, below the CSS arch-diagram.",
    },
    {
        "filename": "flow_overview.png",
        "prompt": (
            STYLE_PREFIX
            + "A visual roadmap showing seven connected waypoints arranged in "
            "a gentle S-curve path from bottom-left to top-right. Each waypoint "
            "is a glowing circle with a different accent color (indigo, indigo, "
            "cyan, cyan, emerald, amber, rose) connected by a luminous path. "
            "Small icon silhouettes near each waypoint suggest activities: "
            "a speech bubble, a cloud, an API endpoint, a gear/wrench, a "
            "checkmark, a magnifying glass, and a presentation screen. "
            "Soft particle effects along the path. Clean minimal background."
        ),
        "aspect_ratio": "3:2",
        "resolution": "2K",
        "placement": "Lab flow page, visual complement to the timeline.",
    },
    {
        "filename": "customer_story.png",
        "prompt": (
            STYLE_PREFIX
            + "An illustration of enterprise systems connecting to an AI agent: "
            "multiple enterprise icons (a search magnifying glass, a ticket, "
            "a document folder, a database cylinder) arranged in a semicircle "
            "on the left side, each emitting a thin glowing line that converges "
            "into a single bright protocol node in the center, which then "
            "connects to a luminous AI brain icon on the right. The convergence "
            "point glows brightest, suggesting standardization. Soft indigo "
            "and cyan color scheme on a light background."
        ),
        "aspect_ratio": "3:2",
        "resolution": "2K",
        "placement": "Section 1: Intro and customer story page.",
    },
    {
        "filename": "cloud_setup.png",
        "prompt": (
            STYLE_PREFIX
            + "A cloud computing environment illustration: a stylized terminal "
            "window floating in space with a command prompt cursor blinking. "
            "Behind it, abstract cloud infrastructure shapes (server racks "
            "rendered as glowing rectangles, a Lambda function icon as a "
            "small glowing cube). Connection lines flow between components. "
            "The scene suggests a clean, ready-to-use development environment. "
            "Amber and indigo accent colors. Minimal, professional."
        ),
        "aspect_ratio": "3:2",
        "resolution": "2K",
        "placement": "Section 2: Cloud environment setup page.",
    },
    {
        "filename": "search_api.png",
        "prompt": (
            STYLE_PREFIX
            + "A mock API endpoint illustration: a glowing endpoint node "
            "receives a search query (represented as a small magnifying glass "
            "icon) and returns structured data (represented as organized rows "
            "of glowing data blocks flowing outward). Each data block has "
            "subtle emerald and cyan accents suggesting metadata: titles, "
            "scores, permissions. The data flows in an organized stream "
            "from right to left. Clean background with soft grid lines."
        ),
        "aspect_ratio": "3:2",
        "resolution": "2K",
        "placement": "Section 3: Mock search API deployment page.",
    },
    {
        "filename": "mcp_server_wiring.png",
        "prompt": (
            STYLE_PREFIX
            + "A server wiring illustration: a central hexagonal server node "
            "with a tool icon (wrench) inside it. From the top, a schema "
            "definition floats as an abstract structured document. From the "
            "left, a stdio transport pipe connects as a glowing tube. From "
            "the right, an HTTPS connection reaches toward an API endpoint. "
            "The server node pulses with cyan energy. Small gear icons orbit "
            "the server suggesting configuration and tooling. Clean minimal "
            "composition on light background."
        ),
        "aspect_ratio": "3:2",
        "resolution": "2K",
        "placement": "Section 4: MCP server wiring page.",
    },
    {
        "filename": "validation_flow.png",
        "prompt": (
            STYLE_PREFIX
            + "An end-to-end validation illustration: on the left, a query "
            "icon (speech bubble with question mark) sends a request through "
            "a chain of three processing nodes (agent, protocol, API). "
            "On the right, the output emerges as a structured answer with "
            "small citation markers (tiny document icons) attached. A green "
            "checkmark glows above the final output. The flow moves cleanly "
            "left to right with emerald accents on the validation elements. "
            "Professional and reassuring composition."
        ),
        "aspect_ratio": "3:2",
        "resolution": "2K",
        "placement": "Section 5: End-to-end validation page.",
    },
    {
        "filename": "troubleshooting_tree.png",
        "prompt": (
            STYLE_PREFIX
            + "A fault isolation triage illustration: three layers stacked "
            "vertically (client at top in indigo, server in middle in cyan, "
            "endpoint at bottom in emerald). A diagnostic probe (magnifying "
            "glass icon) hovers over the middle layer. Red warning indicators "
            "pulse on one layer while the others show green status. Arrows "
            "suggest the diagnostic flow: check each layer in sequence. "
            "The composition conveys systematic debugging methodology. "
            "Clean, professional, with amber warning accents."
        ),
        "aspect_ratio": "3:2",
        "resolution": "2K",
        "placement": "Section 6: Troubleshooting and debugging page.",
    },
    {
        "filename": "positioning_narrative.png",
        "prompt": (
            STYLE_PREFIX
            + "A presentation/demo scene illustration: an abstract figure "
            "presenting to a small audience, with a large screen behind them "
            "showing the three-layer architecture diagram. Glowing connection "
            "lines radiate from the screen. The audience figures lean forward "
            "with interest. The scene conveys confidence, expertise, and "
            "customer engagement. Indigo and cyan dominate with warm amber "
            "highlights suggesting human warmth. Professional conference "
            "or meeting room aesthetic."
        ),
        "aspect_ratio": "3:2",
        "resolution": "2K",
        "placement": "Section 7: Wrap-up and customer positioning page.",
    },
    {
        "filename": "grounding_illustration.png",
        "prompt": (
            STYLE_PREFIX
            + "A RAG (retrieve-then-generate) pattern illustration: on the "
            "left, a stack of authoritative documents with small emerald "
            "checkmarks. In the center, a retrieval mechanism (funnel or "
            "filter shape) selects relevant documents. On the right, a "
            "generative AI node produces an answer with citation links "
            "connecting back to the source documents via thin glowing lines. "
            "The composition emphasizes the grounding chain: sources first, "
            "generation second. Cyan and emerald color scheme."
        ),
        "aspect_ratio": "3:2",
        "resolution": "2K",
        "placement": "Cheat sheet page, illustrating the grounding concept.",
    },
    {
        "filename": "tool_discovery.png",
        "prompt": (
            STYLE_PREFIX
            + "A tool discovery illustration: an AI agent node on the left "
            "sends out a discovery beam (radar-like concentric rings) toward "
            "a server node on the right. The server responds by revealing "
            "multiple tool icons (wrench, magnifying glass, document) that "
            "float upward with their schemas shown as small structured cards. "
            "The agent's beam illuminates available tools dynamically. "
            "Cyan discovery rings against a clean background. The composition "
            "conveys dynamic, runtime capability discovery."
        ),
        "aspect_ratio": "3:2",
        "resolution": "2K",
        "placement": "Cheat sheet page, illustrating tool discovery concept.",
    },
    {
        "filename": "background_texture.png",
        "prompt": (
            STYLE_PREFIX
            + "A subtle abstract background texture: a very faint grid pattern "
            "with occasional glowing nodes at intersections. Soft indigo and "
            "cyan dots connected by barely-visible lines, creating a circuit "
            "board or constellation effect. Extremely minimal and light, "
            "suitable as a low-opacity background overlay. Nearly white "
            "with just hints of the tech pattern. No focal point, purely "
            "atmospheric."
        ),
        "aspect_ratio": "4:5",
        "resolution": "1K",
        "placement": "Subtle tech-pattern for optional page backgrounds.",
    },
]

# ---------------------------------------------------------------------------
# Generation Logic
# ---------------------------------------------------------------------------


def generate_images():
    """Generate all illustrations using the Gemini API."""
    client = genai.Client(api_key=API_KEY)

    total = len(IMAGE_MANIFEST)
    generated = 0
    skipped = 0
    failed = 0

    print(f"\n{'='*60}")
    print(f"  MCP Integration Lab - Image Generator")
    print(f"  Model: {MODEL}")
    print(f"  Images to generate: {total}")
    print(f"  Output directory: {OUTPUT_DIR}")
    print(f"{'='*60}\n")

    for i, img in enumerate(IMAGE_MANIFEST, 1):
        filepath = OUTPUT_DIR / img["filename"]

        # Skip if already generated
        if filepath.exists() and filepath.stat().st_size > 0:
            print(f"[{i}/{total}] SKIP (exists): {img['filename']}")
            skipped += 1
            continue

        print(f"[{i}/{total}] Generating: {img['filename']}")
        print(f"         Aspect: {img['aspect_ratio']}  Resolution: {img['resolution']}")
        print(f"         Placement: {img['placement'][:60]}...")

        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=img["prompt"],
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE"],
                    image_config=types.ImageConfig(
                        aspect_ratio=img["aspect_ratio"],
                    ),
                ),
            )

            # Extract and save image
            saved = False
            if response.candidates:
                for part in response.candidates[0].content.parts:
                    if part.inline_data is not None:
                        image = part.as_image()
                        image.save(str(filepath))
                        size_kb = filepath.stat().st_size / 1024
                        print(f"         SAVED: {filepath.name} ({size_kb:.0f} KB)")
                        generated += 1
                        saved = True
                        break

            if not saved:
                print(f"         WARNING: No image data in response")
                # Check for safety filter blocks
                if response.candidates and response.candidates[0].finish_reason:
                    print(f"         Finish reason: {response.candidates[0].finish_reason}")
                failed += 1

        except Exception as e:
            print(f"         ERROR: {e}")
            failed += 1

        # Rate limit delay (skip after last image)
        if i < total:
            print(f"         Waiting {DELAY_BETWEEN_REQUESTS}s (rate limit)...")
            time.sleep(DELAY_BETWEEN_REQUESTS)

    # Summary
    print(f"\n{'='*60}")
    print(f"  Generation Complete!")
    print(f"  Generated: {generated}")
    print(f"  Skipped:   {skipped}")
    print(f"  Failed:    {failed}")
    print(f"  Total:     {total}")
    print(f"{'='*60}\n")

    # Write manifest for reference
    manifest_path = OUTPUT_DIR / "manifest.json"
    manifest_data = []
    for img in IMAGE_MANIFEST:
        manifest_data.append({
            "filename": img["filename"],
            "aspect_ratio": img["aspect_ratio"],
            "resolution": img["resolution"],
            "placement": img["placement"],
            "prompt": img["prompt"],
            "exists": (OUTPUT_DIR / img["filename"]).exists(),
        })
    with open(manifest_path, "w") as f:
        json.dump(manifest_data, f, indent=2)
    print(f"Manifest written to {manifest_path}")

    return failed == 0


if __name__ == "__main__":
    success = generate_images()
    sys.exit(0 if success else 1)
