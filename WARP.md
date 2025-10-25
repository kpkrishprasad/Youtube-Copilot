# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

YouTube Copilot is a Django-based web application that provides AI-powered video analysis. It extracts YouTube video captions, generates concise summaries, and creates timestamp-based navigation points using Google's Gemini 2.0 Flash model.

## Development Commands

### Running the Application
```bash
# Make sure .env file has GEMINI_API_KEY set
python manage.py runserver
```
Access the application at http://127.0.0.1:8000/

**Note**: See `GEMINI_SETUP.md` for API key configuration.

### Database Management
```bash
# Apply migrations
python manage.py migrate

# Create new migrations after model changes
python manage.py makemigrations

# Create superuser for admin access
python manage.py createsuperuser
```

### Testing
```bash
# Run all tests
python manage.py test

# Run tests for a specific app
python manage.py test summary

# Run a specific test
python manage.py test summary.tests.TestClassName.test_method_name
```

### Django Shell
```bash
# Interactive Python shell with Django context
python manage.py shell
```

## Architecture

### Project Structure
- **mysite/**: Django project configuration
  - `settings.py`: Core Django settings, installed apps, middleware, database config
  - `urls.py`: Root URL routing (delegates to summary app)
  
- **summary/**: Main application handling YouTube video processing
  - `views.py`: Request handlers (index page, summary generation endpoint)
  - `urls.py`: App-level URL routing
  - `extract_caption.py`: Core logic for caption extraction and AI processing
  - `templates/summary/`: HTML templates
  - `static/summary/`: JavaScript and CSS assets

### Key Data Flow

1. **User Input → Caption Extraction**: 
   - User submits YouTube URL via web form
   - `convert_link_video_id()` extracts video ID from URL using regex
   - `extract_caption()` fetches transcript using `youtube_transcript_api`
   - Captions are converted to `{timestamp: text}` dictionary format

2. **AI Processing Pipeline**:
   - `create_summary_gpt()`: Reads `summary-prompt.txt`, sends captions to Gemini 2.0 Flash, returns bullet-point summary with emojis (8-10 sentences, ~100 words per 10 min video)
   - `create_timestamps()`: Reads `prompt.txt`, sends captions to Gemini 2.0 Flash, returns key timestamps with labels and emojis
   - Both functions use Google Generative AI client (requires `GEMINI_API_KEY` in `.env` file)

3. **Response Format**:
   - Backend combines summary and timestamps into single string
   - Returns JSON: `{"summary": "combined_text"}` or `{"error": "message"}`
   - Frontend (`script.js`) displays results in `#summaryContainer`

### Gemini AI Integration

The application requires a Gemini API key in the `.env` file:
```bash
GEMINI_API_KEY=your-gemini-api-key-here
```

Get your API key at: https://aistudio.google.com/app/apikey

Both AI functions use:
- Model: `gemini-2.0-flash-exp`
- Prompt templates: `summary/prompt.txt` and `summary/summary-prompt.txt`
- File paths are relative to project root (`./summary/prompt.txt`)
- Settings loaded via `python-dotenv` from `.env` file

### Frontend Architecture

- **CSRF Protection**: Django CSRF tokens handled via `getCookie()` function
- **Async Requests**: Fetch API used for POST requests to `/get_summary/`
- **Loading States**: Spinner displayed during API processing
- **Error Handling**: Alerts shown for invalid requests or fetch failures

## Important Notes

### Security Considerations
- API keys are stored in `.env` file (never commit this file!)
- `.env` is in `.gitignore` to prevent accidental commits
- `SECRET_KEY` loaded from `.env` with fallback to default
- `DEBUG` loaded from `.env` (set to `False` in production)
- Add allowed hosts to `ALLOWED_HOSTS` before deploying

### Database
- Currently uses SQLite (`db.sqlite3`) for development
- No custom models defined yet (using Django defaults)
- Consider PostgreSQL for production deployments

### Dependencies
The project relies on key packages:
- `django`: Web framework
- `django-cors-headers`: CORS support for Chrome extension
- `youtube-transcript-api`: YouTube caption extraction
- `google-generativeai`: Gemini AI API access
- `python-dotenv`: Environment variable management
- `transformers`, `torch`: HuggingFace models (legacy `create_summary()` function - not used)
- `nltk`: Natural language processing utilities

### Prompt Engineering
Two distinct prompt templates control AI behavior:
- `summary-prompt.txt`: Defines summary format (bullet points, emojis, word count)
- `prompt.txt`: Defines timestamp extraction rules (main ideas, labels, emojis)

When modifying AI output, edit these templates rather than changing code.

