import mlflow
import mlflow.sklearn


MODEL_URI = "models:/SmartFoodDemandModel/1"

mlflow.set_tracking_uri(
    "sqlite:///C:/Users/Menaka/Videos/smart-food-demand-mlops/mlflow.db"
)

model = mlflow.sklearn.load_model(MODEL_URI)


def predict(features):
    prediction = model.predict(features)

    return float(prediction[0])