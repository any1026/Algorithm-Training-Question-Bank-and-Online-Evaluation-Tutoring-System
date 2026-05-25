from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.models.problem import Problem
from app.models.tag import Tag
from app.models.testcase import TestCase
from app.schemas.problem import ProblemCreate, ProblemUpdate


def _normalize_tags(tag_names: list[str], db: Session) -> list[Tag]:
    clean_names = sorted({name.strip() for name in tag_names if name.strip()})
    if not clean_names:
        return []

    existing = db.scalars(select(Tag).where(Tag.name.in_(clean_names))).all()
    existing_by_name = {tag.name: tag for tag in existing}
    tags: list[Tag] = []
    for name in clean_names:
        tag = existing_by_name.get(name)
        if tag is None:
            tag = Tag(name=name)
            db.add(tag)
        tags.append(tag)
    return tags


def create_problem(payload: ProblemCreate, db: Session) -> Problem:
    problem = Problem(
        title=payload.title,
        difficulty=payload.difficulty,
        description=payload.description,
        input_description=payload.input_description,
        output_description=payload.output_description,
        constraints=payload.constraints,
        sample_input=payload.sample_input,
        sample_output=payload.sample_output,
    )
    problem.tags = _normalize_tags(payload.tags, db)
    problem.test_cases = [
        TestCase(
            input_data=item.input_data,
            expected_output=item.expected_output,
            is_sample=item.is_sample,
            sort_order=item.sort_order,
        )
        for item in payload.test_cases
    ]
    db.add(problem)
    db.commit()
    db.refresh(problem)
    return problem


def update_problem(problem: Problem, payload: ProblemUpdate, db: Session) -> Problem:
    data = payload.model_dump(exclude_unset=True)
    tag_names = data.pop("tags", None)
    for key, value in data.items():
        setattr(problem, key, value)
    if tag_names is not None:
        problem.tags = _normalize_tags(tag_names, db)
    db.add(problem)
    db.commit()
    db.refresh(problem)
    return problem


def get_problem(problem_id: int, db: Session) -> Problem | None:
    return db.get(Problem, problem_id)


def list_problems(
    db: Session,
    *,
    keyword: str | None = None,
    difficulty: str | None = None,
    tag: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[Problem], int]:
    stmt: Select[tuple[Problem]] = select(Problem)
    count_stmt = select(func.count(Problem.id))

    if keyword:
        pattern = f"%{keyword}%"
        stmt = stmt.where(Problem.title.like(pattern))
        count_stmt = count_stmt.where(Problem.title.like(pattern))
    if difficulty:
        stmt = stmt.where(Problem.difficulty == difficulty)
        count_stmt = count_stmt.where(Problem.difficulty == difficulty)
    if tag:
        stmt = stmt.join(Problem.tags).where(Tag.name == tag)
        count_stmt = count_stmt.join(Problem.tags).where(Tag.name == tag)

    total = db.scalar(count_stmt) or 0
    items = db.scalars(stmt.order_by(Problem.id.desc()).limit(limit).offset(offset)).unique().all()
    return list(items), total


def delete_problem(problem: Problem, db: Session) -> None:
    db.delete(problem)
    db.commit()
