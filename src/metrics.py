from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response


REQUEST_COUNT = Counter('app_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'http_status'])
REQUEST_LATENCY = Histogram('app_request_latency_seconds', 'Request latency', ['method', 'endpoint'])
ERROR_COUNT = Counter('app_errors_total', 'Total HTTP errors', ['method', 'endpoint', 'http_status'])


def get_metrics_response():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
