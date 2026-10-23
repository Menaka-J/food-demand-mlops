
#!/usr/bin/env bash
set -Eeuo pipefail

echo "Starting FastAPI..."

uvicorn app.main:app \
  --host 127.0.0.1 \
  --port 8000 &
BACKEND_PID=$!

cleanup() {
  echo "Stopping FastAPI..."
  kill "$BACKEND_PID" 2>/dev/null || true
}

trap cleanup EXIT INT TERM

echo "Starting Streamlit..."

streamlit run app/streamlit_app.py \
  --server.address 0.0.0.0 \
  --server.port "${PORT:-10000}" \
  --server.headless true \
  --server.fileWatcherType none
