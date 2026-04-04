import pytest
from src.analyzer import analyze_project


def _minimal_context(**kwargs) -> dict:
    base = {
        "business_background": "",
        "team_client_requirements": "",
        "pm_decisions": "",
        "t1_responsibilities": "",
        "t2_responsibilities": "",
        "architecture_details": "",
        "coordination": "",
        "challenges": "",
        "outcomes": "",
    }
    base.update(kwargs)
    return base


def test_returns_required_fields():
    result = analyze_project("Built a Vue 3 dashboard with Pinia state management.", _minimal_context())
    required = [
        "title", "category", "tags", "ownership_classification",
        "summary", "ownership_description", "technical_highlights",
        "resume_bullets", "interview_answer", "self_intro", "talking_points",
    ]
    for field in required:
        assert field in result, f"Missing field: {field}"


def test_vue_keywords_produce_correct_tags():
    result = analyze_project(
        "Developed a Vue 3 application using Pinia for state management.",
        _minimal_context(),
    )
    assert "vue_web" in result["tags"]
    assert "state_store_design" in result["tags"]


def test_category_web_app_detected():
    result = analyze_project(
        "Built a React frontend with a REST API integration.",
        _minimal_context(),
    )
    assert result["category"] == "web_app"


def test_category_backend_detected():
    result = analyze_project(
        "Implemented a FastAPI server with PostgreSQL and SQL migrations.",
        _minimal_context(),
    )
    assert result["category"] == "backend"


def test_context_fields_appear_in_ownership():
    context = _minimal_context(
        t1_responsibilities="Designed the API interface",
        t2_responsibilities="Implemented the frontend components",
        business_background="Internal tooling platform for ops team",
    )
    result = analyze_project("Project context", context)
    desc = result["ownership_description"]
    assert "API interface" in desc
    assert "frontend components" in desc
    assert "Internal tooling" in desc


def test_bullets_generated_from_contributions():
    context = _minimal_context(
        t1_responsibilities="Scoped the migration plan across three platforms",
        t2_responsibilities="Implemented the Vue component library",
    )
    result = analyze_project("Project", context)
    bullets = result["resume_bullets"]
    assert len(bullets) >= 1
    assert any("component library" in b.lower() or "migration" in b.lower() for b in bullets)


def test_star_contains_all_sections():
    context = _minimal_context(
        business_background="Company needed a new workflow tool",
        t1_responsibilities="Analyzed requirements",
        t2_responsibilities="Built the workflow engine",
        outcomes="Reduced manual steps by 40%",
    )
    result = analyze_project("Project text", context)
    star = result["interview_answer"]
    assert "Situation:" in star
    assert "Task:" in star
    assert "Action:" in star
    assert "Result:" in star


def test_tags_only_valid_values():
    result = analyze_project("Some random text about coordination and mobile platforms", _minimal_context())
    valid = {
        "frontend_architecture", "vue_web", "state_store_design",
        "api_interface_definition", "platform_coordination",
        "workflow_complexity", "middle_office", "cross_functional",
    }
    assert all(t in valid for t in result["tags"])


def test_category_always_valid():
    valid = {"web_app", "mobile", "backend", "data", "devops", "platform", "other"}
    result = analyze_project("completely unrelated text with no tech keywords", _minimal_context())
    assert result["category"] in valid


def test_context_stored_in_result():
    context = _minimal_context(t1_responsibilities="Defined the data model")
    result = analyze_project("text", context)
    assert result["context"] == context


def test_minimal_input_does_not_raise():
    result = analyze_project("A software project.", _minimal_context())
    assert result["title"] != ""
    assert isinstance(result["tags"], list)


def test_title_extracted_from_first_line():
    result = analyze_project("My Internal Dashboard\nMore details below.", _minimal_context())
    assert result["title"] == "My Internal Dashboard"
