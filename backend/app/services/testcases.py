from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.problem import Problem
from app.models.testcase import TestCase
from app.schemas.problem import TestCaseCreate


def add_test_case(problem: Problem, payload: TestCaseCreate, db: Session) -> TestCase:
    test_case = TestCase(
        problem_id=problem.id,
        input_data=payload.input_data,
        expected_output=payload.expected_output,
        is_sample=payload.is_sample,
        sort_order=payload.sort_order,
    )
    db.add(test_case)
    db.commit()
    db.refresh(test_case)
    return test_case


def delete_test_case(problem_id: int, test_case_id: int, db: Session) -> bool:
    test_case = db.scalar(select(TestCase).where(TestCase.id == test_case_id, TestCase.problem_id == problem_id))
    if test_case is None:
        return False
    db.delete(test_case)
    db.commit()
    return True
