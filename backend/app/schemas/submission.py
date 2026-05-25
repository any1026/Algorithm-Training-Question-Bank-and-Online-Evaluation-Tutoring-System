from datetime import datetime

from pydantic import BaseModel, Field


class SubmissionCreate(BaseModel):
    problem_id: int
    language: str = Field(pattern="^(python|cpp)$")
    code: str = Field(min_length=1)


class SubmissionRead(BaseModel):
    id: int
    problem_id: int
    language: str
    status: str
    score: int
    time_ms: int | None
    memory_kb: int | None
    error_message: str | None
    created_at: datetime
    judged_at: datetime | None

    model_config = {"from_attributes": True}


class SubmissionDetail(SubmissionRead):
    code: str


class SubmissionStats(BaseModel):
    total: int
    accepted: int
    wrong_answer: int
    compile_error: int
    runtime_error: int
    time_limit_exceeded: int
    pending: int
