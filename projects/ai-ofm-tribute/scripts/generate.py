#!/usr/bin/env python3
"""AI OFM Content Generator — generates AI model images via Pollinations.ai (free, no key).

Uses: https://image.pollinations.ai/prompt/{prompt}?width=&height=&seed=&model=
Output: content/sessions/NN/*.jpg + preview.html (with real images)

Usage:
    python generate.py --count 5 --style fantasy
    python generate.py --count 3 --session 2 --style anime
"""

import os
import sys
import json
import random
import argparse
import urllib.request
import urllib.parse
import time
from pathlib import Path
from datetime import datetime, timezone

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = PROJECT_ROOT / "content" / "sessions"
CONFIG_FILE = PROJECT_ROOT / "config.yaml"

DEFAULT_CONFIG = {
    "styles": ["fantasy", "anime", "realistic"],
    "prompts": {
        "fantasy": [
            "Ethereal fantasy woman with glowing crystal skin, detailed digital art, cinematic lighting, artstation style, symmetrical face, perfect skin, flowing magical dress, intricate jewelry, golden hour lighting, photorealistic, hyperdetailed, 8k",
            "Mystical elf queen in enchanted forest, bioluminescent flowers, shimmering dress, elegant pose, detailed face, dappled sunlight, fantasy art, intricate details, volumetric fog",
            "Sorceress with flowing silver hair casting a spell, magical particles around hands, dramatic lighting, fantasy portrait, intricate robe details, glowing runes, ethereal atmosphere",
            "Goddess of moonlight standing on ancient temple ruins, silver-white dress, glowing eyes, mystical aura, starry night sky, fantasy art, cinematic composition, photorealistic",
            "Forest nymph with flower crown, dewdrop skin, emerald eyes, magical forest background, soft sunlight filtering through leaves, dreamy atmosphere, hyperdetailed portrait"
        ],
        "anime": [
            "Anime style beautiful woman, detailed eyes, flowing pink hair, elegant kimono, cherry blossom background, warm lighting, high quality anime art, detailed face, trending pixiv style",
            "Vibrant anime girl with colorful hair, stylish modern outfit, dynamic pose, clean lineart, cel shading, beautiful face, urban sunset background, high resolution anime art",
            "Anime girl portrait, large expressive eyes, soft pastel color palette, flowing dress, flower crown, sunset gradient sky, dreamy atmosphere, detailed linework, painterly style",
            "Magical girl anime style, sparkling wand, starry transformation effect, cute outfit with ribbons, bright colors, bokeh background, high quality illustration",
            "Anime waifu portrait, studio quality, detailed hair strands, glowing eyes, fashionable clothes, neon city background at night, cinematic lighting, vibrant colors"
        ],
        "realistic": [
            "Professional editorial photo of elegant woman, natural studio lighting, detailed skin texture, soft focus background, high fashion outfit, clean makeup, 8k photorealistic",
            "Portrait of beautiful woman in summer dress, golden hour outdoor photography, natural sunlight, warm tones, shallow depth of field, professional photography",
            "Fashion model editorial shot, dramatic lighting, high contrast, elegant pose, sophisticated outfit, studio photography, sharp details, magazine quality",
            "Beauty portrait with soft natural lighting, minimal makeup, clean background, professional photography, natural skin texture, sharp eyes, high-end fashion style",
            "Editorial fashion photography, femme fatale style, noir lighting, red lipstick, elegant dress, urban setting, moody atmosphere, cinematic composition"
        ]
    },
    "captions": {
        "fantasy": [
            "✨ New fantasy art | Exclusive content",
            "🌟 Magic in every detail | Premium gallery",
            "💫 Fantasy collection | Member access only",
            "🌙 Mystical beauty | Daily exclusive",
            "⭐ Enchanted | Subscriber preview"
        ],
        "anime": [
            "🌸 New anime art | Daily exclusive",
            "🎨 Fresh illustration | Premium gallery",
            "✨ Anime collection | Member access only",
            "💖 Kawaii dreams | Exclusive content",
            "🌟 Anime magic | Subscriber preview"
        ],
        "realistic": [
            "📸 New editorial | Premium photoshoot",
            "✨ Fresh look | Exclusive content",
            "💫 Daily update | Member gallery",
            "👑 Elegance | Premium subscriber content",
            "💎 Luxury portraits | Exclusive access"
        ]
    }
}


def load_config():
    try:
        import yaml
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE) as f:
                cfg = yaml.safe_load(f)
            if cfg and "styles" in cfg:
                return cfg
    except ImportError:
        pass
    return DEFAULT_CONFIG


def download_image(url, output_path, timeout=60):
    """Download image from url to output_path. Returns True on success."""
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Hermes-Agent/1.0 (AI OFM Generator)"
            }
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            data = response.read()
            if len(data) < 1000:
                print(f"  WARNING: Response too small ({len(data)} bytes), may be error")
                return False
            with open(output_path, "wb") as f:
                f.write(data)
            return True
    except Exception as e:
        print(f"  ERROR: {e}")
        return False


