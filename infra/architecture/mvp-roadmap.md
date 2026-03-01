# Thalpo MVP Roadmap

## Phase 1: Voice core

- Replace text-only input with streamed audio frames.
- Integrate LiveKit SIP bridge and PSTN/WebRTC ingress.
- Implement barge-in interruption handling.

## Phase 2: Intelligence

- Integrate Deepgram Nova-3 streaming STT for Greek.
- Integrate GPT real-time tool calling.
- Connect medication/memory tools and retrieval layer (RAG + memory).

## Phase 3: Parallel analysis

- Connect Hume expression analysis and LANGaware biomarkers.
- Expand risk scoring beyond keyword heuristics.
- Add trend scoring windows (7-day, 30-day).

## Phase 4: Alerting and care loop

- Wire SMS and escalation policies.
- Add caregiver contact routing and acknowledgement states.
- Add configurable rule engine (thresholds per user).

## Phase 5: Dashboard and operations

- Build React family dashboard UI over `family_api`.
- Add auth, audit logs, and encryption at rest.
- Add observability (traces, metrics, SLO for latency and reliability).
