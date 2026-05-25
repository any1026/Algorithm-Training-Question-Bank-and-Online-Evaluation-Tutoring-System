from datetime import datetime

from pydantic import BaseModel, Field


class TagRead(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class TestCaseBase(BaseModel):
    input_data: str
    expected_output: str
    is_sample: bool = False
    sort_order: int = 0


class TestCaseCreate(TestCaseBase):
    __test__ = False

    pass


class TestCaseRead(TestCaseBase):
    id: int

    model_config = {"from_attributes": True}


class ProblemBase(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    difficulty: str = Field(default="easy", pattern="^(easy|medium|hard)$")
    description: str
    input_description: str
    output_description: str
    constraints: str = ""
    sample_input: str = ""
    sample_output: str = ""


class ProblemCreate(ProblemBase):
    tags: list[str] = []
    test_cases: list[TestCaseCreate] = []


class ProblemUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=120)
    difficulty: str | None = Field(default=None, pattern="^(easy|medium|hard)$")
    description: str | None = None
    input_description: str | None = None
    output_description: str | None = None
    constraints: str | None = None
    sample_input: str | None = None
    sample_output: str | None = None
    tags: list[str] | None = None


class ProblemListItem(BaseModel):
    id: int
    title: str
    difficulty: str
    tags: list[TagRead] = []
    created_at: datetime

    model_config = {"from_attributes": True}


class ProblemRead(ProblemBase):
    id: int
    tags: list[TagRead] = []
    test_cases: list[TestCaseRead] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
