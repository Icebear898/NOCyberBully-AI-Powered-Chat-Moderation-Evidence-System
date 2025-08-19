AI-Powered Cyberbullying Detection & Auto-Response System (MVP) using FastAPI + WebSocket and a simple web frontend.

## Features
- Real-time 1:1 chat over WebSocket
- Abuse detection (v1 lexicon/regex)
- Thresholds with auto-warning/final-warning/blocking based on per-user sensitivity
- Auto-warning bot message to the bully
- Screenshot capture via html2canvas, uploaded to backend and saved under `evidence/`
- Incident logging into SQLite with `/incidents` endpoint
- Dashboard page `/dashboard` for reviewing incidents and downloading reports
- Manual block/unblock endpoints and buttons in UI

## Tech
- FastAPI, Uvicorn
- SQLAlchemy + SQLite
- Vanilla HTML/CSS/JS with html2canvas

## Documentation
- docs/01_synopsis.md — Project Synopsis
- docs/02_architecture.md — Architecture Overview
- docs/03_api_reference.md — API Reference
- docs/04_setup_and_running.md — Setup & Running
- docs/05_detection_and_escalation.md — Detection & Escalation
- docs/06_reporting_and_privacy.md — Reporting & Privacy

## Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000` in two tabs. Use two different usernames (usernames are case-insensitive), set each other's peer, and chat. Choose a sensitivity (low/medium/high) before connecting.
Visit `/dashboard` to view incidents and download a zipped report (CSV + screenshots) per offender-victim pair.

Type abusive words like "idiot", "stupid" (and some basic Hindi terms) to trigger detection. The frontend will capture a screenshot and upload it to `evidence/` path; the backend logs an incident row. Repeated offenses trigger final warning and auto-block.

### Block management endpoints
- GET `/blocked?victim=<username>`
- POST `/block` (form: victim, offender)
- POST `/unblock` (form: victim, offender)

## Next Steps
- Integrate ML toxicity model (HuggingFace or Perspective API)
- Add authentication and user accounts
- Enhance dashboard with filters/search/export
- Multi-language support via expanded lexicons or models
