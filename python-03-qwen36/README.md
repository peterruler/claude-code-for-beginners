# caption-gen

Watches a folder for new images and generates Instagram + LinkedIn captions using the OpenAI Vision API.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # then add your OPENAI_API_KEY
```

## Usage

```bash
# Put images in ./input_images (or set WATCH_DIR in .env)
python caption_gen.py
```

Drop a new `.png`, `.jpg`, `.jpeg`, or `.webp` file into the watch folder and the script will:

1. Send it to **GPT-4o** via the Vision API
2. Produce two captions (Instagram & LinkedIn)
3. Save them to `captions/{filename}_captions.txt`

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | _(required)_ | Your OpenAI API key |
| `OPENAI_MODEL` | `gpt-4o` | Model to use |
| `WATCH_DIR` | `./input_images` | Folder to monitor |
| `OUTPUT_DIR` | `./captions` | Where captions are saved |

## Files

| File | Purpose |
|---|---|
| `caption_gen.py` | Main script |
| `requirements.txt` | Python dependencies |
| `.env.example` | Template for environment variables |