def generate_preview(session_dir, images, style, session_num):
    """Generate HTML preview with real images."""
    cards_html = ""
    for img in images:
        img_path = os.path.relpath(img["filepath"], session_dir)
        cards_html += f"""
<div class="card">
 <img src="{img_path}" alt="{img['caption']}" loading="lazy">
 <div class="card-body">
  <div class="caption">{img['caption']}</div>
  <div class="seed">seed {img['seed']} | {img['model']}</div>
 </div>
</div>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Session {session_num:02d} — {style} preview</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, system-ui, sans-serif; background: #0a0a0a; color: #fff; padding: 20px; }}
h1 {{ color: #ff6b9d; margin-bottom: 8px; }}
.subtitle {{ color: #888; margin-bottom: 24px; }}
.gallery {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }}
.card {{ background: #1a1a1a; border-radius: 12px; overflow: hidden; transition: transform 0.2s; }}
.card:hover {{ transform: translateY(-4px); }}
.card img {{ width: 100%; display: block; aspect-ratio: 3/4; object-fit: cover; }}
.card-body {{ padding: 12px; }}
.card-body .caption {{ color: #aaa; font-size: 14px; margin-bottom: 4px; }}
.card-body .seed {{ color: #555; font-size: 12px; }}
</style>
</head>
<body>
<h1>Session {session_num:02d}</h1>
<p class="subtitle">Style: {style} | {len(images)} images | {datetime.now():%Y-%m-%d %H:%M}</p>
<div class="gallery">
{cards_html}
</div>
</body>
</html>"""

    preview_path = session_dir / "preview.html"
    with open(preview_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Preview: {preview_path}")


def main():
    parser = argparse.ArgumentParser(description="AI OFM Content Generator (Pollinations.ai)")
    parser.add_argument("--count", type=int, default=5, help="Number of images (default: 5)")
    parser.add_argument("--style", choices=["fantasy", "anime", "realistic"],
                        default="fantasy", help="Art style")
    parser.add_argument("--session", type=int, default=None,
                        help="Session number (auto-increments)")
    parser.add_argument("--model", choices=["flux", "seedream", "turbo", "nanobanana"],
                        default="flux", help="Pollinations model (default: flux)")
    parser.add_argument("--width", type=int, default=768, help="Image width (default: 768)")
    parser.add_argument("--height", type=int, default=1024, help="Image height (default: 1024)")
    parser.add_argument("--delay", type=float, default=2.0, help="Delay between requests in seconds (default: 2.0)")
    args = parser.parse_args()

    config = load_config()

    # Auto-increment session number
    if args.session is None:
        existing = list(CONTENT_DIR.glob("*"))
        session_nums = []
        for d in existing:
            if d.is_dir() and d.name.isdigit():
                session_nums.append(int(d.name))
        args.session = max(session_nums) + 1 if session_nums else 1

    session_dir = CONTENT_DIR / f"{args.session:02d}"
    session_dir.mkdir(parents=True, exist_ok=True)

    prompts = config.get("prompts", {}).get(args.style, DEFAULT_CONFIG["prompts"]["fantasy"])
    captions = config.get("captions", {}).get(args.style, DEFAULT_CONFIG["captions"]["fantasy"])
    results = []
    success_count = 0
    fail_count = 0

    print(f"\n{'='*60}")
    print(f"Session {args.session:02d} | Style: {args.style} | Model: {args.model}")
    print(f"Generating {args.count} images via Pollinations.ai...")
    print(f"{'='*60}\n")

    for i in range(args.count):
        prompt = random.choice(prompts)
        caption = random.choice(captions) if captions else ""
        seed = random.randint(1, 1000000)

        # Build Pollinations URL
        encoded_prompt = urllib.parse.quote(prompt)
        url = (f"https://image.pollinations.ai/prompt/{encoded_prompt}"
               f"?width={args.width}&height={args.height}"
               f"&seed={seed}&model={args.model}")

        filename = f"{args.style}_{args.session:02d}_{i+1:02d}.jpg"
        filepath = session_dir / filename

        print(f"[{i+1}/{args.count}] Generating... seed={seed}")
        print(f"  model={args.model} | {args.width}x{args.height}")

        ok = download_image(url, filepath)

        # Delay between requests to avoid rate limiting
        if i < args.count - 1:
            time.sleep(args.delay)

        result = {
            "index": i + 1,
            "style": args.style,
            "prompt": prompt,
            "seed": seed,
            "caption": caption,
            "model": args.model,
            "filename": filename,
            "filepath": str(filepath),
            "success": ok,
        }

        if ok:
            file_size = filepath.stat().st_size
            result["file_size"] = file_size
            success_count += 1
            print(f"  OK — {file_size // 1024} KB")
        else:
            fail_count += 1
            print(f"  FAIL — placeholder created")

        results.append(result)

    # Save manifest
    manifest = {
        "session": args.session,
        "style": args.style,
        "model": args.model,
        "count": args.count,
        "success_count": success_count,
        "fail_count": fail_count,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "provider": "pollinations.ai",
        "images": results
    }

    manifest_path = session_dir / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    # Generate preview
    generate_preview(session_dir, results, args.style, args.session)

    print(f"\n{'='*60}")
    print(f"Session {args.session:02d} complete")
    print(f"  Generated: {success_count}/{args.count} images")
    print(f"  Failed: {fail_count}")
    print(f"  Location: {session_dir}")
    print(f"  Preview: {session_dir / 'preview.html'}")
    print(f"{'='*60}")

    # Output JSON for assistant processing
    print("\n---META---")
    print(json.dumps({
        "session": args.session,
        "style": args.style,
        "model": args.model,
        "count": args.count,
        "success_count": success_count,
        "fail_count": fail_count,
        "dir": str(session_dir)
    }))


if __name__ == "__main__":
    main()
