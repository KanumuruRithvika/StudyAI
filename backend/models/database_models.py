from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
    )
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )


class LearningSession(Base):
    __tablename__ = "learning_sessions"

    id: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
    )
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id"),
        index=True,
    )
    learning_mode: Mapped[str] = mapped_column(String(20))
    goal: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(
        String(30),
        default="active",
    )
    current_topic: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )
    progress_percent: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )


class TaskAttempt(Base):
    __tablename__ = "task_attempts"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )
    session_id: Mapped[str] = mapped_column(
        ForeignKey("learning_sessions.id"),
        index=True,
    )
    task_id: Mapped[str] = mapped_column(String(100))
    completed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )
    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )
    session_id: Mapped[str] = mapped_column(
        ForeignKey("learning_sessions.id"),
        index=True,
    )
    topic: Mapped[str] = mapped_column(String(200))
    score: Mapped[float] = mapped_column(Float)
    total_questions: Mapped[int] = mapped_column()
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )