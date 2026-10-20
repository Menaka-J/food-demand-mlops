
import os
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

import joblib
import mlflow
import mlflow.sklearn
from mlflow import MlflowClient
from mlflow.exceptions import MlflowException


TRACKING_URI = os.getenv(
    "MLFLOW_TRACKING_URI",
    "http://127.0.0.1:5000",
)

MODEL_NAME = "SmartFoodDemandModel"
EXPERIMENT_NAME = "Smart Food Demand Forecasting"
MODEL_PATH = Path("/app/models/candidate_model.joblib")


def wait_for_mlflow():
    for attempt in range(60):
        try:
            with urlopen(
                f"{TRACKING_URI}/health",
                timeout=3,
            ) as response:
                if response.status == 200:
                    print("MLflow server is ready.")
                    return
        except (URLError, TimeoutError, OSError):
            pass

        print(f"Waiting for MLflow... {attempt + 1}/60")
        time.sleep(2)

    raise RuntimeError("MLflow server did not become ready.")


def main():
    wait_for_mlflow()

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Candidate model not found: {MODEL_PATH}"
        )

    mlflow.set_tracking_uri(TRACKING_URI)
    client = MlflowClient()

    try:
        registered = client.get_registered_model(MODEL_NAME)

        if registered.latest_versions:
            print(
                f"{MODEL_NAME} is already registered. "
                "Keeping the existing registry."
            )
            return

    except MlflowException:
        pass

    experiment = client.get_experiment_by_name(EXPERIMENT_NAME)

    if experiment is None:
        experiment_id = client.create_experiment(EXPERIMENT_NAME)
    else:
        experiment_id = experiment.experiment_id

    mlflow.set_experiment(experiment_id=experiment_id)

    model = joblib.load(MODEL_PATH)

    with mlflow.start_run(
        run_name="Render Deployment - Candidate Model"
    ):
        mlflow.log_param("model_source", "candidate_model.joblib")
        mlflow.log_param("deployment_platform", "Render")
        mlflow.log_param("deployment_method", "Docker")

        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="model",
            registered_model_name=MODEL_NAME,
        )

    print(f"Registered model: {MODEL_NAME}")


if __name__ == "__main__":
    main()
