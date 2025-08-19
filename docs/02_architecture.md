# Architecture Overview

## Components
- Frontend (Web): HTML/CSS/JS. Connects to backend via WebSocket for chat; uses html2canvas to capture screenshots.
- Backend (API): FastAPI. Serves pages, WebSocket endpoint, REST endpoints for incidents, settings, blocking, and reports.
- Database: SQLite via SQLAlchemy ORM.
- Evidence Store: Local folder `evidence/` (screenshots, reports).

## Runtime Flow
1. User connects via WebSocket: `/ws/{username}`
2. User sets peer and starts sending messages over the socket
3. Backend persists messages; detects abuse via lexicon; triggers client to screenshot
4. Client uploads screenshot to `/upload_screenshot`
5. Backend logs incident, applies thresholds for warning/final/block
6. Admin views `/dashboard` and downloads `/report?offender=&victim=`

## Key Modules
- `app/main.py`: routes, WebSocket, thresholds, blocking, reports
- `app/detection.py`: abuse detection utils
- `app/models.py`: `Message`, `IncidentLog`, `BlockedUser`, `UserSetting`
- `app/database.py`: SQLAlchemy engine/session
- `app/templates/`: `index.html`, `dashboard.html`
- `app/static/`: `app.js`, `style.css`

## Data Model
- `messages`: id, sender, receiver, content, created_at
- `incident_logs`: message_id, sender, victim, detected_words, severity, screenshot_path, created_at
- `blocked_users`: victim, offender, status
- `user_settings`: username, sensitivity, warn_threshold, block_threshold

## Security & Privacy (MVP)
- Local demo; no auth
- Evidence stored locally; do not expose publicly
- CORS limited to same origin (default)
- Upgrade with auth, encryption, and secure storage for production
