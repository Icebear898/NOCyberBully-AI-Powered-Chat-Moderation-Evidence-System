# API Reference (MVP)

## WebSocket
`/ws/{username}` (case-insensitive)
- Send: `{ to: string, message: string }`
- Receive events:
  - `{"type":"message","from":"user","message":"text"}`
  - `{"type":"bot","message":"warning text"}`
  - `{"type":"bot_info","message":"info"}`
  - `{"type":"capture_screenshot","context":{"message_id":1,"words":[...],"victim":"..."}}`

## REST
- `GET /` — Chat UI
- `GET /dashboard` — Incident dashboard
- `GET /presence` — `{ active: string[] }`
- `POST /settings` — form: `username`, `sensitivity`
- `GET /incidents` — latest incidents JSON
- `POST /upload_screenshot` — form-data: `message_id`, `screenshot` (file)
- `GET /report?offender=&victim=` — zip with `incidents.csv` and screenshots
- `GET /blocked?victim=` — list blocked offenders for a victim
- `POST /block` — form: `victim`, `offender`
- `POST /unblock` — form: `victim`, `offender`

## Status Codes
- 200 OK on success
- 404 on missing report context
- 4xx on invalid input
