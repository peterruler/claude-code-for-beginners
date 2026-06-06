import os
import sys
import time
import signal
import logging
from pathlib import Path
from typing import Optional

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from PIL import Image
from io import BytesIO

import openai

# Optional dotenv loading – harmless if package not installed
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# ---------------------------------------------------------------------------
# Configuration (can be overridden via env vars or CLI args – simplified here)
# ---------------------------------------------------------------------------
WATCH_DIR = Path(os.getenv("WATCH_DIR", "./input"))
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "./output"))
FAILED_DIR = OUTPUT_DIR / "failed"
LOG_FILE = Path("watch_and_caption.log")

# Ensure directories exist
for p in (WATCH_DIR, OUTPUT_DIR, FAILED_DIR):
    p.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helper: wait until a file is fully written (size stabilises)
# ---------------------------------------------------------------------------
def wait_for_complete(path: Path, timeout: int = 30) -> bool:
    """Poll the file size until it stops changing or timeout expires."""
    start = time.time()
    last_size = -1
    while time.time() - start < timeout:
        try:
            size = path.stat().st_size
        except FileNotFoundError:
            return False
        if size == last_size:
            return True
        last_size = size
        time.sleep(0.5)
    return False

# ---------------------------------------------------------------------------
# Caption generation via OpenAI Vision API
# ---------------------------------------------------------------------------
def generate_captions(image_bytes: bytes) -> Optional[dict]:
    """Return {'instagram': str, 'linkedin': str} or None on failure."""
    prompt = (
        "You are a social‑media copywriter. Provide two captions for the attached image:\n"
        "1️⃣ Instagram caption (max 150 characters, include relevant hashtags).\n"
        "2️⃣ LinkedIn caption (max 300 characters, professional tone)."
    )
    for attempt in range(3):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",  # Vision‑capable model
                messages=[
                    {"role": "user", "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_bytes.hex()}"}}
                    ]}
                ],
                max_tokens=500,
            )
            text = response.choices[0].message.content.strip()
            # Simple split on line breaks – assume two lines
            lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
            if len(lines) >= 2:
                return {"instagram": lines[0], "linkedin": lines[1]}
            else:
                log.error("Unexpected caption format: %s", text)
                return None
        except Exception as e:
            log.error("OpenAI API error (attempt %s): %s", attempt + 1, e)
            time.sleep(2 ** attempt)
    return None

# ---------------------------------------------------------------------------
# Event handler for new images
# ---------------------------------------------------------------------------
class ImageHandler(FileSystemEventHandler):
    IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

    def on_created(self, event):
        if event.is_directory:
            return
        path = Path(event.src_path)
        if path.suffix.lower() not in self.IMAGE_EXTS:
            return
        log.info("New image detected: %s", path)
        if not wait_for_complete(path):
            log.error("File %s did not become stable – skipping", path)
            return
        try:
            with Image.open(path) as img:
                    # Ensure image is in RGB mode for JPEG (convert if needed)
                    if img.mode != "RGB":
                        img = img.convert("RGB")
                    buf = BytesIO()
                    img.save(buf, format="JPEG")
                    image_bytes = buf.getvalue()
        except Exception as e:
            log.error("Failed to read image %s: %s", path, e)
            return
        captions = generate_captions(image_bytes)
        if not captions:
            # move to failed folder for manual inspection
            dest = FAILED_DIR / path.name
            path.rename(dest)
            log.error("Captions generation failed – moved %s to %s", path, dest)
            return
        base = path.stem
        (OUTPUT_DIR / f"{base}_instagram.txt").write_text(captions["instagram"], encoding="utf-8")
        (OUTPUT_DIR / f"{base}_linkedin.txt").write_text(captions["linkedin"], encoding="utf-8")
        log.info("Captions written for %s", base)

# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------
def main():
    observer = Observer()
    handler = ImageHandler()
    observer.schedule(handler, str(WATCH_DIR), recursive=False)
    observer.start()
    log.info("Watching %s for new images…", WATCH_DIR)

    # Graceful shutdown handling
    def shutdown(signum, frame):
        log.info("Received signal %s – stopping…", signum)
        observer.stop()
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    try:
        while observer.is_alive():
            observer.join(1)
    except KeyboardInterrupt:
        shutdown(signal.SIGINT, None)
    observer.join()
    log.info("Watcher stopped.")

if __name__ == "__main__":
    main()
