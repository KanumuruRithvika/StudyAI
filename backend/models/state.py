from typing import Any, Literal, TypedDict


class LearningState(TypedDict, total=False):
    # Session and authentication context
    session_id: str
    user_id: str

    # Learning request
    learning_mode: Literal["general", "project"]
    goal: str
    current_level: str
    available_time_minutes: int
    duration_days: int

    # Project context
    role: str
    project_name: str
    project_description: str
    current_skills: list[str]
    required_technologies: list[str]

    # Optional learning preferences
    learning_preferences: str
    prior_experience: str
    additional_instructions: str

    # Project skill-gap analysis
    skill_gaps: list[dict[str, Any]]

    # Structured learning roadmap
    plan: dict[str, Any]
    plan_approved: bool
    plan_feedback: str

    # Current learning position
    current_topic_index: int
    current_topic: str
    current_day: int
    day_started_at: str

    # Daily task management
    tasks: list[dict[str, Any]]
    completed_tasks: list[str]
    unfinished_tasks: list[str]
    skipped_tasks: list[str]
    carried_forward_tasks: list[dict[str, Any]]
    task_progress: float
    last_task_update: dict[str, Any]

    # Detailed learning content for the current task
    task_details: dict[str, Any]
    learning_content: dict[str, Any]

    # Quiz state
    quiz: list[dict[str, Any]]
    quiz_answers: list[dict[str, str]]
    quiz_score: float
    quiz_history: list[dict[str, Any]]

    # Topic-level performance
    strong_topics: list[str]
    medium_topics: list[str]
    weak_topics: list[str]
    topic_performance: dict[str, Any]

    # Adaptive learning
    adaptive_action: Literal[
        "move_forward",
        "improve_weak_topics",
    ]
    adaptive_recommendation: str
    adaptation_requested: bool
    improvement_days: int
    improvement_time_minutes: int
    improvement_description: str

    # Overall learning analytics
    study_time_minutes: int
    current_streak: int
    learning_history: list[dict[str, Any]]

    # Workflow completion flags
    topic_completed: bool
    goal_completed: bool

    # Final readiness report
    readiness_report: dict[str, Any]