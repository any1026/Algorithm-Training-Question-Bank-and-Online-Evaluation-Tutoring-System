from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(40), unique=True, nullable=False, index=True)

    problems: Mapped[list["Problem"]] = relationship(  # noqa: F821
        secondary="problem_tags",
        back_populates="tags",
    )
