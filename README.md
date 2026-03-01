# Thalpo v1

Full-stack architecture scaffold for **Thalpo** with:
- voice orchestration pipeline
- external provider adapters (LiveKit, Deepgram, OpenAI, Google Chirp-3 Leda, Cartesia)
- Telnyx + LiveKit SIP telephony path
- parallel analysis and alerting
- persistent family dashboard API (Postgres)
- React family dashboard
- role-based authentication and internal service auth

## Services

- `orchestrator` (`8000`): VAD -> STT -> LLM -> TTS, PSTN endpoints, Telnyx webhook endpoint, LiveKit SIP control endpoints, audio serving, Redis turn stream.
- `analysis-engine` (`8001`): baseline scoring + optional Hume/LANGaware adapters.
- `alert-engine` (`8002`): emergency decision logic + optional Telnyx SMS dispatch.
- `family-api` (`8003`): Postgres-backed dashboard data + JWT auth/roles + conversation insights.
- `family-dashboard` (`5173`): caregiver UI (React + Vite).
- Infra: Redis (`6379`), Postgres (`5432`).

## Repo map

- `apps/orchestrator/`
- `apps/analysis_engine/`
- `apps/alert_engine/`
- `apps/family_api/`
- `apps/family_dashboard/`
- `shared/contracts/`
- `infra/docker-compose.yml`
- `infra/env/*.env.example`
- `scripts/smoke_test.sh`
- `scripts/sip_bridge_test.sh`
- `scripts/telnyx_webhook_test.sh`
- `scripts/mac_chat.py`

## Quick start (local)

```bash
cd "/Users/aretikirpitsa/Desktop/Thalpo/Thalpo_v1"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

docker compose -f infra/docker-compose.yml up -d postgres redis analysis-engine alert-engine family-api
```

In a new terminal:

```bash
cd "/Users/aretikirpitsa/Desktop/Thalpo/Thalpo_v1"
source .venv/bin/activate
make run-orchestrator
```

## Text chat from your Mac (no phone)

In another terminal while orchestrator is running:

```bash
cd "/Users/aretikirpitsa/Desktop/Thalpo/Thalpo_v1"
source .venv/bin/activate
python scripts/mac_chat.py --orchestrator-url http://localhost:8000 --user-id areti --play-audio
```

- Type messages and press Enter.
- Use `/exit` to stop.
- `--play-audio` plays generated local MP3 replies with `afplay`.

## Greek voice chat from your Mac (no phone)

This mode supports two STT paths:
- Browser STT (SpeechRecognition, best in Chrome)
- Server STT (OpenAI transcription, requires `OPENAI_API_KEY`)

Flow:
1. Open:
   - `http://localhost:8000/v1/mac/voice-chat`
2. Click `Έναρξη κλήσης` once.
3. Speak naturally; each turn is auto-sent and Thalpo auto-replies.
4. Click `Τερματισμός κλήσης` when you want to end.
5. If browser STT is unavailable, export `OPENAI_API_KEY` and retry.

## Required env (orchestrator)

Use values from `infra/env/orchestrator.env.example`, especially:

```bash
export PUBLIC_BASE_URL="https://YOUR_PUBLIC_DOMAIN"

export TTS_BACKEND="google"
export GOOGLE_TTS_LANGUAGE_CODE="el-GR"
export GOOGLE_TTS_VOICE_NAME="el-GR-Chirp3-HD-Leda"
export GOOGLE_TTS_SPEAKING_RATE="0.95"
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/.config/thalpo/keys/thalpo-tts.json"

export LLM_PROVIDER="openai"   # or "azure"
export OPENAI_API_KEY="..."
export OPENAI_MODEL="gpt-4.1-mini"
export OPENAI_TRANSCRIBE_MODEL="whisper-1"
export OPENAI_REQUEST_TIMEOUT_SECONDS="20"

# If using Azure OpenAI for replies (LLM only):
export LLM_PROVIDER="azure"
export AZURE_OPENAI_API_KEY="..."
export AZURE_OPENAI_ENDPOINT="https://<resource>.openai.azure.com"
export AZURE_OPENAI_DEPLOYMENT="gpt-4o-mini"
export AZURE_OPENAI_API_VERSION="2024-10-21"
# Optional: Azure server-STT for /v1/mac/transcribe
export AZURE_OPENAI_TRANSCRIBE_DEPLOYMENT="gpt-4o-mini-transcribe"

export TELNYX_API_KEY="..."
export TELNYX_ENABLE_TRANSCRIPTION="true"
export TELNYX_TRANSCRIPTION_TRACKS="inbound"

export LIVEKIT_API_KEY="..."
export LIVEKIT_API_SECRET="..."
export LIVEKIT_WS_URL="wss://..."
export LIVEKIT_SIP_INBOUND_TRUNK_ID="..."
export LIVEKIT_SIP_OUTBOUND_TRUNK_ID="..."
```

Notes:
- Leda voice stays on Google TTS (`GOOGLE_TTS_VOICE_NAME=el-GR-Chirp3-HD-Leda`) even if LLM provider is Azure.
- Server STT can use either `OPENAI_API_KEY` OR Azure transcribe deployment (`AZURE_OPENAI_TRANSCRIBE_DEPLOYMENT`).
- Browser STT does not need API keys.

## Real phone test (fast path)

This is the fastest real test from your own phone.

1. Start ngrok for orchestrator:

```bash
ngrok http 8000
```

2. Copy your ngrok URL and set:

```bash
export PUBLIC_BASE_URL="https://<your-ngrok-domain>"
```

3. In Telnyx dashboard:
- Create/use a Voice API application (Call Control).
- Set webhook URL to:
  - `https://<your-ngrok-domain>/v1/telnyx/webhook`
- Assign your Telnyx phone number to this app.

4. Keep both running:
- orchestrator terminal
- ngrok terminal

5. Call your Telnyx number from your mobile phone.
- The app answers.
- Greets with Leda (Google TTS MP3 playback).
- Receives transcription webhook events from Telnyx.
- Sends each utterance to Thalpo pipeline.
- Plays back Leda responses.

## Local webhook simulation (no phone)

```bash
./scripts/telnyx_webhook_test.sh
```

## Conversation memory and insights

Every processed turn is persisted in Postgres and can be queried from `family-api`:

- `GET /v1/dashboard/{user_id}/history` -> recent-first turn history (user transcript + Thalpo reply + analysis)
- `GET /v1/dashboard/{user_id}/insights?days=30` -> aggregated conclusions (trends, flags, keywords, suggested actions)

## LiveKit SIP setup endpoints

Create/refresh SIP dispatch rule:

```bash
curl -s -X POST http://localhost:8000/v1/livekit/sip/dispatch \
  -H 'Content-Type: application/json' \
  -d '{}'
```

Start outbound SIP participant:

```bash
curl -s -X POST http://localhost:8000/v1/livekit/sip/call \
  -H 'Content-Type: application/json' \
  -d '{"to_number":"+3069XXXXXXXX","room_name":"thalpo-pstn-demo"}'
```

## Alert engine env (Telnyx SMS)

In `infra/env/alert-engine.env.example`:
- `TELNYX_API_KEY`
- `TELNYX_FROM`
- `TELNYX_TO`
- optional: `TELNYX_MESSAGING_PROFILE_ID`

## Notes

- If provider keys are missing, orchestrator falls back to safe/no-op behavior.
- This repo is production-shaped, but clinical deployment still needs hardening (HIPAA/GDPR, auditing, encryption key rotation, DR).
