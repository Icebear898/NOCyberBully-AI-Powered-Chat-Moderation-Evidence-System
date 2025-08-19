from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from .database import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    sender = Column(String(128), index=True, nullable=False)
    receiver = Column(String(128), index=True, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class IncidentLog(Base):
    __tablename__ = "incident_logs"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, index=True)
    sender = Column(String(128), index=True, nullable=False)
    victim = Column(String(128), index=True, nullable=False)
    detected_words = Column(String(512), nullable=False)
    severity = Column(String(32), default="warning")
    screenshot_path = Column(String(512))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class BlockedUser(Base):
    __tablename__ = "blocked_users"

    id = Column(Integer, primary_key=True, index=True)
    victim = Column(String(128), index=True, nullable=False)
    offender = Column(String(128), index=True, nullable=False)
    status = Column(String(32), default="blocked")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class UserSetting(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(128), unique=True, index=True, nullable=False)
    sensitivity = Column(String(32), default="medium")
    warn_threshold = Column(Integer, default=1)
    block_threshold = Column(Integer, default=3)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
