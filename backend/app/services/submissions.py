import json
from datetime import UTC, datetime

from redis import Redis
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.problem import Problem
from app.models.submission import Submission
from app.schemas.submission import SubmissionCreate, SubmissionStats

SUBMISSION_QUEUE = "judge:submissions"


def create_submission(payload: SubmissionCreate, db: Session, redis: Redis) -> Submission:
    problem = db.get(Problem, payload.problem_id)
    if problem is None:
        raise ValueError("Problem not found")

    submission = Submission(
        problem_id=payload.problem_id,
        language=payload.language,
        code=payload.code,
        status="PENDING",
        score=0,
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)

    redis.rpush(SUBMISSION_QUEUE, json.dumps({"submission_id": submission.id}))
    return submission


def get_submission(submission_id: int, db: Session) -> Submission | None:
    return db.get(Submission, submission_id)


def list_submissions(db: Session, *, problem_id: int | None = None, limit: int = 20, offset: int = 0) -> tuple[list[Submission], int]:
    stmt = select(Submission)
    count_stmt = select(func.count(Submission.id))
    if problem_id is not None:
        stmt = stmt.where(Submission.problem_id == problem_id)
        count_stmt = count_stmt.where(Submission.problem_id == problem_id)

    total = db.scalar(count_stmt) or 0
    items = db.scalars(stmt.order_by(Submission.id.desc()).limit(limit).offset(offset)).all()
    return list(items), total


def mark_submission(
    submission: Submission,
    db: Session,
    *,
    status: str,
    score: int,
    time_ms: int | None = None,
    memory_kb: int | None = None,
    error_message: str | None = None,
) -> Submission:
    submission.status = status
    submission.score = score
    submission.time_ms = time_ms
    submission.memory_kb = memory_kb
    submission.error_message = error_message
    submission.judged_at = datetime.now(UTC).replace(tzinfo=None)
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission


def get_stats(db: Session) -> SubmissionStats:
    rows = db.execute(select(Submission.status, func.count(Submission.id)).group_by(Submission.status)).all()
    counts = {status: count for status, count in rows}
    return SubmissionStats(
        total=sum(counts.values()),
        accepted=counts.get("AC", 0),
        wrong_answer=counts.get("WA", 0),
        compile_error=counts.get("CE", 0),
        runtime_error=counts.get("RE", 0),
        time_limit_exceeded=counts.get("TLE", 0),
        pending=counts.get("PENDING", 0) + counts.get("RUNNING", 0),
    )
