from typing import Literal

from pydantic import BaseModel, Field, model_validator


class SignupRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=8, max_length=128)


class UserResponse(BaseModel):
    id: str
    name: str
    email: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class LearningRequest(BaseModel):
    user_id: str = "anonymous"
    learning_mode: Literal["general", "project"]

    goal: str = ""

    current_level: str = "beginner"
    available_time_minutes: int = Field(
        default=60,
        gt=0,
    )
    duration_days: int | None = None

    role: str | None = None
    project_name: str | None = None
    project_description: str | None = None

    current_skills: list[str] = Field(
        default_factory=list
    )
    required_skills: list[str] = Field(
        default_factory=list
    )
    required_technologies: list[str] = Field(
        default_factory=list
    )

    # Optional enrichment fields used by context analyzer
    learning_preferences: str | None = None
    prior_experience: str | None = None
    additional_instructions: str | None = None

    @model_validator(mode="after")
    def validate_goal_not_empty(self):
        if not self.goal or not self.goal.strip():
            # For project mode, goal can be derived from project_description
            if (
                self.learning_mode == "project"
                and self.project_description
                and self.project_description.strip()
            ):
                self.goal = self.project_description.strip()
                return self
            raise ValueError("Goal must not be empty")
        return self


class PlanApprovalRequest(BaseModel):
    approved: bool
    feedback: str | None = None


class TaskCompletionRequest(BaseModel):
    task_id: str

    status: Literal[
        "done",
        "not_done",
        "skip",
    ] | None = None

    completed: bool | None = None
    notes: str | None = None

    @model_validator(mode="after")
    def validate_task_status(self):
        if self.status is None and self.completed is None:
            raise ValueError(
                "Either 'status' or 'completed' must be provided."
            )

        if self.status is None:
            self.status = "done" if self.completed else "not_done"

        if self.completed is None:
            self.completed = self.status == "done"

        return self


class TaskUpdate(BaseModel):
    task_id: str

    status: Literal[
        "done",
        "not_done",
        "skip",
    ]

    notes: str | None = None


class DaySubmission(BaseModel):
    tasks: list[TaskUpdate]


class QuizAnswer(BaseModel):
    question_id: str
    answer: str


class QuizSubmission(BaseModel):
    answers: list[QuizAnswer]


class AdaptationRequest(BaseModel):
    action: Literal[
        "move_forward",
        "improve_weak_topics",
    ]

    available_time_minutes: int | None = Field(
        default=None,
        gt=0,
    )

    duration_days: int | None = Field(
        default=None,
        gt=0,
    )

    description: str | None = None


class LearningTopic(BaseModel):
    title: str
    description: str
    estimated_days: float | int = Field(gt=0)
    objectives: list[str] = Field(default_factory=list)


class LearningPlan(BaseModel):
    title: str
    summary: str
    topics: list[LearningTopic] = Field(default_factory=list)


class LearningTask(BaseModel):
    id: str
    title: str
    description: str

    task_type: Literal[
        "study",
        "practice",
        "project",
    ]

    estimated_minutes: float | int = Field(gt=0)
    objective: str


class TaskList(BaseModel):
    tasks: list[LearningTask] = Field(default_factory=list)


class ExternalSource(BaseModel):
    title: str
    url: str


class LearningContent(BaseModel):
    """
    Detailed learning material generated for an individual task.
    """

    title: str
    explanation: str

    learning_objective: str | None = None

    key_concepts: list[str] = Field(default_factory=list)
    step_by_step: list[str] = Field(default_factory=list)
    examples: list[str] = Field(default_factory=list)
    common_mistakes: list[str] = Field(default_factory=list)
    practice: list[str] = Field(default_factory=list)

    mini_challenge: str | None = None
    expected_outcome: str | None = None
    completion_criteria: list[str] = Field(default_factory=list)

    external_sources: list[ExternalSource] = Field(default_factory=list)


class TaskDetailsResponse(BaseModel):
    task_id: str
    topic: str
    content: LearningContent


class QuizQuestion(BaseModel):
    id: str
    question: str
    options: list[str]
    correct_answer: str
    explanation: str

    question_type: Literal[
        "mcq",
        "conceptual",
        "scenario",
        "code",
        "application",
    ] = "mcq"

    topic: str | None = None


class Quiz(BaseModel):
    questions: list[QuizQuestion] = Field(default_factory=list)


class QuizQuestionResponse(BaseModel):
    id: str
    question: str
    options: list[str]

    question_type: Literal[
        "mcq",
        "conceptual",
        "scenario",
        "code",
        "application",
    ] = "mcq"

    topic: str | None = None


class QuizResponse(BaseModel):
    questions: list[QuizQuestionResponse] = Field(default_factory=list)


class LearningResponse(BaseModel):
    session_id: str
    status: str
    message: str


class ProgressResponse(BaseModel):
    session_id: str
    current_topic: str | None = None
    current_day: int = 1

    completed_tasks: int = 0
    unfinished_tasks: int = 0
    total_tasks: int = 0

    quiz_score: float | None = None

    weak_topics: list[str] = Field(default_factory=list)
    medium_topics: list[str] = Field(default_factory=list)
    strong_topics: list[str] = Field(default_factory=list)

    progress_percent: float = 0.0


class TopicPerformance(BaseModel):
    topic: str
    score: float
    status: Literal[
        "weak",
        "medium",
        "strong",
    ]


class QuizPerformance(BaseModel):
    topic: str
    score: float
    total_questions: int
    correct_answers: int = 0


class LearningActivity(BaseModel):
    activity_type: str
    description: str
    timestamp: str


class PerformanceResponse(BaseModel):
    session_id: str

    overall_progress: float = 0.0

    tasks_completed: int = 0
    tasks_total: int = 0
    tasks_skipped: int = 0

    quiz_accuracy: float = 0.0
    quizzes_completed: int = 0

    study_time_minutes: int = 0
    current_streak: int = 0

    topic_performance: list[TopicPerformance] = Field(
        default_factory=list
    )

    quiz_history: list[QuizPerformance] = Field(
        default_factory=list
    )

    strong_topics: list[str] = Field(default_factory=list)
    medium_topics: list[str] = Field(default_factory=list)
    weak_topics: list[str] = Field(default_factory=list)

    recent_activity: list[LearningActivity] = Field(
        default_factory=list
    )


class ReadinessResponse(BaseModel):
    session_id: str

    learning_mode: Literal[
        "general",
        "project",
    ]

    progress_percent: float

    strong_topics: list[str] = Field(default_factory=list)
    medium_topics: list[str] = Field(default_factory=list)
    weak_topics: list[str] = Field(default_factory=list)

    skill_gaps: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)

    report: str | None = None   