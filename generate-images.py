#!/usr/bin/env python3
"""
Goldilocks and the Three Bears - AI Image Generator
====================================================
Generates all illustrations for the children's book using the
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
    "Children's book illustration in warm watercolor style with soft edges, "
    "golden light, and a cozy storybook aesthetic. "
    "Characters have friendly rounded features and expressive eyes. "
    "Color palette: warm honey gold, forest green, soft cream, rustic brown, "
    "sky blue, and rose pink. "
    "Style inspired by classic picture books like Beatrix Potter meets "
    "modern Pixar warmth. "
)

# ---------------------------------------------------------------------------
# Image Manifest
# ---------------------------------------------------------------------------
# Each entry defines one illustration for the book.
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
            + "A magical book cover scene: a little girl with golden curly hair "
            "wearing a blue dress stands before a charming thatched-roof cottage "
            "nestled in an enchanted forest. The cottage has round windows glowing "
            "with warm amber light. Tall oak trees frame the scene, with dappled "
            "sunlight filtering through leaves. Wildflowers carpet the foreground. "
            "Three bear silhouettes are subtly visible in an upstairs window. "
            "Butterflies and fireflies add sparkle. The mood is inviting and "
            "full of wonder."
        ),
        "aspect_ratio": "4:5",
        "resolution": "2K",
        "placement": "Full bleed cover page. Image fills entire 8.5x11 page with title overlaid.",
    },
    {
        "filename": "title_vignette.png",
        "prompt": (
            STYLE_PREFIX
            + "A small oval vignette illustration of a peaceful forest clearing "
            "with three wooden bowls on a tree stump, steam rising gently from "
            "the porridge inside. Wildflowers surround the stump. Soft morning "
            "light streams through birch trees. A winding path leads away into "
            "a misty forest. Simple, elegant composition suitable for a title page."
        ),
        "aspect_ratio": "1:1",
        "resolution": "1K",
        "placement": "Centered on title page below the book title, roughly 4x4 inches.",
    },
    {
        "filename": "bear_family.png",
        "prompt": (
            STYLE_PREFIX
            + "A loving bear family portrait: Papa Bear is large and sturdy "
            "wearing a green vest, Mama Bear is medium-sized and graceful "
            "wearing a floral apron, and Baby Bear is small and adorable "
            "wearing a red scarf. They stand together in front of their cozy "
            "cottage surrounded by a garden with sunflowers and a white picket "
            "fence. Papa Bear has his arm around Mama Bear, and Baby Bear hugs "
            "a stuffed bunny. Warm golden hour lighting."
        ),
        "aspect_ratio": "3:4",
        "resolution": "2K",
        "placement": "Pages 3-4 spread. Large image on right page, text wraps on left.",
    },
    {
        "filename": "cottage_interior.png",
        "prompt": (
            STYLE_PREFIX
            + "Interior of a cozy bear cottage kitchen: a rustic wooden table "
            "with three chairs of different sizes (large, medium, tiny). "
            "Three steaming bowls of porridge sit on the table. The kitchen has "
            "exposed wooden beams, a stone fireplace with a crackling fire, "
            "copper pots hanging on the wall, a cuckoo clock, and checkered "
            "curtains on round windows. Honey jars line a shelf. Warm, inviting "
            "amber lighting fills the room."
        ),
        "aspect_ratio": "3:2",
        "resolution": "2K",
        "placement": "Pages 5-6. Full-width image spanning top half of spread.",
    },
    {
        "filename": "bears_walking.png",
        "prompt": (
            STYLE_PREFIX
            + "Three bears walking along a winding forest path on a beautiful "
            "morning. Papa Bear leads the way with a walking stick, Mama Bear "
            "carries a basket of wildflowers, and Baby Bear skips along behind "
            "chasing a butterfly. The forest is lush with tall ferns, moss-covered "
            "rocks, and shafts of golden sunlight. A small stream runs alongside "
            "the path. Birds sing from the branches above. Peaceful, adventurous mood."
        ),
        "aspect_ratio": "3:2",
        "resolution": "2K",
        "placement": "Page 6. Landscape image with text above and below.",
    },
    {
        "filename": "goldilocks_forest.png",
        "prompt": (
            STYLE_PREFIX
            + "A curious little girl with bouncy golden curls and a blue dress "
            "with a white pinafore walks through an enchanted forest. She looks "
            "wide-eyed with wonder at the tall trees around her. Sunbeams create "
            "a natural spotlight on her. The forest floor is carpeted with "
            "bluebells and ferns. A tiny rabbit watches from behind a mushroom. "
            "The path ahead curves toward a distant cottage with smoke curling "
            "from its chimney."
        ),
        "aspect_ratio": "4:5",
        "resolution": "2K",
        "placement": "Page 7. Portrait image on left side, text wraps around right.",
    },
    {
        "filename": "tasting_porridge.png",
        "prompt": (
            STYLE_PREFIX
            + "Goldilocks sits at a rustic wooden table tasting porridge from "
            "a tiny blue bowl with a delighted expression. Two other bowls "
            "(one large, one medium) sit nearby - the large one steams heavily "
            "and the medium one has icicle-like frost effects to show it's cold. "
            "Goldilocks holds a wooden spoon and her eyes are closed in bliss. "
            "The cozy kitchen surrounds her with warm firelight. A cat sleeps "
            "by the hearth. Honey drips from a jar on the table."
        ),
        "aspect_ratio": "4:5",
        "resolution": "2K",
        "placement": "Pages 8-9. Large central image with text panels on sides.",
    },
    {
        "filename": "broken_chair.png",
        "prompt": (
            STYLE_PREFIX
            + "A comical scene: Goldilocks sits on a tiny wooden chair that is "
            "cracking and splintering beneath her. Her expression is one of "
            "surprise with arms flailing. Wood pieces fly in all directions. "
            "Two other chairs nearby - one enormous and one medium - are intact. "
            "The living room has a braided rug, a bookshelf with tiny books, "
            "and family portraits of bears on the wall. A toy bear has tumbled "
            "off a shelf from the commotion. Dynamic, funny composition."
        ),
        "aspect_ratio": "1:1",
        "resolution": "2K",
        "placement": "Page 10. Square image with rounded SVG mask, text wraps around.",
    },
    {
        "filename": "sleeping_goldilocks.png",
        "prompt": (
            STYLE_PREFIX
            + "Goldilocks peacefully asleep in a tiny wooden bed with a "
            "patchwork quilt in soft pastels. Her golden curls spread across "
            "a small pillow. Moonlight streams through a round window casting "
            "a gentle blue glow. The bedroom has three beds of different sizes - "
            "she's in the smallest. A teddy bear has been knocked to the floor. "
            "Stars twinkle outside the window. Fireflies glow softly. "
            "The mood is dreamy, serene, and magical."
        ),
        "aspect_ratio": "3:2",
        "resolution": "2K",
        "placement": "Pages 11-12. Wide image across full spread, text overlaid in semi-transparent box.",
    },
    {
        "filename": "bears_return.png",
        "prompt": (
            STYLE_PREFIX
            + "Three bears standing in their kitchen doorway looking shocked "
            "and confused. Papa Bear points at his empty porridge bowl with wide "
            "eyes, Mama Bear covers her mouth in surprise, and Baby Bear peeks "
            "out from behind Mama with worried eyes. The kitchen shows signs of "
            "disturbance - a spoon on the floor, a chair tipped over. "
            "Dramatic lighting from the open front door creates long shadows. "
            "The mood is comedic surprise."
        ),
        "aspect_ratio": "4:5",
        "resolution": "2K",
        "placement": "Page 13. Portrait image with dialogue bubbles positioned around it.",
    },
    {
        "filename": "bears_find_goldilocks.png",
        "prompt": (
            STYLE_PREFIX
            + "The dramatic discovery scene: three bears peer over the edge of "
            "Baby Bear's tiny bed where Goldilocks is sleeping. Papa Bear leans "
            "in with a bewildered expression, Mama Bear looks concerned and "
            "gentle, and Baby Bear is wide-eyed with surprise, pointing at the "
            "sleeping girl. The room is dimly lit with moonlight. A nightlight "
            "shaped like a star casts soft patterns on the wall. "
            "Tension mixed with humor and tenderness."
        ),
        "aspect_ratio": "4:5",
        "resolution": "2K",
        "placement": "Pages 14-15. Full page image on right, text on left page.",
    },
    {
        "filename": "goldilocks_running.png",
        "prompt": (
            STYLE_PREFIX
            + "Goldilocks running through the forest with a startled but "
            "exhilarated expression, her golden curls streaming behind her. "
            "She leaps over a fallen log. Behind her in the distance, three "
            "bear silhouettes stand in the cottage doorway. Morning sunlight "
            "breaks through the trees creating dramatic god-rays. Leaves swirl "
            "in her wake. A family of deer watches from behind a tree. "
            "Dynamic motion and energy, but not scary - more like an adventure."
        ),
        "aspect_ratio": "3:2",
        "resolution": "2K",
        "placement": "Pages 16-17. Wide panoramic image with text below.",
    },
    {
        "filename": "the_end.png",
        "prompt": (
            STYLE_PREFIX
            + "A peaceful epilogue scene: the bear family sits together on "
            "their cottage porch in rocking chairs, eating fresh porridge under "
            "a sunset sky. Baby Bear's chair has been lovingly repaired with "
            "a visible patch. In the far distance, a tiny golden-haired figure "
            "waves from a hilltop path. Fireflies begin to glow. A rainbow "
            "arcs across the sky. Flowers frame the foreground. "
            "The mood is warm, forgiving, and happily-ever-after."
        ),
        "aspect_ratio": "3:2",
        "resolution": "2K",
        "placement": "Final page. Wide image with 'The End' text overlaid in decorative font.",
    },
    {
        "filename": "forest_bg_texture.png",
        "prompt": (
            STYLE_PREFIX
            + "An abstract soft watercolor background texture of a misty forest "
            "canopy seen from below. Extremely soft and diffused, almost like "
            "a dream. Pale greens, soft golds, and creamy whites blend together. "
            "No defined shapes, just gentle color washes with hints of leaves "
            "and branches. Suitable as a translucent background overlay. "
            "Very light and ethereal."
        ),
        "aspect_ratio": "4:5",
        "resolution": "1K",
        "placement": "Background texture used on multiple pages at low opacity (0.08-0.15).",
    },
    {
        "filename": "decorative_border.png",
        "prompt": (
            STYLE_PREFIX
            + "A decorative rectangular border frame made of intertwining "
            "forest vines, wildflowers, tiny mushrooms, acorns, and oak leaves. "
            "The border is on a transparent/white background with the center "
            "completely empty. Corners have special flourishes with small "
            "woodland creatures: a bird, a squirrel, a ladybug, and a butterfly. "
            "Delicate and whimsical. Suitable as a page border overlay."
        ),
        "aspect_ratio": "4:5",
        "resolution": "2K",
        "placement": "Page border overlay used on select pages at varying opacity.",
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
    print(f"  Goldilocks Image Generator")
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
