#!/usr/bin/env bash
set -euo pipefail

ORCH_URL="${ORCH_URL:-http://localhost:8000}"
CALL_CONTROL_ID="${CALL_CONTROL_ID:-v2:test-call-control-id}"
CALL_SESSION_ID="${CALL_SESSION_ID:-call-session-001}"
FROM_NUMBER="${FROM_NUMBER:-+306900000000}"
TO_NUMBER="${TO_NUMBER:-+302100000000}"


echo "[1/3] Simulate call.initiated"
curl -s -X POST "$ORCH_URL/v1/telnyx/webhook" \
  -H 'Content-Type: application/json' \
  -d "{
    \"data\": {
      \"id\": \"evt-001\",
      \"event_type\": \"call.initiated\",
      \"payload\": {
        \"call_control_id\": \"$CALL_CONTROL_ID\",
        \"call_session_id\": \"$CALL_SESSION_ID\",
        \"from\": \"$FROM_NUMBER\",
        \"to\": \"$TO_NUMBER\"
      }
    }
  }"

echo
echo "[2/3] Simulate call.answered"
curl -s -X POST "$ORCH_URL/v1/telnyx/webhook" \
  -H 'Content-Type: application/json' \
  -d "{
    \"data\": {
      \"id\": \"evt-002\",
      \"event_type\": \"call.answered\",
      \"payload\": {
        \"call_control_id\": \"$CALL_CONTROL_ID\",
        \"call_session_id\": \"$CALL_SESSION_ID\",
        \"from\": \"$FROM_NUMBER\",
        \"to\": \"$TO_NUMBER\"
      }
    }
  }"

echo
echo "[3/3] Simulate final transcription"
curl -s -X POST "$ORCH_URL/v1/telnyx/webhook" \
  -H 'Content-Type: application/json' \
  -d "{
    \"data\": {
      \"id\": \"evt-003\",
      \"event_type\": \"call.transcription\",
      \"payload\": {
        \"call_control_id\": \"$CALL_CONTROL_ID\",
        \"call_session_id\": \"$CALL_SESSION_ID\",
        \"from\": \"$FROM_NUMBER\",
        \"to\": \"$TO_NUMBER\",
        \"transcription_data\": {
          \"transcript\": \"Καλημέρα, πώς είσαι σήμερα;\",
          \"is_final\": true
        }
      }
    }
  }"

echo
echo "Telnyx webhook simulation finished"
