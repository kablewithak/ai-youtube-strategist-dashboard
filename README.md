# AI YouTube Strategist Dashboard

An MVP web app that helps analyze a YouTube channel and turn channel evidence into strategist-style recommendations.

This project is built to feel like an **analyst dashboard**, not a generic chatbot. It combines:
- YouTube channel evidence
- manual audience context
- screenshot evidence
- notes
- evidence synthesis
- early recommendation drafting

## What the MVP does

A user can:

1. open the web app
2. enter a YouTube channel URL
3. enter channel niche and goals
4. enter audience demographics through a normal form
5. add notes
6. review and edit assumptions
7. ingest YouTube channel evidence
8. upload screenshots
9. synthesize evidence with Gemini
10. draft ranked recommendation outputs in the dashboard

## Current product flow

### Intake page
The intake page collects:
- YouTube channel URL
- channel niche
- channel goals
- audience demographics
- notes

### Run page
The run page supports:
- assumption review and editing
- YouTube evidence ingestion
- screenshot upload
- evidence synthesis
- recommendation draft generation

### Current dashboard sections
The run page currently exposes:
- run overview
- assumptions
- screenshot evidence
- YouTube channel summary
- evidence summary
- synthesized strategist findings
- audience psychology
- ranked recommendation draft output

## Current stack

### Frontend
- Next.js
- TypeScript
- App Router
- simple client-side state for MVP speed

### Backend
- FastAPI
- Pydantic
- Uvicorn

### Model layer
- Gemini API
- multimodal synthesis for screenshots and compiled evidence

### External data
- YouTube Data API v3

## Current architecture

The MVP uses a staged pipeline.

### 1. Intake
Collect:
- channel URL
- niche
- goals
- audience demographics
- notes

### 2. Assumptions
Create and edit:
- audience interests
- likely topic patterns
- audience intent
- screenshot interpretation
- confidence notes

### 3. Evidence ingestion
Fetch and structure:
- channel metadata
- recent video metadata
- comment samples

### 4. Screenshot evidence
Upload screenshots and store them locally for the run.

### 5. Evidence synthesis
Gemini synthesizes:
- channel summary
- audience mood
- praise themes
- pain points
- request themes
- repeated phrases
- evidence strength notes

### 6. Strategist playbook layer
The app includes a strategist playbook layer used for:
- audience psychology framing
- title logic
- thumbnail logic
- CTA timing
- CTA copy logic

### 7. Recommendation draft
The backend produces:
- audience psychology output
- idea candidates
- ranked recommendation draft output

## Repo structure

```text
ai-youtube-strategist-dashboard/
├── apps/
│   ├── api/
│   │   ├── app/
│   │   │   ├── api/routes/
│   │   │   ├── core/
│   │   │   ├── schemas/
│   │   │   ├── services/
│   │   │   │   ├── analysis/
│   │   │   │   ├── evidence/
│   │   │   │   ├── playbooks/
│   │   │   │   ├── recommendations/
│   │   │   │   └── youtube/
│   │   │   └── main.py
│   │   ├── .env
│   │   └── requirements.txt
│   └── web/
│       ├── src/app/
│       ├── src/lib/
│       └── package.json
└── README.md


Environment variables

Create apps/api/.env with:

APP_ENV=development
CORS_ALLOW_ORIGINS=http://localhost:3000
YOUTUBE_API_KEY=your_youtube_api_key
GEMINI_API_KEY=your_gemini_api_key
GEMINI_SYNTHESIS_MODEL=gemini-2.5-flash

Create apps/web/.env.local with:

NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

Frontend:

http://localhost:3000
Important MVP note

Runs are currently stored in memory.

That means if the backend restarts, old runs disappear.

After every backend restart, use a fresh flow:

create run
save assumptions
ingest YouTube evidence
upload screenshots if needed
synthesize evidence
draft recommendations
Key backend routes
Health
GET /health
Runs
POST /runs
GET /runs/{run_id}
PATCH /runs/{run_id}/assumptions
Evidence
POST /runs/{run_id}/ingest-youtube
POST /runs/{run_id}/screenshots
POST /runs/{run_id}/synthesize-evidence
Recommendation draft
POST /runs/{run_id}/recommendations/draft
Current recommendation draft output

The recommendation draft route currently returns:

audience psychology output
idea candidates
top ranked recommendation draft output

Each recommendation includes:

rank
idea
hook
title options
thumbnail angle
suggested structure
CTA placement
CTA copy
why this fits
evidence notes
What is working well right now
the intake UX is cleaner
demographics are normal form fields, not JSON
assumptions are editable without broken typing
channel evidence can be ingested
screenshots can be uploaded
evidence can be synthesized
audience psychology and recommendation draft data can be rendered in the UI
Known limitations

This is still an MVP.

Current limitations:

runs are in-memory only
no database persistence yet
trend layer is still basic / incomplete
recommendation scoring is heuristic and should be improved
idea quality still needs stronger localization and trend weighting
screenshot handling is local-first, not production storage
strategist playbook assets may still be using fallbacks if repo playbook files are not yet added
no auth or multi-user persistence yet
no production deployment configuration yet