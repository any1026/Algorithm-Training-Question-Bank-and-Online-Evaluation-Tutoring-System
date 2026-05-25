import json
import logging
import time

from sqlalchemy.orm import selectinload

from app.core.database import SessionLocal, init_db
from app.core.redis import get_redis
from app.models.problem import Problem
from app.models.submission import Submission
from app.services.judge import judge_submission
from app.services.submissions import SUBMISSION_QUEUE, mark_submission

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def run_worker() -> None:
    init_db()
    redis = get_redis()
    logger.info("Judge worker started. queue=%s", SUBMISSION_QUEUE)

    while True:
        item = redis.blpop(SUBMISSION_QUEUE, timeout=5)
        if item is None:
            continue
        _, raw_payload = item
        try:
            payload = json.loads(raw_payload)
            submission_id = int(payload["submission_id"])
            _judge_one(submission_id)
        except Exception:
            logger.exception("Failed to judge payload: %s", raw_payload)
            time.sleep(1)


def _judge_one(submission_id: int) -> None:
    with SessionLocal() as db:
        submission = db.get(
            Submission,
            submission_id,
            options=[
                selectinload(Submission.problem).selectinload(Problem.test_cases),
            ],
        )
        if submission is None:
            logger.warning("Submission %s not found", submission_id)
            return

        try:
            result = judge_submission(submission, db)
            logger.info("Submission %s judged: %s", result.id, result.status)
        except Exception as exc:
            logger.exception("Submission %s failed", submission_id)
            mark_submission(submission, db, status="RE", score=0, error_message=str(exc)[:1000])


if __name__ == "__main__":
    run_worker()
