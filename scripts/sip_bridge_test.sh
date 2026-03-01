#!/usr/bin/env bash
set -euo pipefail

ORCH_URL="${ORCH_URL:-http://localhost:8000}"
CALL_ID="${CALL_ID:-CALL_TEST_001}"
FROM_NUMBER="${FROM_NUMBER:-+306900000000}"

echo "[1/2] Simulate PSTN call start (Telnyx + LiveKit SIP adapter)"
curl -s -X POST "$ORCH_URL/v1/pstn/start" \
  -H 'Content-Type: application/json' \
  -d "{\"call_id\":\"$CALL_ID\",\"from_number\":\"$FROM_NUMBER\"}"

echo
echo "[2/2] Simulate speech turn"
curl -s -X POST "$ORCH_URL/v1/pstn/turn" \
  -H 'Content-Type: application/json' \
  -d "{\"call_id\":\"$CALL_ID\",\"from_number\":\"$FROM_NUMBER\",\"speech_text\":\"Καλημέρα, ξέχασα τα φάρμακά μου\"}"

echo
echo "PSTN SIP simulation finished"
