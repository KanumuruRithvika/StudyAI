from datetime import datetime

from sqlalchemy.orm import Session

from models.database_models import (
    LearningSession,
    QuizAttempt,
    TaskAttempt,
    User,
)


def create_user(
    db: Session,
    user_id: str,
    name: str,
    email: str,
    password_hash: str,
) -> User:
    """Create and persist a new user."""
    user = User(
        id=user_id,
        name=name.strip(),
        email=email.lower().strip(),
        password_hash=password_hash,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def get_user_by_email(
    db: Session,
    email: str,
) -> User | None:
    """Find a user by normalized email address."""
    return (
        db.query(User)
        .filter(
            User.email == email.lower().strip()
        )
        .first()
    )


def get_user(
    db: Session,
    user_id: str,
) -> User | None:
    """Find a user by ID."""
    return db.get(
        User,
        user_id,
    )


def create_learning_session(
    db: Session,
    session_id: str,
    user_id: str,
    learning_mode: str,
    goal: str,
) -> LearningSession:
    """Create a learning session for an existing user."""
    user = get_user(db, user_id)
    if not user:
        user = create_user(
            db=db,
            user_id=user_id,
            name="Learner",
            email=f"{user_id}@studyai.local",
            password_hash="auto_generated_hash",
        )

    session = LearningSession(
        id=session_id,
        user_id=user_id,
        learning_mode=learning_mode,
        goal=goal,
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return session


def get_learning_session(
    db: Session,
    session_id: str,
) -> LearningSession | None:
    """Find a learning session by ID."""
    return db.get(
        LearningSession,
        session_id,
    )


def get_user_sessions(
    db: Session,
    user_id: str,
) -> list[LearningSession]:
    """Return all learning sessions for a user."""
    return (
        db.query(LearningSession)
        .filter(
            LearningSession.user_id == user_id
        )
        .order_by(
            LearningSession.created_at.desc()
        )
        .all()
    )


def update_session_progress(
    db: Session,
    session_id: str,
    current_topic: str | None,
    progress_percent: float,
) -> LearningSession | None:
    """Update the persisted progress of a learning session."""
    session = get_learning_session(
        db,
        session_id,
    )

    if not session:
        return None

    session.current_topic = current_topic
    session.progress_percent = max(
        0.0,
        min(
            float(progress_percent),
            100.0,
        ),
    )
    session.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(session)

    return session


def complete_session(
    db: Session,
    session_id: str,
) -> LearningSession | None:
    """Mark a learning session as completed."""
    session = get_learning_session(
        db,
        session_id,
    )

    if not session:
        return None

    session.status = "completed"
    session.progress_percent = 100.0
    session.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(session)

    return session


def save_task_attempt(
    db: Session,
    session_id: str,
    task_id: str,
    completed: bool,
    notes: str | None = None,
) -> TaskAttempt:
    """Persist a learner's task attempt."""
    attempt = TaskAttempt(
        session_id=session_id,
        task_id=task_id,
        completed=completed,
        notes=notes,
        completed_at=(
            datetime.utcnow()
            if completed
            else None
        ),
    )

    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    return attempt


def save_quiz_attempt(
    db: Session,
    session_id: str,
    topic: str,
    score: float,
    total_questions: int,
) -> QuizAttempt:
    """Persist a completed quiz attempt."""
    attempt = QuizAttempt(
        session_id=session_id,
        topic=topic,
        score=float(score),
        total_questions=max(
            0,
            int(total_questions),
        ),
    )

    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    return attempt


def get_task_attempts(
    db: Session,
    session_id: str,
) -> list[TaskAttempt]:
    """Return task history for a learning session."""
    return (
        db.query(TaskAttempt)
        .filter(
            TaskAttempt.session_id == session_id
        )
        .order_by(
            TaskAttempt.id.asc()
        )
        .all()
    )


def get_quiz_attempts(
    db: Session,
    session_id: str,
) -> list[QuizAttempt]:
    """Return quiz history for a learning session."""
    return (
        db.query(QuizAttempt)
        .filter(
            QuizAttempt.session_id == session_id
        )
        .order_by(
            QuizAttempt.id.asc()
        )
        .all()
    )