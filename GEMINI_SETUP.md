# Gemini 2.0 Flash Setup Guide

Your YouTube Copilot now uses **Gemini 2.0 Flash** instead of OpenAI! 🚀

## Quick Setup

### 1. Get Your Gemini API Key

1. Visit: https://aistudio.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key

### 2. Add API Key to .env File

Open the `.env` file in the project root and replace the placeholder:

```bash
# Before
GEMINI_API_KEY=your-gemini-api-key-here

# After (with your actual key)
GEMINI_API_KEY=AIzaSyD...your-actual-key...
```

### 3. Run the Application

```bash
python manage.py runserver
```

That's it! The app now uses Gemini 2.0 Flash.

## What Changed

### Code Changes
- ✅ Replaced OpenAI with `google-generativeai`
- ✅ Updated `extract_caption.py` to use Gemini 2.0 Flash model
- ✅ Added `.env` file for environment variables
- ✅ Updated Django settings to load `.env`
- ✅ Created `.gitignore` to protect API keys

### Model Info
- **Previous**: OpenAI GPT-4o-mini
- **Current**: Google Gemini 2.0 Flash (experimental)
- **Benefits**: 
  - ⚡ Faster responses
  - 💰 More cost-effective
  - 🌐 Google's latest multimodal AI

## Environment Variables

The `.env` file now contains:

```bash
# Gemini API Key
GEMINI_API_KEY=your-gemini-api-key-here

# Django Secret Key
SECRET_KEY=django-insecure-...

# Debug mode
DEBUG=True
```

**Important**: Never commit `.env` to git! It's already in `.gitignore`.

## Testing

Test that everything works:

```bash
# 1. Start server
python manage.py runserver

# 2. Open browser and go to:
http://127.0.0.1:8000/

# 3. Test with any YouTube URL, for example:
https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

## Chrome Extension

The Chrome extension works exactly the same way! No changes needed.

Just make sure:
1. Your Django server is running
2. Your `.env` file has a valid `GEMINI_API_KEY`

## Troubleshooting

### "GEMINI_API_KEY not found" error

**Solution**: Make sure you've added your API key to the `.env` file.

```bash
# Check if .env file exists
ls -la .env

# Edit the file
nano .env  # or use your preferred editor
```

### Import error: "No module named 'google.generativeai'"

**Solution**: Install the package:
```bash
pip install google-generativeai
```

### "API key invalid" error

**Solution**: 
1. Verify your API key at https://aistudio.google.com/app/apikey
2. Make sure there are no extra spaces in the `.env` file
3. Regenerate the API key if needed

### Model not available

If `gemini-2.0-flash-exp` is not available, you can try:
- `gemini-2.0-flash` (stable version)
- `gemini-1.5-flash` (previous generation)
- `gemini-pro` (older model)

Update in `summary/extract_caption.py`:
```python
model = genai.GenerativeModel('gemini-1.5-flash')  # Change here
```

## API Key Security

✅ **Good Practices:**
- Store API keys in `.env` file
- Never commit `.env` to version control
- Use different keys for development and production
- Rotate keys regularly

❌ **Never:**
- Hardcode API keys in source code
- Share API keys in chat/email
- Commit `.env` to public repos

## Costs

Gemini 2.0 Flash pricing (as of 2024):
- **Free tier**: 15 requests per minute
- **Paid tier**: Very affordable ($0.075 per 1M tokens)

Check current pricing: https://ai.google.dev/pricing

## Next Steps

- ✅ Your app now uses Gemini!
- 🔧 Test thoroughly with various YouTube videos
- 🚀 Deploy to production when ready
- 📊 Monitor API usage in Google AI Studio

Enjoy faster, more cost-effective AI summaries! 🎉

