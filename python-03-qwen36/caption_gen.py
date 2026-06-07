#!/usr/bin/env python3
"""Watch a folder for new images and generate social media captions via the OpenAI Vision API."""

import base64
import io
import os
import time
from pathlib import Path

import dotenv
from openai import OpenAI
from PIL import Image
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

dotenv.load_dotenv()

WATCH_DIR = Path(os.getenv("WATCH_DIR", "."))
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "."))
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
API_KEY = os.getenv("OPENAI_API_KEY")

MAX_DIM = 2048  # resize images larger than this to reduce token cost
SUPPORTED_EXTS = {".png", ".jpg", ".jpeg", ".webp"}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _processed_marker(image_path: Path) -> Path:
    """Return the .processed marker path for an image."""
    return image_path.parent / (image_path.stem + ".processed")


def _is_already_processed(image_path: Path) -> bool:
    """Check whether the marker file exists."""
    return _processed_marker(image_path).exists()


def _mark_processed(image_path: Path) -> None:
    """Touch the marker file."""
    _processed_marker(image_path).touch()


def _encode_image(image_path: Path) -> str:
    """Resize (if needed) and base64-encode the image."""
    with Image.open(image_path) as img:
        # Convert to RGB if necessary (e.g. RGBA or palette mode)
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")

        w, h = img.size
        if w > MAX_DIM or h > MAX_DIM:
            ratio = MAX_DIM / max(w, h)
            img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)

        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=95)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode()


# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------

def generate_captions(image_path: Path) -> str | None:
    """Send the image to GPT-4 Vision and return the raw captions string."""
    client = OpenAI(api_key=API_KEY)
    encoded = _encode_image(image_path)

    prompt = (
        "Generate two social-media captions for the image in this photo:\n"
        "1) Instagram caption — casual, friendly, include relevant hashtags.\n"
        "2) LinkedIn caption — professional, concise.\n\n"
        "Return them as plain text like this:\n"
        "INSTAGRAM:\n<caption>\n\nLINKEDIN:\n<caption>\n"
    )

    resp = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{encoded}"},
                    },
                ],
            }
        ],
        max_tokens=512,
    )

    return resp.choices[0].message.content


def save_captions(image_name: str, captions: str) -> None:
    """Write captions to {image_name}_captions.txt."""
    out_path = OUTPUT_DIR / f"{image_name}_captions.txt"
    out_path.write_text(captions, encoding="utf-8")
    print(f"  -> Saved {out_path}")


# ---------------------------------------------------------------------------
# Watch loop
# ---------------------------------------------------------------------------

def _process(event) -> None:
    """Handle one file-creation event."""
    path = Path(event.src_path)
    if path.suffix.lower() not in SUPPORTED_EXTS:
        return
    if _is_already_processed(path):
        return
    if path.name.startswith("."):
        return  # skip hidden files

    print(f"\n[{path.name}] Generating captions ...")
    try:
        captions = generate_captions(path)
        if captions:
            save_captions(path.stem, captions)
            _mark_processed(path)
        else:
            print(f"  ! No captions returned for {path.name}")
    except Exception:
        print(f"  ! Error processing {path.name}")


class _Handler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        _process(event)


def main() -> None:
    observer = Observer()
    observer.schedule(_Handler(), str(WATCH_DIR), recursive=False)
    observer.start()
    print("Ready.\n")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopped.")
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
