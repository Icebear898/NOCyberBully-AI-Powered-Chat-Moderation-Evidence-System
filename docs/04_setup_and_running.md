# Setup & Running (Local Demo)

## Prerequisites
- Python 3.10+

## Steps
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000` in two tabs.
- Choose usernames (case-insensitive)
- Set each other as peer
- Choose sensitivity (low/medium/high)

## Troubleshooting
- If one side doesn’t receive messages:
  - Ensure both tabs use the same lowercase usernames
  - Refresh and reconnect both
  - Check `/presence` to see connected users
- Ensure the virtual environment is active and dependencies are installed
