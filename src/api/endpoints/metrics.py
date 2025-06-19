from fastapi import APIRouter

from src.metrics import get_metrics_response


router = APIRouter(tags=['Метрики'])


@router.get("/metrics")
def metrics():
    return get_metrics_response()