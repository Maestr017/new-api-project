import time
from fastapi import Request
from src.metrics import REQUEST_COUNT, REQUEST_LATENCY, ERROR_COUNT


async def prometheus_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    latency = time.time() - start_time

    method = request.method
    endpoint = request.url.path
    status = str(response.status_code)

    REQUEST_COUNT.labels(method=method, endpoint=endpoint, http_status=status).inc()
    REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(latency)

    if response.status_code >= 400:
        ERROR_COUNT.labels(method=method, endpoint=endpoint, http_status=status).inc()

    return response
