from models.schemas import LearningRequest


def validate_learning_request(
    request: LearningRequest,
) -> None:
    if request.learning_mode == "project":
        validate_project_request(request)


def validate_project_request(
    request: LearningRequest,
) -> None:
    if not request.role or not request.role.strip():
        raise ValueError(
            "Role is required for project learning."
        )

    if (
        not request.project_name
        or not request.project_name.strip()
    ):
        raise ValueError(
            "Project name is required for project learning."
        )

    if (
        not request.project_description
        or not request.project_description.strip()
    ):
        raise ValueError(
            "Project description is required for project learning."
        )

    # At least one of: required_skills, required_technologies
    # must be provided (they may be listed in either field).
    has_required = bool(
        getattr(request, "required_skills", [])
        or request.required_technologies
    )

    if not has_required:
        raise ValueError(
            "At least one required skill or technology "
            "is required for project learning."
        )


def validate_task_ids(
    submitted_task_id: str,
    available_task_ids: list[str],
) -> None:
    if submitted_task_id not in available_task_ids:
        raise ValueError(
            "Task does not belong to the current learning session."
        )


def validate_quiz_answers(
    answers: list[str],
    expected_count: int,
) -> None:
    if len(answers) != expected_count:
        raise ValueError(
            f"Expected {expected_count} answers, "
            f"received {len(answers)}."
        )