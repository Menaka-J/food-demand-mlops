
#!/usr/bin/env bash
set -Eeuo pipefail

export DATA_DIR="${DATA_DIR:-/tmp/data}"
export MLFLOW_TRACKING_URI="${MLFLOW_TRACKING_URI:-http://127.0.0.1:5000}"
export MODEL_URI="${MODEL_URI:-models:/SmartFoodDemandModel/1}"
export DATABASE_URL="${DATABASE_URL:-sqlite:////tmp/data/app.db}"
export CALIBRATION_PATH="${CALIBRATION_PATH:-/tmp/data/operational_calibration.json}"

mkdir -p "$DATA_DIR" "$DATA_DIR/mlflow-artifacts"

echo "Starting MLflow..."

mlflow server \
  --host 127.0.0.1 \
  --port 5000 \
  --backend-store-uri "sqlite:///$DATA_DIR/mlflow.db" \
    --artifacts-destination "$DATA_DIR/mlflow-artifacts" \
  2>&1 | tee "$DATA_DIR/mlflow.log" &

MLFLOW_PID=$!

cleanup() {
  kill "$MLFLOW_PID" "${BACKEND_PID:-}" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo "Registering candidate model..."
python /app/deployment/mlflow_bootstrap.py

echo "Starting FastAPI..."
uvicorn app.main:app --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

echo "Starting Streamlit..."
exec streamlit run app/streamlit_app.py \
  --server.address 0.0.0.0 \
  --server.port "${PORT:-10000}" \
  --server.headless true
