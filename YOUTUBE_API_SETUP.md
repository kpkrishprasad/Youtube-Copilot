# YouTube Data API Setup Guide

The YouTube Research feature requires a YouTube Data API key.

## Quick Setup

### 1. Get Your YouTube API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the **YouTube Data API v3**:
   - Go to "APIs & Services" > "Library"
   - Search for "YouTube Data API v3"
   - Click "Enable"
4. Create credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "API Key"
   - Copy your API key

### 2. Add to .env File

Open `.env` and add your key:

```bash
YOUTUBE_API_KEY=YOUR_ACTUAL_API_KEY_HERE
```

### 3. Restart Django Server

```bash
python manage.py runserver
```

## How the Research Feature Works

1. **User Input**: "I want to learn how to create a resume for software engineering"
2. **Query Optimization**: Gemini converts this to "software engineering resume tutorial"
3. **YouTube Search**: Finds top 5 relevant educational videos
4. **Caption Extraction**: Downloads captions from each video
5. **Guide Generation**: Gemini analyzes all videos and creates a comprehensive learning guide

## API Quota

- Free tier: 10,000 units per day
- Each search costs ~100 units
- You can make ~100 research queries per day for free

## Troubleshooting

### "YouTube API key not configured"
- Make sure you added `YOUTUBE_API_KEY` to `.env`
- Make sure there are no extra spaces
- Restart Django server

### "Quota exceeded"
- You've hit the daily limit (10,000 units)
- Wait until tomorrow or upgrade your quota in Google Cloud Console

### "No videos with captions found"
- Some topics may not have videos with captions
- Try a different search query

## Test It

1. Reload extension at `chrome://extensions/`
2. Click "YouTube Research" tab
3. Enter: "learn python programming basics"
4. Click "Research Topic"
5. Wait 30-60 seconds for results

Enjoy researching any topic with AI-powered YouTube analysis! 🚀

