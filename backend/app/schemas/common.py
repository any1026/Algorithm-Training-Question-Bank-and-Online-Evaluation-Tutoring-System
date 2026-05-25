from pydantic import BaseModel


class HealthRead(BaseModel):
    status: str
    app: str


class PageMeta(BaseModel):
    total: int
    limit: int
    offset: int


class PageResponse[T](BaseModel):
    items: list[T]
    meta: PageMeta
