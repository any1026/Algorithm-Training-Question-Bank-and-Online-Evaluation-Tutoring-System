from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.common import PageMeta
from app.schemas.problem import ProblemCreate, ProblemListItem, ProblemRead, ProblemUpdate, TestCaseCreate, TestCaseRead
from app.services import problems as problem_service
from app.services.testcases import add_test_case, delete_test_case

router = APIRouter(prefix="/problems", tags=["problems"])


@router.post("", response_model=ProblemRead, status_code=status.HTTP_201_CREATED)
def create_problem(payload: ProblemCreate, db: Session = Depends(get_db)) -> ProblemRead:
    return problem_service.create_problem(payload, db)


@router.get("")
def list_problems(
    keyword: str | None = None,
    difficulty: str | None = Query(default=None, pattern="^(easy|medium|hard)$"),
    tag: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    items, total = problem_service.list_problems(
        db,
        keyword=keyword,
        difficulty=difficulty,
        tag=tag,
        limit=limit,
        offset=offset,
    )
    return {
        "items": [ProblemListItem.model_validate(item) for item in items],
        "meta": PageMeta(total=total, limit=limit, offset=offset),
    }


@router.get("/{problem_id}", response_model=ProblemRead)
def get_problem(problem_id: int, db: Session = Depends(get_db)) -> ProblemRead:
    problem = problem_service.get_problem(problem_id, db)
    if problem is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")
    return problem


@router.patch("/{problem_id}", response_model=ProblemRead)
def update_problem(problem_id: int, payload: ProblemUpdate, db: Session = Depends(get_db)) -> ProblemRead:
    problem = problem_service.get_problem(problem_id, db)
    if problem is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")
    return problem_service.update_problem(problem, payload, db)


@router.delete("/{problem_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_problem(problem_id: int, db: Session = Depends(get_db)) -> None:
    problem = problem_service.get_problem(problem_id, db)
    if problem is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")
    problem_service.delete_problem(problem, db)


@router.post("/{problem_id}/test-cases", response_model=TestCaseRead, status_code=status.HTTP_201_CREATED)
def create_test_case(problem_id: int, payload: TestCaseCreate, db: Session = Depends(get_db)) -> TestCaseRead:
    problem = problem_service.get_problem(problem_id, db)
    if problem is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")
    return add_test_case(problem, payload, db)


@router.delete("/{problem_id}/test-cases/{test_case_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_test_case(problem_id: int, test_case_id: int, db: Session = Depends(get_db)) -> None:
    problem = problem_service.get_problem(problem_id, db)
    if problem is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")
    if not delete_test_case(problem_id, test_case_id, db):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test case not found")
