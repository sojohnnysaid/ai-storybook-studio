#!/usr/bin/env python3
"""
Goldilocks and the Three Bears: Home Security Edition
=====================================================
Generates all illustrations for the comedic children's book
using the Google Gemini image generation API.

Usage:
    export GEMINI_IMAGE_API_KEY="your-api-key-here"
    python3 generate-images.py
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

API_KEY = os.environ.get("GEMINI_IMAGE_API_KEY")
if not API_KEY:
    print("ERROR: Set GEMINI_IMAGE_API_KEY environment variable.")
    sys.exit(1)

OUTPUT_DIR = Path(__file__).parent / "images"
OUTPUT_DIR.mkdir(exist_ok=True)

MODEL = "gemini-2.5-flash-image"
DELAY_BETWEEN_REQUESTS = 6

# Consistent style across all illustrations
STYLE_PREFIX = (
    "Humorous children's book illustration in warm watercolor and ink style, "
    "with exaggerated cartoon expressions and comedic timing. "
    "Whimsical and playful like a Pixar short meets classic picture book. "
    "Anthropomorphic bear characters wear modern clothes and use technology. "
    "Color palette: warm honey gold, forest green, soft cream, rustic brown, "
    "sky blue, and rose pink. Bright, cheerful, and comedically expressive. "
    "The tone is silly and lighthearted, like a funny cartoon. "
    "IMPORTANT: Do NOT include any text, letters, words, or captions in the image. "
)

IMAGE_MANIFEST = [
    {
        "filename": "cover.png",
        "prompt": (
            STYLE_PREFIX
            + "A hilarious book cover scene: a little girl with golden curly hair "
            "in a blue dress skips merrily toward a charming thatched-roof cottage, "
            "completely oblivious to the multiple high-tech security cameras mounted "
            "on the cottage walls and trees, a Ring doorbell glowing by the front door, "
            "and a small satellite dish on the roof. Motion sensor lights point at her. "
            "A security yard sign reading says 'Protected' sits in the garden. "
            "She's smiling blissfully. The contrast between her innocence and the "
            "heavy security is the joke. Enchanted forest setting with warm golden light."
        ),
        "aspect_ratio": "4:5",
        "resolution": "2K",
        "placement": "Full bleed cover page.",
    },
    {
        "filename": "title_vignette.png",
        "prompt": (
            STYLE_PREFIX
            + "A small circular vignette: a cartoon security camera mounted on a "
            "tree branch in a forest, with a tiny red blinking light. A curious "
            "bluebird sits on top of the camera looking confused. Wildflowers and "
            "mushrooms below. Soft morning forest light. Simple, funny, elegant "
            "composition for a title page. No text."
        ),
        "aspect_ratio": "1:1",
        "resolution": "1K",
        "placement": "Centered on title page, feathered circle mask.",
    },
    {
        "filename": "smart_home_bears.png",
        "prompt": (
            STYLE_PREFIX
            + "A proud bear family portrait in front of their high-tech cottage. "
            "Papa Bear is large and sturdy, wearing a polo shirt and dad jeans, "
            "holding up a tablet showing security camera feeds. Mama Bear is "
            "medium-sized wearing a cozy sweater, looking confident with arms crossed. "
            "Baby Bear is tiny and adorable in a little hoodie, playing with a toy. "
            "Their cottage behind them has solar panels, security cameras on every "
            "corner, smart doorbell, and a Wi-Fi router visible through a window. "
            "A 'Protected by BearGuard' sign in the yard. Warm, proud family photo vibe."
        ),
        "aspect_ratio": "3:4",
        "resolution": "2K",
        "placement": "Page 3. Large image right side, text wraps left.",
    },
    {
        "filename": "kitchen_cameras.png",
        "prompt": (
            STYLE_PREFIX
            + "Cozy bear kitchen interior with a comical amount of modern technology "
            "blended in: a smart fridge with a screen, an Alexa-style device on the "
            "counter, security camera in the corner of the ceiling with a blinking "
            "red light, a tablet mounted on the wall showing camera feeds. "
            "Three bowls of steaming porridge on a rustic wooden table with three "
            "chairs of different sizes. The contrast of cozy cottage and tech is funny. "
            "Warm amber kitchen lighting, copper pots, checkered curtains."
        ),
        "aspect_ratio": "3:2",
        "resolution": "2K",
        "placement": "Page 4. Panoramic image top half.",
    },
    {
        "filename": "papa_phone_walk.png",
        "prompt": (
            STYLE_PREFIX
            + "Three bears walking along a forest path. Papa Bear leads while "
            "staring intently at his smartphone, checking a security camera app. "
            "Mama Bear walks behind carrying a picnic basket, rolling her eyes at "
            "Papa's phone obsession. Baby Bear skips along chasing a butterfly, "
            "oblivious. Papa Bear has one eyebrow raised suspiciously at his phone. "
            "Lush forest path with dappled sunlight. Comedy of Papa's paranoia."
        ),
        "aspect_ratio": "3:2",
        "resolution": "2K",
        "placement": "Page 5. Wide landscape image.",
    },
    {
        "filename": "phone_alert.png",
        "prompt": (
            STYLE_PREFIX
            + "Close-up dramatic shot of Papa Bear's face looking at his smartphone "
            "with a shocked, wide-eyed, jaw-dropped expression. The phone screen "
            "glows on his face. His eyes are huge saucers. He's dropping his "
            "walking stick in surprise. Behind him the peaceful forest is blurred. "
            "Pure comedic overreaction. His fur is standing on end. Sweat drops "
            "fly off his forehead cartoon-style."
        ),
        "aspect_ratio": "4:5",
        "resolution": "2K",
        "placement": "Page 6. Portrait with feathered oval mask.",
    },
    {
        "filename": "goldilocks_oblivious.png",
        "prompt": (
            STYLE_PREFIX
            + "Goldilocks with golden curly hair in a blue dress happily walking "
            "into the bears' cottage through the front door. She has a huge innocent "
            "smile and sparkly eyes, skipping joyfully. Meanwhile, THREE security "
            "cameras on the walls are clearly pointed right at her, red lights "
            "blinking. A motion sensor light has turned on above her. She is "
            "completely oblivious and looks like she's entering Disneyland. "
            "The front door has a high-tech digital lock she somehow got past. "
            "Comedy of her total unawareness."
        ),
        "aspect_ratio": "4:5",
        "resolution": "2K",
        "placement": "Page 7. Large image with text wrapping.",
    },
    {
        "filename": "papa_calls_911.png",
        "prompt": (
            STYLE_PREFIX
            + "Papa Bear frantically talking on his smartphone while speed-walking "
            "back through the forest. He's gesturing wildly with one paw, his "
            "expression is intense and dramatic like an action movie hero. "
            "Mama Bear is behind him on her own phone, looking determined and fierce. "
            "Baby Bear is being carried under Mama's arm like a football, looking "
            "confused but going along with it. Trees blur past suggesting speed. "
            "Comedically dramatic and over-the-top urgent energy."
        ),
        "aspect_ratio": "3:2",
        "resolution": "2K",
        "placement": "Page 8. Wide image.",
    },
    {
        "filename": "mama_gun_locker.png",
        "prompt": (
            STYLE_PREFIX
            + "A comedic dramatic scene: Mama Bear stands in front of an open "
            "high-tech wall safe or locker that has just swung open with dramatic "
            "lighting from inside, like an action movie armory reveal. She looks "
            "fierce and determined, like an action hero. The locker has cool "
            "blue LED interior lighting. Baby Bear peeks from behind a doorframe "
            "with huge worried saucer eyes. The bedroom is cozy with quilts and "
            "teddy bears in the background contrasting the action movie moment. "
            "Over-the-top dramatic lighting and Mama's warrior expression are the joke."
        ),
        "aspect_ratio": "4:5",
        "resolution": "2K",
        "placement": "Page 9. Portrait image, dramatic reveal.",
    },
    {
        "filename": "goldilocks_porridge_cameras.png",
        "prompt": (
            STYLE_PREFIX
            + "Split composition showing TWO things happening simultaneously: "
            "In the main scene, Goldilocks sits at the kitchen table blissfully "
            "tasting porridge from a tiny bowl with her eyes closed in pure "
            "happiness, a dreamy smile on her face, totally at peace. "
            "In the upper corner, a security camera is pointed right at her "
            "with its red light blinking. She doesn't notice or care. "
            "Three bowls on table - one steaming hot, one with frost, one just right. "
            "The comedy is her total zen obliviousness while being fully surveilled."
        ),
        "aspect_ratio": "4:5",
        "resolution": "2K",
        "placement": "Page 10. Float right with text wrap.",
    },
    {
        "filename": "chair_breaks_camera.png",
        "prompt": (
            STYLE_PREFIX
            + "Hilarious scene: Goldilocks crashes through Baby Bear's tiny chair "
            "which splinters everywhere. She has a surprised but still oddly happy "
            "expression, arms flailing, legs in the air. A piece of the chair flies "
            "toward a security camera on the wall. The camera's angle suggests it "
            "caught the whole thing perfectly. Two intact chairs of different sizes "
            "nearby. Living room with bear family photos on wall. Dynamic comic "
            "energy with motion lines. Slapstick comedy."
        ),
        "aspect_ratio": "1:1",
        "resolution": "2K",
        "placement": "Page 11. Square with blob mask.",
    },
    {
        "filename": "hello_baby_bear.png",
        "prompt": (
            STYLE_PREFIX
            + "A sweet and funny scene: Goldilocks has just opened the door to "
            "Baby Bear's bedroom and discovered Baby Bear sitting on his little "
            "bed looking up at her with huge startled eyes. Goldilocks has her "
            "hands on her cheeks in a delighted expression, like she just found "
            "the cutest thing ever. She's beaming with joy. Baby Bear is wearing "
            "pajamas and clutching a teddy bear, frozen in surprise. The room has "
            "glow-in-the-dark stars on the ceiling, tiny furniture, toy trucks. "
            "Sweet and funny contrast - she's delighted, he's terrified."
        ),
        "aspect_ratio": "4:5",
        "resolution": "2K",
        "placement": "Page 12. Large centered image.",
    },
    {
        "filename": "mama_freeze.png",
        "prompt": (
            STYLE_PREFIX
            + "The dramatic confrontation: Mama Bear stands in the bedroom doorway "
            "in a wide power stance, wearing her cozy sweater but looking absolutely "
            "fierce and intimidating like an action movie hero. She's pointing forward "
            "with authority. Her expression is intense mama-bear protective fury. "
            "Goldilocks is turned around with her hands up in surprise, eyes wide "
            "as saucers, mouth in a perfect O shape. Baby Bear peeks out from "
            "under his blanket. The room has a nightlight casting dramatic shadows. "
            "The composition is like a movie poster standoff. Comedically dramatic."
        ),
        "aspect_ratio": "3:2",
        "resolution": "2K",
        "placement": "Pages 13-14. Full width dramatic spread.",
    },
    {
        "filename": "outside_arrest.png",
        "prompt": (
            STYLE_PREFIX
            + "Hilarious scene outside the cottage: Papa Bear stands with arms "
            "crossed looking smug and vindicated. Two animal police officers stand "
            "on either side - one is a SKUNK in a crisp blue police uniform with "
            "a badge, looking very serious and professional, and the other is a "
            "BEAVER in a matching police uniform with a police hat, writing notes "
            "in a tiny notepad. Goldilocks stands between the officers looking "
            "confused and bewildered but not scared. The cottage with all its "
            "security cameras is visible behind them. A police car with flashing "
            "lights is parked on the forest path. Morning sunlight, wildflowers."
        ),
        "aspect_ratio": "3:2",
        "resolution": "2K",
        "placement": "Page 15. Wide panoramic scene.",
    },
    {
        "filename": "handcuffs_departure.png",
        "prompt": (
            STYLE_PREFIX
            + "The funniest scene: Goldilocks is being gently led toward a cartoon "
            "police car by the beaver police officer. She has comically tiny "
            "handcuffs on and an exaggerated pouty confused expression. The skunk "
            "officer holds open the police car door professionally. Papa Bear waves "
            "goodbye smugly from the porch. Mama Bear stands in the doorway looking "
            "relieved, with Baby Bear waving from behind her legs. The police car "
            "has 'FOREST PD' on the side. The whole scene is ridiculously "
            "over-the-top for what was essentially a porridge theft. Golden hour light."
        ),
        "aspect_ratio": "3:2",
        "resolution": "2K",
        "placement": "Page 16. Wide image with text below.",
    },
    {
        "filename": "the_end.png",
        "prompt": (
            STYLE_PREFIX
            + "Epilogue scene: The bear family sits on their cottage porch in "
            "rocking chairs, looking satisfied and cozy. Papa Bear is reviewing "
            "security footage on his tablet with a proud grin. Mama Bear sips tea "
            "peacefully. Baby Bear plays with a toy police car. The cottage behind "
            "them now has EVEN MORE security cameras than before - they've doubled "
            "down. A new bigger security sign is in the yard. A rainbow arcs across "
            "the sunset sky. In the far distance, a tiny police car drives away "
            "on a winding forest road. Warm, funny, happily-ever-after mood."
        ),
        "aspect_ratio": "3:2",
        "resolution": "2K",
        "placement": "Final page with 'The End' overlay.",
    },
    {
        "filename": "forest_bg_texture.png",
        "prompt": (
            STYLE_PREFIX
            + "Abstract soft watercolor background texture of a misty forest "
            "canopy with very subtle hint of a security camera lens flare in one "
            "corner. Extremely soft and diffused, dreamlike. Pale greens, soft "
            "golds, and creamy whites. No defined shapes, just gentle color washes. "
            "Suitable as a translucent background overlay at very low opacity."
        ),
        "aspect_ratio": "4:5",
        "resolution": "1K",
        "placement": "Background texture at low opacity on multiple pages.",
    },
]


def generate_images():
    client = genai.Client(api_key=API_KEY)
    total = len(IMAGE_MANIFEST)
    generated = 0
    skipped = 0
    failed = 0

    print(f"\n{'='*60}")
    print(f"  Goldilocks: Home Security Edition - Image Generator")
    print(f"  Model: {MODEL}")
    print(f"  Images to generate: {total}")
    print(f"  Output directory: {OUTPUT_DIR}")
    print(f"{'='*60}\n")

    for i, img in enumerate(IMAGE_MANIFEST, 1):
        filepath = OUTPUT_DIR / img["filename"]

        if filepath.exists() and filepath.stat().st_size > 0:
            print(f"[{i}/{total}] SKIP (exists): {img['filename']}")
            skipped += 1
            continue

        print(f"[{i}/{total}] Generating: {img['filename']}")
        print(f"         Aspect: {img['aspect_ratio']}  Resolution: {img['resolution']}")

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
                if response.candidates and response.candidates[0].finish_reason:
                    print(f"         Finish reason: {response.candidates[0].finish_reason}")
                failed += 1

        except Exception as e:
            print(f"         ERROR: {e}")
            failed += 1

        if i < total:
            print(f"         Waiting {DELAY_BETWEEN_REQUESTS}s (rate limit)...")
            time.sleep(DELAY_BETWEEN_REQUESTS)

    print(f"\n{'='*60}")
    print(f"  Generation Complete!")
    print(f"  Generated: {generated}")
    print(f"  Skipped:   {skipped}")
    print(f"  Failed:    {failed}")
    print(f"  Total:     {total}")
    print(f"{'='*60}\n")

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
