# Chrome Extension Setup - Quick Start

Your YouTube Copilot is now a Chrome Extension! 🎉

## Quick Setup (5 minutes)

### Step 1: Start Django Backend
```bash
export OPENAI_API_KEY="your-api-key-here"
python manage.py runserver
```

### Step 2: Load Extension in Chrome
1. Open Chrome → `chrome://extensions/`
2. Enable **Developer mode** (top-right toggle)
3. Click **Load unpacked**
4. Select folder: `chrome-extension/`
5. Done! ✅

### Step 3: Try It Out
- Visit any YouTube video
- Click the extension icon in Chrome toolbar
- Click "Get Summary" button

## What Was Changed

### Backend (Django)
- ✅ Installed `django-cors-headers`
- ✅ Updated `settings.py` to allow cross-origin requests
- ✅ No changes needed to your existing API endpoints

### New Files Created
```
chrome-extension/
├── manifest.json      # Chrome extension config
├── popup.html         # Extension UI
├── popup.css          # Styling
├── popup.js          # Connects to your Django API
├── content.js        # Adds button to YouTube pages
├── content.css       # Button styling
└── README.md         # Full documentation
```

## How It Works

```
User clicks extension → popup.js → Django API (localhost:8000)
                                       ↓
                                  OpenAI GPT-4o-mini
                                       ↓
                                  Summary + Timestamps
                                       ↓
                                  Display in popup
```

## Features
- 🎯 Auto-fills YouTube URL when on youtube.com
- ⚡ Same AI summaries from your Django backend
- 📍 Generates timestamps with emojis
- 🎨 Beautiful gradient UI
- 🔒 API keys stay secure on backend

## Troubleshooting

**Extension doesn't work?**
1. Check Django is running: `curl http://127.0.0.1:8000/`
2. Check browser console: Right-click popup → Inspect

**Need help?**
See `chrome-extension/README.md` for detailed docs

## Next Steps

**Deploy to Production:**
1. Deploy Django backend (Heroku, Railway, DigitalOcean, etc.)
2. Update `popup.js` API_URL to production URL
3. Update CORS settings in Django

**Publish to Chrome Web Store:**
1. Add icon (see chrome-extension/ICON_README.txt)
2. Create ZIP of chrome-extension folder
3. Submit at https://chrome.google.com/webstore/devconsole/
4. Pay $5 one-time developer fee

Enjoy your Chrome extension! 🚀

