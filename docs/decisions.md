# Decisions Log

| Date | Decision | Why | Owner |
| --- | --- | --- | --- |
| 2026-02-26 | Use service boundaries (orchestrator, analysis, alert, dashboard API) from day 1 | Mirrors target architecture and allows independent scaling | Team |
| 2026-02-26 | Keep analysis non-blocking and off user response path | Preserves conversational latency | Team |
| 2026-02-26 | Start with rule-based alerting before ML policy | Faster validation with clinicians and caregivers | Team |
| 2026-02-26 | Share Pydantic contracts across services | Prevents schema drift and integration bugs | Team |
