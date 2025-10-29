# YouTube Copilot - System Architecture

```mermaid
---
config:
  theme: base
---

flowchart TB
 %% ==================== USER INTERFACE ====================
 subgraph UI["🖥️ User Interface"]
    CHROME["Chrome Extension<br>Video Info | Research Tabs<br>24hr Cache"]
    WEB["Web Interface<br>(Django Template)"]
 end

 %% ==================== BACKEND ====================
 subgraph BACKEND["🔧 Django Backend (Port 8000)"]
    API["API Endpoints<br>/get_summary/<br>/ask_question/<br>/youtube_research/<br>/email_summary/<br>/email_research/"]
    EXTRACT["Caption Extraction<br>extract_caption.py"]
 end

 %% ==================== DATA PROCESSING ====================
 subgraph PROCESS["📹 Data Processing"]
    CAPTION["Caption Extraction<br>URLToText API<br>Timestamp Estimation"]
    AI["🤖 Gemini 2.0 Flash AI<br>• Video Summary<br>• Key Timestamps<br>• Q&A Answers<br>• Research Guides"]
    RESEARCH["YouTube Research<br>• Query Optimization<br>• Video Search (YT API)<br>• Multi-video Analysis"]
 end

 %% ==================== EXTERNAL SERVICES ====================
 subgraph EXTERNAL["🌐 External APIs"]
    GEMINI["Google Gemini 2.0<br>Flash API"]
    URLTEXT["URLToText API<br>(Transcript)"]
    YTAPI["YouTube Data<br>API v3"]
    SENDGRID["SendGrid<br>(Email Service)"]
 end

 %% ==================== CONFIGURATION ====================
 subgraph CONFIG["⚙️ Configuration"]
    ENV[".env File<br>API Keys"]
 end

 %% =========== MAIN FLOW CONNECTIONS ===========
 
 %% User to Backend
 CHROME --> API
 WEB --> API
 
 %% Backend Processing
 API --> EXTRACT
 EXTRACT --> CAPTION
 
 %% Caption to AI
 CAPTION --> AI
 
 %% Research Flow
 API --> RESEARCH
 RESEARCH --> YTAPI
 RESEARCH --> CAPTION
 RESEARCH --> AI
 
 %% AI to External
 AI --> GEMINI
 CAPTION --> URLTEXT
 
 %% Email Flow
 API --> SENDGRID
 
 %% Results back to UI
 AI --> CHROME
 RESEARCH --> CHROME
 
 %% Configuration
 ENV --> GEMINI
 ENV --> URLTEXT
 ENV --> YTAPI
 ENV --> SENDGRID

 %% Styling
 classDef uiClass fill:#e3f2fd,stroke:#1976d2,stroke-width:3px
 classDef backendClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:3px
 classDef processClass fill:#fff3e0,stroke:#f57c00,stroke-width:3px
 classDef externalClass fill:#e8f5e9,stroke:#388e3c,stroke-width:3px
 classDef configClass fill:#fce4ec,stroke:#c2185b,stroke-width:3px
 
 class CHROME,WEB uiClass
 class BACKEND,API,EXTRACT backendClass
 class PROCESS,CAPTION,AI,RESEARCH processClass
 class EXTERNAL,GEMINI,URLTEXT,YTAPI,SENDGRID externalClass
 class CONFIG,ENV configClass
```

## Key Components

### Frontend (Chrome Extension)
- **Popup UI**: React-like tabbed interface with main tabs (Video Information, YouTube Research)
- **Sub-tabs**: Summary, Timestamps, Q&A under Video Information
- **Caching**: 24-hour local cache using Chrome Storage API

### Backend (Django)
- **Caption Extraction**: URLToText API integration for video transcripts
- **AI Processing**: Google Gemini 2.0 Flash for all AI operations
- **Email Service**: SendGrid for sending summaries and research guides

### Data Flow
1. **Video Analysis**: URL → Caption Extraction → AI Processing → Cache → Display
2. **Q&A**: Question + Captions → Gemini → Answer → Cache
3. **Research**: Topic → Query Optimization → YouTube Search → Multi-video Analysis → Learning Guide
4. **Email**: Content → Template Rendering → SendGrid → User Email

### External Dependencies
- **Google Gemini 2.0 Flash**: Summary, timestamps, Q&A, research guide generation
- **URLToText API**: YouTube video transcript extraction
- **YouTube Data API v3**: Video search for research feature
- **SendGrid**: Email delivery service

### Configuration
All API keys stored in `.env` file and loaded via `python-dotenv`

