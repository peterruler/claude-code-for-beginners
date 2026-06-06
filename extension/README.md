# Summarize Selection Chrome Extension

## Overview
This minimal Chrome extension adds a **"Summarize"** entry to the right‑click context menu when you highlight text on any webpage. Selecting the entry opens a small popup that shows a three‑sentence AI summary of the highlighted text using the **OpenAI API**.

## Prerequisites
- An OpenAI API key. Add it to a `.env` file in the project root as:
  ```
  OPENAPI_API_KEY=your‑openai‑key
  ```
- The extension reads the key at build time and embeds it into the popup script.

## File structure
```
extension/
│   manifest.json
│   background.js
│   README.md
│
├─ popup/
│   │   popup.html
│   │   popup.css
│   │   popup.js          # Calls OpenAI API (key injected from .env)
│
└─ icons/
    │   icon-16.png
    │   icon-48.png
    │   icon-128.png
```

## How it works
1. **Context menu registration** – `background.js` creates a menu item that only appears when text is selected (`contexts: ["selection"]`).
2. **Fetching the selected text** – When the user clicks the menu, the background script injects a tiny content script that returns `window.getSelection().toString()`.
3. **Passing the text to the popup** – The selected text is stored in `chrome.storage.session` (short‑lived, non‑persistent) and the extension popup is opened.
4. **Calling OpenAI** – `popup.js` reads the stored text, sends a chat‑completion request to `https://api.openai.com/v1/chat/completions` using the model `gpt-4o-mini`. The system prompt forces a three‑sentence summary, and the result is displayed in the popup.

## Security considerations
- The API key is **embedded at build time**; it is not read at runtime from the user's machine, so the extension does not need extra permissions beyond the host permission for `https://api.openai.com/*`.
- The extension only communicates with the OpenAI endpoint, no local server is required.

## Installing locally
1. Open `chrome://extensions/` in Chrome.
2. Enable **Developer mode**.
3. Click **Load unpacked** and select the `extension/` folder.
4. Highlight any text on a page, right‑click, and choose **Summarize**. The popup will appear with the AI‑generated summary.

## Publishing tips
- Provide real icons (16 × 16, 48 × 48, 128 × 128 PNGs) in the `icons/` directory.
- Write a clear **privacy policy** describing that the extension sends selected text only to the OpenAI service.
- Add screenshots of the popup for the Chrome Web Store listing.

---
*Feel free to replace the placeholder icons, adjust the UI styling, or change the system prompt in `popup.js` to suit your needs.*