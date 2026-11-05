from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

VALID = {
    "product_name": "CampusFlow Bottle",
    "category": "Reusable water bottle",
    "key_features": ["700 ml capacity"],
    "usp": "Easy to carry and refill",
    "brand_name": "CampusFlow",
    "brand_voice": "Friendly and practical",
    "target_audience": "college_students",
    "campaign_goal": "Increase product-page conversions",
    "platforms": ["instagram"],
    "language": "en-US",
}


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_list_personas():
    assert client.get("/personas").status_code == 200
    assert len(client.get("/personas").json()) == 10


def test_get_persona():
    assert client.get("/personas/college_students").status_code == 200


def test_unknown_persona_error():
    response = client.get("/personas/not-real")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "PERSONA_NOT_FOUND"


def test_validate_input():
    assert client.post("/inputs/validate", json=VALID).status_code == 200


def test_validation_error():
    response = client.post("/inputs/validate", json={**VALID, "platforms": ["tiktok"]})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_profile_persona():
    response = client.post("/audiences/profile", json={"persona_id": "college_students"})
    assert response.status_code == 200


def test_profile_custom():
    response = client.post("/audiences/profile", json={"custom_audience": {"age_range": "18-24", "interests": ["value"]}})
    assert response.status_code == 200
