
#!/usr/bin/env bash
set -Eeuo pipefail

export DATA_DIR="${DATA_DIR:-/tmp/data}"
export MLFLOW_TRACKING_URI="${MLFLOW_TRACKING_URI:-http://127.0.0.1:5000}"
export MODEL_URI="${MODEL_URI:-models:/SmartFoodDemandModel/1}"

mkdir -p "$DATA_DIR" "$DATA_DIR/mlflow-artifacts"

echo "Starting MLflow..."

mlflow server \
  --host 127.0.0.1 \
  --port 5000 \
  --backend-store-uri "sqlite:///$DATA_DIR/mlflow.db" \
  --artifacts-destination "$DATA_DIR/mlflow-artifacts" \
  > "$DATA_DIR/mlflow.log" 2>&1 &

MLFLOW_PID=$!
BACKEND_PID=""

cleanup() {
  echo "Stopping application processes..."
  if [[ -n "$BACKEND_PID" ]]; then
    kill "$BACKEND_PID" 2>/dev/null || true
  fi
  kill "$MLFLOW_PID" 2>/dev/null || true
}

trap cleanup EXIT INT TERM

echo "Waiting for MLflow to become healthy..."

MLFLOW_READY=0

for attempt in $(seq 1 60); do
  if ! kill -0 "$MLFLOW_PID" 2>/dev/null; then
    echo "ERROR: MLflow exited unexpectedly."
    cat "$DATA_DIR/mlflow.log"
    exit 1
  fi

  if python -c \
    "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/health', timeout=2)" \
    >/dev/null 2>&1; then
    MLFLOW_READY=1
    break
  fi

  sleep 2
done

if [[ "$MLFLOW_READY" -ne 1 ]]; then
  echo "ERROR: MLflow did not become healthy."
  cat "$DATA_DIR/mlflow.log"
  exit 1
fi

echo "MLflow is ready. Registering candidate model..."

python /app/deployment/mlflow_bootstrap.py

echo "Starting FastAPI..."

uvicorn app.main:app \
  --host 127.0.0.1 \
  --port 8000 &

BACKEND_PID=$!

echo "Starting Streamlit..."

streamlit run app/streamlit_app.py \
  --server.address 0.0.0.0 \
  --server.port "${PORT:-10000}" \
  --server.headless true \
  --server.fileWatcherType none
