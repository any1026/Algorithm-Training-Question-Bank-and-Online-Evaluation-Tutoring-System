from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


problem_tags = Table(
    "problem_tags",
    Base.metadata,
    Column("problem_id", Integer, ForeignKey("problems.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Problem(Base):
    __tablename__ = "problems"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False, default="easy")
    description: Mapped[str] = mapped_column(Text, nullable=False)
    input_description: Mapped[str] = mapped_column(Text, nullable=False)
    output_description: Mapped[str] = mapped_column(Text, nullable=False)
    constraints: Mapped[str] = mapped_column(Text, nullable=False, default="")
    sample_input: Mapped[str] = mapped_column(Text, nullable=False, default="")
    sample_output: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    tags: Mapped[list["Tag"]] = relationship(  # noqa: F821
        secondary=problem_tags,
        back_populates="problems",
        lazy="selectin",
    )
    test_cases: Mapped[list["TestCase"]] = relationship(  # noqa: F821
        back_populates="problem",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    submissions: Mapped[list["Submission"]] = relationship(  # noqa: F821
        back_populates="problem",
        cascade="all, delete-orphan",
    )
