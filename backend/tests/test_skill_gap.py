from agents.skill_gap import analyze_skill_gaps


def test_general_mode_has_no_skill_gaps():
    state = {
        "learning_mode": "general",
        "current_skills": ["Python"],
        "required_technologies": ["PyTorch"],
    }

    result = analyze_skill_gaps(state)

    assert result["skill_gaps"] == []


def test_project_mode_finds_missing_skills():
    state = {
        "learning_mode": "project",
        "current_skills": [
            "Java",
            "SQL",
            "Git",
        ],
        "required_technologies": [
            "Spring Boot",
            "PostgreSQL",
            "REST APIs",
            "Database Design",
            "Redis",
        ],
    }

    result = analyze_skill_gaps(state)
    gaps = result["skill_gaps"]

    assert len(gaps) == 5

    skills = [gap["skill"] for gap in gaps]

    assert skills == [
        "Spring Boot",
        "PostgreSQL",
        "REST APIs",
        "Database Design",
        "Redis",
    ]


def test_existing_skills_are_not_reported_as_gaps():
    state = {
        "learning_mode": "project",
        "current_skills": [
            "Java",
            "SQL",
            "Spring Boot",
        ],
        "required_technologies": [
            "Java",
            "REST APIs",
            "Spring Boot",
            "PostgreSQL",
        ],
    }

    result = analyze_skill_gaps(state)
    skills = [gap["skill"] for gap in result["skill_gaps"]]

    assert "Java" not in skills
    assert "Spring Boot" not in skills
    assert "REST APIs" in skills
    assert "PostgreSQL" in skills


def test_skill_matching_ignores_case_and_extra_spaces():
    state = {
        "learning_mode": "project",
        "current_skills": [
            "  Spring Boot  ",
            "POSTGRESQL",
        ],
        "required_technologies": [
            "spring boot",
            "PostgreSQL",
            "Redis",
        ],
    }

    result = analyze_skill_gaps(state)
    skills = [gap["skill"] for gap in result["skill_gaps"]]

    assert skills == ["Redis"]


def test_duplicate_required_technologies_are_removed():
    state = {
        "learning_mode": "project",
        "current_skills": [],
        "required_technologies": [
            "REST APIs",
            "rest apis",
            " REST APIs ",
            "Spring Boot",
            "spring boot",
        ],
    }

    result = analyze_skill_gaps(state)
    skills = [gap["skill"] for gap in result["skill_gaps"]]

    assert skills.count("REST APIs") == 1
    assert skills.count("Spring Boot") == 1


def test_high_priority_foundational_skills():
    state = {
        "learning_mode": "project",
        "current_skills": [],
        "required_technologies": [
            "Python",
            "Java",
            "SQL",
            "PostgreSQL",
        ],
    }

    result = analyze_skill_gaps(state)

    for gap in result["skill_gaps"]:
        assert gap["priority"] == "high"


def test_unknown_skills_get_medium_priority():
    state = {
        "learning_mode": "project",
        "current_skills": [],
        "required_technologies": [
            "System Design",
            "Redis",
        ],
    }

    result = analyze_skill_gaps(state)

    assert len(result["skill_gaps"]) == 2

    for gap in result["skill_gaps"]:
        assert gap["priority"] == "medium"


def test_all_skill_gaps_are_marked_missing():
    state = {
        "learning_mode": "project",
        "current_skills": ["Java"],
        "required_technologies": [
            "Spring Boot",
            "REST APIs",
            "PostgreSQL",
        ],
    }

    result = analyze_skill_gaps(state)

    for gap in result["skill_gaps"]:
        assert gap["status"] == "missing"


def test_empty_project_skills_returns_no_gaps():
    state = {
        "learning_mode": "project",
        "current_skills": [],
        "required_technologies": [],
    }

    result = analyze_skill_gaps(state)

    assert result["skill_gaps"] == []