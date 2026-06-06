# Python‑03: Image‑watcher & caption generator

This small utility watches a folder for newly added images, sends each image to the OpenAI Vision API, and writes two caption files – one for Instagram and one for LinkedIn.

## Quick start
```bash
# Install dependencies
pip install -r requirements.txt

# (optional) create a .env with your OpenAI key
echo "OPENAI_API_KEY=sk-..." > .env

# Run the watcher (default watches ./input and writes to ./output)
python watch_and_caption.py
```

## Configuration
- **WATCH_DIR** – directory to monitor (env var or `--watch-dir` CLI flag). Default: `./input`.
- **OUTPUT_DIR** – where caption `.txt` files are saved. Default: `./output`.
- **OPENAI_API_KEY** – required; can be placed in a `.env` file or exported in the shell.

## How it works
1. `watchdog` detects a new image file.
2. The script reads the image, calls the OpenAI Vision model with a prompt asking for two captions.
3. Captions are written to `<basename>_instagram.txt` and `<basename>_linkedin.txt`.
4. Errors are logged and the problematic image is moved to a `failed/` folder.

## Future ideas
- Batch multiple images in a single API request to reduce cost.
- Cache hashes of processed images to avoid duplicates.
- Use `typer` for a richer CLI.
