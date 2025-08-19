# Project Synopsis: AI-Powered Cyberbullying Detection & Auto-Response (CyberBull V2)

## Problem
Women and girls face online harassment across social platforms. Manual reporting is too slow and reactive, causing psychological harm and exposing victims to repeat abuse.

## Solution
CyberBull V2 provides a real-time monitoring and mitigation layer for 1:1 chat. It detects abusive language, warns the offender, captures evidence (screenshots), logs incidents, escalates repeated offenses, and can automatically block offenders based on user-configurable sensitivity.

## Objectives
- Detect abusive/harassing messages in real-time
- Nudge/educate offenders with automated warnings
- Reduce harm via configurable thresholds and auto-blocking
- Preserve evidence with screenshots and structured logs
- Provide a simple dashboard and report generation for escalation

## Scope (MVP)
- Web chat client (two users, local demo)
- FastAPI backend with WebSocket chat
- Lexicon-based abuse detection (extendable to ML)
- Threshold/escalation logic and blocklist
- Evidence uploads and incident logs
- Dashboard and downloadable incident report

## Out of Scope (MVP)
- Production-grade authentication and identity
- Native mobile apps
- Full multi-platform integrations (Instagram/Twitter/Meta/WhatsApp)
- Advanced ML models (placeholder for v2)

## Impact
- Helps reduce exposure to abuse in real-time
- Lowers barrier to documenting/reporting harassment
- Provides a foundation to integrate with real social media APIs
