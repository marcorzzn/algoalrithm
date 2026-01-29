from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
import time

# Metrics
PREDICTION_COUNTER = Counter(
    'ml_predictions_total', 
    'Total predictions made',
    ['model_version', 'outcome']
)

PREDICTION_LATENCY = Histogram(
    'ml_prediction_duration_seconds',
    'Time spent on prediction',
    ['model_type']
)

ACTIVE_BETS = Gauge(
    'active_value_bets',
    'Number of active value bets detected'
)

API_REQUESTS = Counter(
    'api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status']
)

def track_prediction(model_version: str, outcome: str):
    PREDICTION_COUNTER.labels(
        model_version=model_version,
        outcome=outcome
    ).inc()

def track_latency(model_type: str, duration: float):
    PREDICTION_LATENCY.labels(model_type=model_type).observe(duration)

@app.get("/metrics")
async def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )