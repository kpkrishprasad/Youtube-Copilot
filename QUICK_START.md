# Quick Start Guide

## First Time Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install Django django-cors-headers google-generativeai python-dotenv youtube-transcript-api nltk
```

### 2. Configure API Key

Edit the `.env` file and add your Gemini API key:

```bash
# Get your key from: https://aistudio.google.com/app/apikey
GEMINI_API_KEY=AIzaSyD_your_actual_key_here
```

### 3. Run Migrations

```bash
python manage.py migrate
```

### 4. Start the Server

```bash
python manage.py runserver
```

The server will start at: http://127.0.0.1:8000/

## Chrome Extension Setup

### 1. Load Extension in Chrome

1. Open Chrome and go to `chrome://extensions/`
2. Enable **Developer mode** (top-right toggle)
3. Click **Load unpacked**
4. Select the `chrome-extension` folder
5. Done! ✅

### 2. Use the Extension

**On any page:**
- Click the extension icon
- Paste YouTube URL
- Click "Get Summary"

**On YouTube videos:**
- Click the extension icon (URL auto-fills)
- Click "Get Summary"

## Testing

Try with this YouTube URL:
```
https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

## Common Commands

```bash
# Check for issues
python manage.py check

# Run tests
python manage.py test

# Django shell
python manage.py shell

# Create superuser
python manage.py createsuperuser
```

## Troubleshooting

### "ModuleNotFoundError"
**Fix**: Install missing packages
```bash
pip install -r requirements.txt
```

### "GEMINI_API_KEY not found"
**Fix**: Add your key to `.env` file

### Server won't start
**Fix**: Check if another process is using port 8000
```bash
lsof -ti:8000 | xargs kill -9  # Kill process on port 8000
python manage.py runserver 8001  # Use different port
```

## Files Overview

- **`.env`** - API keys (never commit!)
- **`requirements.txt`** - Python dependencies
- **`manage.py`** - Django management script
- **`chrome-extension/`** - Chrome extension files
- **`summary/`** - Main app with AI logic

## Documentation

- **Full Setup**: `GEMINI_SETUP.md`
- **Migration Info**: `MIGRATION_SUMMARY.md`
- **Chrome Extension**: `CHROME_EXTENSION_SETUP.md`
- **Architecture**: `WARP.md`

## Success! 🎉

If you see this message, you're good to go:
```
Django version X.X.X, using settings 'mysite.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

Open http://127.0.0.1:8000/ in your browser and enjoy! 🚀

