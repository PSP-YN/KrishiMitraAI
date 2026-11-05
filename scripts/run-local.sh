#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PYTHON="${PYTHON:-$ROOT/.venv/bin/python}"
if [[ ! -x "$PYTHON" ]]; then
  PYTHON="$(command -v python3 || true)"
fi
if [[ -z "$PYTHON" || ! -x "$PYTHON" ]]; then
  echo "Python 3.11–3.13 is required. Create .venv and install requirements.txt." >&2
  exit 1
fi

if ! "$PYTHON" -c 'import fastapi, strands, uvicorn' >/dev/null 2>&1; then
  echo "Application dependencies are missing. Install with: $PYTHON -m pip install -r requirements.txt" >&2
  exit 1
fi

OLLAMA_HOST="${OLLAMA_HOST:-http://127.0.0.1:11434}"
OLLAMA_MODEL="${OLLAMA_MODEL:-qwen2.5:3b}"
if ! OLLAMA_HOST="$OLLAMA_HOST" OLLAMA_MODEL="$OLLAMA_MODEL" "$PYTHON" - <<'PY'
import json, os, sys, urllib.request
host = os.environ["OLLAMA_HOST"].rstrip("/")
model = os.environ["OLLAMA_MODEL"]
try:
    with urllib.request.urlopen(host + "/api/tags", timeout=3) as response:
        models = {item.get("name") for item in json.load(response).get("models", [])}
except Exception as exc:
    print(f"Ollama is not reachable at {host}: {exc}", file=sys.stderr)
    print("Start Ollama with: ollama serve", file=sys.stderr)
    sys.exit(1)
if model not in models:
    print(f"Model {model!r} is not installed. Run: ollama pull {model}", file=sys.stderr)
    sys.exit(1)
print(f"Ollama ready · model {model}")
PY
then
  exit 1
fi

HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8000}"
echo "Starting KrishiMitra at http://$HOST:$PORT"
exec "$PYTHON" -m uvicorn main:app --host "$HOST" --port "$PORT"
