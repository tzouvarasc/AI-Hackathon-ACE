#!/usr/bin/env bash
set -euo pipefail

ORCH_URL="${ORCH_URL:-http://localhost:8000}"
FAMILY_URL="${FAMILY_URL:-http://localhost:8003}"

echo "[1/5] Start session"
SESSION_JSON=$(curl -s -X POST "$ORCH_URL/v1/sessions/start" \
  -H 'Content-Type: application/json' \
  -d '{"user_id":"demo-user","channel":"pstn"}')

SESSION_ID=$(echo "$SESSION_JSON" | sed -n 's/.*"session_id":"\([^"]*\)".*/\1/p')
if [[ -z "$SESSION_ID" ]]; then
  echo "Failed to create session"
  echo "$SESSION_JSON"
  exit 1
fi

echo "Session: $SESSION_ID"

echo "[2/5] Process turn"
curl -s -X POST "$ORCH_URL/v1/turns/process" \
  -H 'Content-Type: application/json' \
  -d "{\"session_id\":\"$SESSION_ID\",\"user_id\":\"demo-user\",\"raw_text\":\"I forgot my pills and feel afraid\",\"audio_features\":{\"stress\":0.8}}" | cat

echo
echo "[3/5] Login family API"
LOGIN_JSON=$(curl -s -X POST "$FAMILY_URL/v1/auth/login" \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin123"}')
TOKEN=$(echo "$LOGIN_JSON" | sed -n 's/.*"access_token":"\([^"]*\)".*/\1/p')
if [[ -z "$TOKEN" ]]; then
  echo "Failed to login"
  echo "$LOGIN_JSON"
  exit 1
fi

echo "[4/5] Fetch dashboard"
curl -s "$FAMILY_URL/v1/dashboard/demo-user" \
  -H "Authorization: Bearer $TOKEN" | cat

echo
echo "[5/5] Fetch history"
curl -s "$FAMILY_URL/v1/dashboard/demo-user/history?limit=5" \
  -H "Authorization: Bearer $TOKEN" | cat

echo
echo "Smoke test finished"
