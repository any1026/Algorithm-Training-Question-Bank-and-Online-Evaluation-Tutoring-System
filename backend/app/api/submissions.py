from fastapi import APIRouter, Depends, HTTPException, Query, status
from redis import Redis
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.redis import get_redis
from app.schemas.common import PageMeta
from app.schemas.submission import SubmissionCreate, SubmissionDetail, SubmissionRead, SubmissionStats
from app.services import submissions as submission_service

router = APIRouter(prefix="/submissions", tags=["submissions"])


@router.post("", response_model=SubmissionRead, status_code=status.HTTP_201_CREATED)
def create_submission(
    payload: SubmissionCreate,
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> SubmissionRead:
    try:
        return submission_service.create_submission(payload, db, redis)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("")
def list_submissions(
    problem_id: int | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    items, total = submission_service.list_submissions(db, problem_id=problem_id, limit=limit, offset=offset)
    return {
        "items": [SubmissionRead.model_validate(item) for item in items],
        "meta": PageMeta(total=total, limit=limit, offset=offset),
    }


@router.get("/stats", response_model=SubmissionStats)
def get_stats(db: Session = Depends(get_db)) -> SubmissionStats:
    return submission_service.get_stats(db)


@router.get("/{submission_id}", response_model=SubmissionDetail)
def get_submission(submission_id: int, db: Session = Depends(get_db)) -> SubmissionDetail:
    submission = submission_service.get_submission(submission_id, db)
    if submission is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")
    return submission
