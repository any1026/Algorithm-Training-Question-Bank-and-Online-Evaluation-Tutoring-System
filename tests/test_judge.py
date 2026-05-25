import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.submission import Submission
from app.schemas.problem import ProblemCreate, TestCaseCreate
from app.services.judge import judge_submission
from app.services.problems import create_problem


def make_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal()


def test_python_submission_is_accepted():
    db = make_session()
    problem = create_problem(
        ProblemCreate(
            title="A + B",
            difficulty="easy",
            description="sum",
            input_description="a b",
            output_description="a+b",
            test_cases=[TestCaseCreate(input_data="1 2\n", expected_output="3\n")],
        ),
        db,
    )
    submission = Submission(
        problem_id=problem.id,
        problem=problem,
        language="python",
        code="a,b=map(int,input().split())\nprint(a+b)\n",
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)

    result = judge_submission(submission, db)
    assert result.status == "AC"
    assert result.score == 100


def test_wrong_answer_is_reported():
    db = make_session()
    problem = create_problem(
        ProblemCreate(
            title="A + B",
            difficulty="easy",
            description="sum",
            input_description="a b",
            output_description="a+b",
            test_cases=[TestCaseCreate(input_data="1 2\n", expected_output="3\n")],
        ),
        db,
    )
    submission = Submission(problem_id=problem.id, problem=problem, language="python", code="print(4)\n")
    db.add(submission)
    db.commit()
    db.refresh(submission)

    result = judge_submission(submission, db)
    assert result.status == "WA"


def test_cpp_submission_is_accepted_when_compiler_available():
    db = make_session()
    problem = create_problem(
        ProblemCreate(
            title="A + B",
            difficulty="easy",
            description="sum",
            input_description="a b",
            output_description="a+b",
            test_cases=[TestCaseCreate(input_data="1 2\n", expected_output="3\n")],
        ),
        db,
    )
    code = "#include <bits/stdc++.h>\nusing namespace std;int main(){long long a,b;cin>>a>>b;cout<<a+b<<'\\n';}\n"
    submission = Submission(problem_id=problem.id, problem=problem, language="cpp", code=code)
    db.add(submission)
    db.commit()
    db.refresh(submission)

    result = judge_submission(submission, db)
    if sys.platform.startswith("win"):
        assert result.status in {"AC", "CE"}
    else:
        assert result.status == "AC"
