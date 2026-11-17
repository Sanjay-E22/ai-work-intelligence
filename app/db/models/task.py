
from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    assignee: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    deadline: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    dependencies: Mapped[list] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    priority: Mapped[str] = mapped_column(
        String(20),
        default="unknown",
        nullable=False,
    )

    execution_status: Mapped[str] = mapped_column(
        String(30),
        default="ready",
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
