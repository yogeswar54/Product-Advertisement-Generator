from fastapi.testclient import TestClient
from app.main import app

client=TestClient(app)
INPUT={"product_name":"CampusFlow Bottle","category":"Reusable water bottle","key_features":["700 ml capacity","Leak-resistant lid"],"usp":"Easy campus carry","brand_voice":"Friendly and practical","target_audience":"college_students","campaign_goal":"Conversions","platforms":["instagram"],"language":"en-US"}
PROFILE={"tone":"Friendly","vocabulary_level":"Plain","slang_tolerance":"Low","motivations":["value"],"objections":["price"],"emotional_triggers":["confidence"],"best_platforms":["instagram"],"preferred_content_formats":["short video"],"words_styles_to_avoid":["jargon"]}
BRIEF={"core_message":"Practical hydration","tone":"Friendly","emotional_hook":"Readiness","key_benefits":["700 ml capacity","Leak-resistant lid","Easy carry"],"audience_profile_reference":"college_students","dos_and_donts":{"dos":["Use facts"],"donts":["Invent claims"]},"prompt_version":"brief_v1"}
REQUEST={"product_input":INPUT,"audience_profile":PROFILE,"brief":BRIEF}


def test_regenerate_video():
    assert client.post("/campaigns/video/regenerate",json=REQUEST).status_code == 200


def test_regenerate_duration():
    assert client.post("/campaigns/video/regenerate?duration=30",json=REQUEST).status_code == 200


def test_invalid_duration():
    response=client.post("/campaigns/video/regenerate?duration=20",json=REQUEST)
    assert response.status_code == 422


def test_voiceover():
    response=client.post("/campaigns/video/voiceover",json={"request":REQUEST,"duration":15,"voice":"warm","pace":"normal","language":"en-US"})
    assert response.status_code == 200


def test_assemble_starts_job():
    response = client.post("/campaigns/video/assemble", json={"request":REQUEST,"duration":15})
    assert response.status_code == 200
    assert response.json()["status"] in {"queued", "running"}


def test_unknown_job():
    assert client.get("/jobs/not-a-job").status_code == 404
