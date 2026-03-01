# Thalpo System Architecture (v1 Scaffold)

This implementation maps your architecture blocks into a runnable service topology.

## User entry points

- PSTN/WebRTC ingress to `orchestrator`.
- Family dashboard via React UI talking to `family-api`.

## Core runtime services

1. **Orchestrator (`apps/orchestrator`)**
- Pipeline: VAD -> STT (Deepgram adapter) -> LLM (OpenAI adapter) -> TTS (Google Chirp-3 Leda / Cartesia fallback).
- Telnyx Voice API webhook endpoint for real phone-call handling (`/v1/telnyx/webhook`).
- Provider-neutral PSTN turn bridge endpoints (`/v1/pstn/start`, `/v1/pstn/turn`).
- LiveKit SIP control endpoints (`/v1/livekit/sip/dispatch`, `/v1/livekit/sip/call`).
- Serves generated MP3 audio files (`/v1/audio/{filename}`).
- Generates LiveKit participant tokens for browser/WebRTC sessions.
- Publishes each turn to Redis stream `thalpo.turns`.
- Launches analysis/alert flow asynchronously and ingests into family API.

2. **Analysis Engine (`apps/analysis_engine`)**
- Baseline risk scoring for emotion/cognition.
- External adapter hooks for Hume and LANGaware.
- Returns merged `AnalysisResult` contract.

3. **Alert Engine (`apps/alert_engine`)**
- Rule-based critical/warning decisioning.
- Optional Telnyx SMS dispatch for family escalation.

4. **Family API (`apps/family_api`)**
- PostgreSQL persistence for events and snapshots.
- JWT auth + role-based access (`admin/caregiver/clinician`).
- Internal token-protected ingest endpoint for orchestrator.

5. **Family Dashboard (`apps/family_dashboard`)**
- Login and dashboard view with metrics, alerts, and history.

## Data stores and messaging

- PostgreSQL: durable snapshots + event history.
- Redis streams: low-latency turn event feed for observability and future worker expansion.

## Security model

- JWT bearer tokens for user API access.
- Role checks on dashboard endpoints.
- `x-internal-token` for machine-to-machine ingest.

## Growth path

- Add Redis consumer workers for resilient retry-based fanout.
- Add multi-tenant policy engine per user profile.
- Add observability stack (OpenTelemetry traces + metrics + alerting).
