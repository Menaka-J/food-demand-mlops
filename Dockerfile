
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV DATA_DIR=/var/data
ENV MLFLOW_TRACKING_URI=http://127.0.0.1:5000
ENV MODEL_URI=models:/SmartFoodDemandModel/1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt

RUN python -m pip install --upgrade pip \
    && pip install -r /app/requirements.txt

COPY app/ /app/app/
COPY models/ /app/models/
COPY data/ /app/data/
COPY deployment/ /app/deployment/
COPY render-start.sh /app/render-start.sh

RUN sed -i 's/\r$//' /app/render-start.sh \
    && chmod +x /app/render-start.sh \
    && mkdir -p /var/data/mlflow-artifacts

EXPOSE 10000

CMD ["bash", "/app/render-start.sh"]