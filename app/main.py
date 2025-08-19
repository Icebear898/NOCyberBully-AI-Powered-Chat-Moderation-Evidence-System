from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from sqlalchemy.orm import Session
from typing import Dict, List, Tuple
import os
import uuid
import io
import csv
import zipfile

from .database import Base, engine, get_db
from .models import Message, IncidentLog, BlockedUser, UserSetting
from .detection import detect_abuse

app = FastAPI(title="CyberBull V2")

# Mount static and templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Create tables
Base.metadata.create_all(bind=engine)

# In-memory mapping: username -> WebSocket
active_connections: Dict[str, WebSocket] = {}


def normalize_username(value: str) -> str:
    if value is None:
        return ""
    return value.strip().lower()


def get_or_create_user_settings(db: Session, username: str) -> UserSetting:
    setting = db.query(UserSetting).filter(UserSetting.username == username).first()
    if setting:
        return setting
    setting = UserSetting(username=username)
    db.add(setting)
    db.commit()
    db.refresh(setting)
    return setting


def map_sensitivity_to_thresholds(sensitivity: str) -> Tuple[int, int]:
    s = (sensitivity or "medium").lower()
    if s == "low":
        return 2, 4
    if s == "high":
        return 1, 2
    return 1, 3


def count_offenses(db: Session, sender: str, victim: str) -> int:
    return db.query(IncidentLog).filter(
        IncidentLog.sender == sender,
        IncidentLog.victim == victim,
    ).count()


def is_blocked(db: Session, victim: str, offender: str) -> bool:
    return db.query(BlockedUser).filter(
        BlockedUser.victim == victim,
        BlockedUser.offender == offender,
        BlockedUser.status == "blocked",
    ).first() is not None


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    logs = db.query(IncidentLog).order_by(IncidentLog.id.desc()).limit(200).all()
    return templates.TemplateResponse("dashboard.html", {"request": request, "logs": logs})


@app.get("/presence")
async def presence():
    return {"active": sorted(list(active_connections.keys()))}


@app.post("/settings")
async def set_settings(
    username: str = Form(...),
    sensitivity: str = Form("medium"),
    db: Session = Depends(get_db),
):
    warn_th, block_th = map_sensitivity_to_thresholds(sensitivity)
    setting = db.query(UserSetting).filter(UserSetting.username == username).first()
    if setting is None:
        setting = UserSetting(
            username=username,
            sensitivity=sensitivity,
            warn_threshold=warn_th,
            block_threshold=block_th,
        )
        db.add(setting)
    else:
        setting.sensitivity = sensitivity
        setting.warn_threshold = warn_th
        setting.block_threshold = block_th
    db.commit()
    return {"status": "ok", "username": username, "sensitivity": sensitivity,
            "warn_threshold": warn_th, "block_threshold": block_th}


@app.get("/blocked")
async def list_blocked(victim: str, db: Session = Depends(get_db)):
    rows = db.query(BlockedUser).filter(BlockedUser.victim == victim).all()
    return [
        {"offender": r.offender, "status": r.status, "created_at": str(r.created_at)}
        for r in rows
    ]


@app.post("/block")
async def block_user(victim: str = Form(...), offender: str = Form(...), db: Session = Depends(get_db)):
    existing = db.query(BlockedUser).filter(
        BlockedUser.victim == victim,
        BlockedUser.offender == offender,
    ).first()
    if existing is None:
        db.add(BlockedUser(victim=victim, offender=offender, status="blocked"))
    else:
        existing.status = "blocked"
    db.commit()
    return {"status": "ok"}


@app.post("/unblock")
async def unblock_user(victim: str = Form(...), offender: str = Form(...), db: Session = Depends(get_db)):
    existing = db.query(BlockedUser).filter(
        BlockedUser.victim == victim,
        BlockedUser.offender == offender,
    ).first()
    if existing:
        db.delete(existing)
        db.commit()
    return {"status": "ok"}


