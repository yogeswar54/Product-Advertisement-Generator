from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
INPUT = {"product_name":"CampusFlow Bottle","category":"Reusable water bottle","key_features":["700 ml capacity","Leak-resistant lid"],"usp":"Easy campus carry","brand_name":"CampusFlow","brand_voice":"Friendly and practical","target_audience":"college_students","campaign_goal":"Conversions","platforms":["instagram","linkedin"],"language":"en-US"}
PROFILE = {"tone":"Friendly and practical","vocabulary_level":"Plain","slang_tolerance":"Low","motivations":["value"],"objections":["price"],"emotional_triggers":["confidence"],"best_platforms":["instagram"],"preferred_content_formats":["short video"],"words_styles_to_avoid":["jargon"]}
BRIEF = {"core_message":"Practical campus hydration","tone":"Friendly and practical","emotional_hook":"Readiness","key_benefits":["700 ml capacity","Leak-resistant lid","Easy carry"],"audience_profile_reference":"college_students","dos_and_donts":{"dos":["Use facts"],"donts":["Invent claims"]},"prompt_version":"brief_v1"}
REQUEST = {"product_input":INPUT,"audience_profile":PROFILE,"brief":BRIEF}


def test_social_regenerate():
    response = client.post("/campaigns/social/regenerate", json=REQUEST)
    assert response.status_code == 200


def test_social_single_platform_regenerate():
    response = client.post("/campaigns/social/regenerate?platform=instagram", json=REQUEST)
    assert response.status_code == 200
    assert response.json()["platform"] == "instagram"


def test_invalid_platform():
    response = client.post("/campaigns/social/regenerate?platform=tiktok", json=REQUEST)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_calendar_regenerate():
    response = client.post("/campaigns/social/calendar/regenerate", json=REQUEST)
    assert response.status_code == 200
    assert len(response.json()["calendar"]) == 7
