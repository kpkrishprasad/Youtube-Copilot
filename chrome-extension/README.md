# YouTube Copilot Chrome Extension

AI-powered YouTube video summaries and timestamps, powered by your Django backend.

## Setup Instructions

### 1. Start the Django Backend

Make sure your Django server is running:

```bash
cd /Users/krish.prasad/Desktop/Youtube-Copilot
export OPENAI_API_KEY="your-api-key-here"
python manage.py runserver
```

The server should be running at `http://127.0.0.1:8000/`

### 2. Load the Extension in Chrome

1. Open Chrome and go to `chrome://extensions/`
2. Enable **Developer mode** (toggle in top-right corner)
3. Click **Load unpacked**
4. Select the `chrome-extension` folder:
   ```
   /Users/krish.prasad/Desktop/Youtube-Copilot/chrome-extension
   ```

### 3. Use the Extension

**Method 1: From any page**
- Click the extension icon in your Chrome toolbar
- Paste a YouTube URL
- Click "Get Summary"

**Method 2: On YouTube videos**
- Navigate to any YouTube video
- Click the extension icon (URL will auto-fill)
- Click "Get Summary"

**Method 3: Integrated button (bonus)**
- Navigate to any YouTube video page
- Look for the "✨ Get Summary" button near the like/share buttons
- Click it to open the extension popup

## Features

- 🎯 Auto-detects YouTube URLs when on youtube.com
- ⚡ Fast AI-powered summaries using GPT-4o-mini
- 📍 Generates key timestamps with descriptions
- 🎨 Beautiful, modern UI
- 🔒 Secure - API keys stay on your backend

## Troubleshooting

### "Failed to fetch summary" error

1. **Check if Django server is running:**
   ```bash
   curl http://127.0.0.1:8000/get_summary/
   ```
   Should return an error about POST method (that's OK - means server is up)

2. **Check CORS is enabled:**
   Look for `corsheaders` in your Django settings INSTALLED_APPS

3. **Check browser console:**
   - Right-click on extension popup → Inspect
   - Look for error messages in Console tab

### Extension doesn't load

1. Make sure you're using Chrome (not Safari or Firefox)
2. Check `chrome://extensions/` for any error messages
3. Try clicking "Reload" button on the extension card

### No icon appears

The extension works without an icon. To add one:
- See `ICON_README.txt` for instructions
- Or just ignore it - Chrome will show a default icon

## Development

### File Structure

```
chrome-extension/
├── manifest.json       # Extension configuration
├── popup.html         # Extension popup UI
├── popup.css          # Popup styles
├── popup.js           # Popup logic & API calls
├── content.js         # YouTube page integration
├── content.css        # YouTube button styles
├── icon.svg           # Icon source file
└── README.md          # This file
```

### Modifying the API URL

If you deploy your backend to production, update the API URL in `popup.js`:

```javascript
const API_URL = 'https://your-production-url.com/get_summary/';
```

Also update Django's CORS settings to include your production domain.

## Publishing to Chrome Web Store

1. Create an icon.png file (see ICON_README.txt)
2. Test thoroughly in Developer mode
3. Create a ZIP of the extension folder
4. Go to [Chrome Web Store Developer Dashboard](https://chrome.google.com/webstore/devconsole/)
5. Pay one-time $5 developer fee
6. Upload your ZIP file
7. Fill out store listing details
8. Submit for review

**Important:** If publishing, make sure to:
- Deploy your Django backend to a production server
- Update API URLs in the extension
- Add proper error handling
- Create privacy policy (required by Chrome Web Store)

## License

Same as parent project

