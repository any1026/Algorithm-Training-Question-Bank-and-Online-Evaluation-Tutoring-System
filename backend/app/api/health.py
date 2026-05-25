from fastapi import APIRouter

from app.core.config import get_settings
from app.schemas.common import HealthRead

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthRead)
def health() -> HealthRead:
    return HealthRead(status="ok", app=get_settings().app_name)
