from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_vague_query_clarifies_without_recommendations():
    response = client.post(
        "/chat",
        json={
            "messages": [
                {
                    "role": "user",
                    "content": "I need an assessment.",
                }
            ]
        },
    )

    data = response.json()

    assert response.status_code == 200
    assert "reply" in data
    assert data["recommendations"] == []
    assert data["end_of_conversation"] is False


def test_legal_question_is_refused():
    response = client.post(
        "/chat",
        json={
            "messages": [
                {
                    "role": "user",
                    "content": "Are we legally required under HIPAA to test all staff who touch patient records?",
                }
            ]
        },
    )

    data = response.json()

    assert response.status_code == 200
    assert data["recommendations"] == []
    assert data["end_of_conversation"] is False
    assert "legal" in data["reply"].lower()


def test_finance_graduate_recommendations():
    response = client.post(
        "/chat",
        json={
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "We're hiring graduate financial analysts — final-year students, "
                        "no work experience. We need numerical reasoning and a finance knowledge test."
                    ),
                }
            ]
        },
    )

    data = response.json()
    names = [item["name"] for item in data["recommendations"]]

    assert response.status_code == 200
    assert "SHL Verify Interactive – Numerical Reasoning" in names
    assert "Financial Accounting (New)" in names
    assert "Basic Statistics (New)" in names
    assert "Graduate Scenarios" in names


def test_java_backend_cloud_recommendations():
    response = client.post(
        "/chat",
        json={
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "Senior Full-Stack Engineer with Core Java, Spring, SQL, "
                        "AWS and Docker. Backend-leaning senior IC."
                    ),
                }
            ]
        },
    )

    data = response.json()
    names = [item["name"] for item in data["recommendations"]]

    assert response.status_code == 200
    assert "Core Java (Advanced Level) (New)" in names
    assert "Spring (New)" in names
    assert "SQL (New)" in names
    assert "Amazon Web Services (AWS) Development (New)" in names
    assert "Docker (New)" in names


def test_recommendation_schema_is_strict():
    response = client.post(
        "/chat",
        json={
            "messages": [
                {
                    "role": "user",
                    "content": "I need to quickly screen admin assistants for Excel and Word daily.",
                }
            ]
        },
    )

    data = response.json()

    assert response.status_code == 200

    for item in data["recommendations"]:
        assert set(item.keys()) == {"name", "url", "test_type"}
        assert item["name"]
        assert item["url"].startswith("https://www.shl.com/")
        assert item["test_type"]

def test_comparison_request_returns_grounded_catalog_answer():
    response = client.post(
        "/chat",
        json={
            "messages": [
                {
                    "role": "user",
                    "content": "What is the difference between OPQ and GSA?",
                }
            ]
        },
    )

    data = response.json()

    assert response.status_code == 200
    assert data["recommendations"] == []
    assert data["end_of_conversation"] is False
    assert "Occupational Personality Questionnaire OPQ32r" in data["reply"]
    assert "Global Skills Assessment" in data["reply"]