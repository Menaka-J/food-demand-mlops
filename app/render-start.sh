
#!/usr/bin/env bash
set -Eeuo pipefail

export DATA_DIR="${DATA_DIR:-/var/data}"
export MLFLOW_TRACKING_URI="${MLFLOW_TRACKING_URI:-http://127.0.0.1:5000}"
export MODEL_URI="${MODEL_URI:-models:/SmartFoodDemandModel/1}"
export DATABASE_URL="${DATABASE_URL:-sqlite:////var/data/app.db}"
export CALIBRATION_PATH="${CALIBRATION_PATH:-/var/data/operational_calibration.json}"

mkdir -p "$DATA_DIR" "$DATA_DIR/mlflow-artifacts"

echo "Starting MLflow tracking server..."

mlflow server \
  --host 127.0.0.1 \
  --port 5000 \
  --backend-store-uri sqlite:////var/data/mlflow.db \
  --artifacts-destination /var/data/mlflow-artifacts \
  > /var/data/mlflow.log 2>&1 &

MLFLOW_PID=$!

cleanup() {
  echo "Stopping application services..."
  kill "$MLFLOW_PID" "${BACKEND_PID:-}" 2>/dev/null || true
}

trap cleanup EXIT INT TERM

echo "Registering the candidate model..."
python /app/deployment/mlflow_bootstrap.py

echo "Starting FastAPI..."
uvicorn app.main:app \
  --host 127.0.0.1 \
  --port 8000 &

BACKEND_PID=$!

echo "Starting Streamlit on Render's public port..."
exec streamlit run app/streamlit_app.py \
  --server.address 0.0.0.0 \
  --server.port "${PORT:-10000}" \
  --server.headless true