@app.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str, db: Session = Depends(get_db)):
    await websocket.accept()
    sender_norm = normalize_username(username)
    # Handle duplicate connections for same username: close old one if any
    previous = active_connections.get(sender_norm)
    if previous is not None and previous is not websocket:
        try:
            await previous.send_json({"type": "bot_info", "message": "You have been signed out due to a new login from the same username."})
        except Exception:
            pass
        try:
            await previous.close()
        except Exception:
            pass
    active_connections[sender_norm] = websocket
    try:
        while True:
            data = await websocket.receive_json()
            receiver_raw = data.get("to")
            receiver = normalize_username(receiver_raw)
            content = data.get("message", "")

            # If receiver has blocked sender, do not deliver
            if is_blocked(db, victim=receiver, offender=sender_norm):
                await websocket.send_json({
                    "type": "bot",
                    "message": f"Your message was not delivered. You are blocked by {receiver}.",
                })
                # Still store the message for audit but skip further processing
                msg = Message(sender=sender_norm, receiver=receiver, content=content)
                db.add(msg)
                db.commit()
                continue

            msg = Message(sender=sender_norm, receiver=receiver, content=content)
            db.add(msg)
            db.commit()
            db.refresh(msg)

            abusive, words = detect_abuse(content)

            # Forward the message to receiver if online
            if receiver in active_connections:
                await active_connections[receiver].send_json({
                    "type": "message",
                    "from": sender_norm,
                    "message": content,
                })
            else:
                await websocket.send_json({
                    "type": "bot_info",
                    "message": f"Peer '{receiver}' is not connected right now.",
                })

            # Echo to sender UI as well
            await websocket.send_json({
                "type": "message",
                "from": sender_norm,
                "message": content,
            })

            if abusive:
                # Ask frontend to capture screenshot
                await websocket.send_json({
                    "type": "capture_screenshot",
                    "context": {
                        "message_id": msg.id,
                        "words": words,
                        "victim": receiver,
                    }
                })
                settings = get_or_create_user_settings(db, receiver)
                offenses_before = count_offenses(db, sender=sender_norm, victim=receiver)
                offenses = offenses_before + 1

                # Determine severity and actions
                if offenses < settings.block_threshold:
                    severity = "warning" if offenses <= settings.warn_threshold else "final_warning"
                    text = (
                        f"⚠️ Warning: You used abusive word(s) {', '.join(words)} against {receiver}. "
                        if severity == "warning" else
                        f"⚠️ Final Warning: You used abusive word(s) {', '.join(words)} against {receiver}. Next offense will trigger blocking." 
                    )
                    await websocket.send_json({"type": "bot", "message": text})
                else:
                    severity = "blocked"
                    # Block offender for the victim
                    if not is_blocked(db, victim=receiver, offender=sender_norm):
                        db.add(BlockedUser(victim=receiver, offender=sender_norm, status="blocked"))
                        db.commit()
                    await websocket.send_json({
                        "type": "bot",
                        "message": f"🚫 You have been blocked by {receiver} due to repeated abusive messages. An incident report has been prepared.",
                    })

                incident = IncidentLog(
                    message_id=msg.id,
                    sender=sender_norm,
                    victim=receiver,
                    detected_words=", ".join(words),
                    severity=severity,
                    screenshot_path=None,
                )
                db.add(incident)
                db.commit()

                # Notify receiver privately
                if receiver in active_connections:
                    await active_connections[receiver].send_json({
                        "type": "bot_info",
                        "message": f"Abusive language detected from {sender_norm}. Severity: {severity}.",
                    })

    except WebSocketDisconnect:
        pass
    finally:
        active_connections.pop(sender_norm, None)


@app.post("/upload_screenshot")
async def upload_screenshot(
    message_id: int = Form(...),
    screenshot: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    evidence_dir = os.path.abspath("evidence")
    os.makedirs(evidence_dir, exist_ok=True)
    filename = f"{uuid.uuid4().hex}.png"
    filepath = os.path.join(evidence_dir, filename)
    with open(filepath, "wb") as f:
        f.write(await screenshot.read())

    # update last incident for this message
    incident = db.query(IncidentLog).filter(IncidentLog.message_id == message_id).order_by(IncidentLog.id.desc()).first()
    if incident:
        incident.screenshot_path = filepath
        db.commit()

    return {"status": "ok", "path": filepath}


@app.get("/incidents")
async def list_incidents(db: Session = Depends(get_db)):
    logs = db.query(IncidentLog).order_by(IncidentLog.id.desc()).limit(100).all()
    return [
        {
            "id": log.id,
            "message_id": log.message_id,
            "sender": log.sender,
            "victim": log.victim,
            "detected_words": log.detected_words,
            "severity": log.severity,
            "screenshot_path": log.screenshot_path,
            "created_at": str(log.created_at),
        }
        for log in logs
    ]


@app.get("/report")
async def download_report(offender: str, victim: str, db: Session = Depends(get_db)):
    incidents: List[IncidentLog] = db.query(IncidentLog).filter(
        IncidentLog.sender == offender,
        IncidentLog.victim == victim,
    ).order_by(IncidentLog.id.asc()).all()
    if not incidents:
        raise HTTPException(status_code=404, detail="No incidents for this pair")

    reports_dir = os.path.abspath(os.path.join("evidence", "reports"))
    os.makedirs(reports_dir, exist_ok=True)
    zip_name = f"report_{victim}_vs_{offender}_{uuid.uuid4().hex}.zip"
    zip_path = os.path.join(reports_dir, zip_name)

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        # incidents.csv
        csv_buf = io.StringIO()
        writer = csv.writer(csv_buf)
        writer.writerow(["id", "message_id", "sender", "victim", "detected_words", "severity", "screenshot_path", "created_at"])
        for inc in incidents:
            writer.writerow([
                inc.id, inc.message_id, inc.sender, inc.victim, inc.detected_words, inc.severity,
                inc.screenshot_path or "", str(inc.created_at),
            ])
        zf.writestr("incidents.csv", csv_buf.getvalue())

        # add screenshots
        for inc in incidents:
            if inc.screenshot_path and os.path.exists(inc.screenshot_path):
                arcname = os.path.join("screenshots", os.path.basename(inc.screenshot_path))
                zf.write(inc.screenshot_path, arcname)

    return FileResponse(zip_path, media_type="application/zip", filename=zip_name)
