from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

INPUT = {"product_name":"CampusFlow Bottle","category":"Reusable water bottle","key_features":["700 ml capacity","Leak-resistant lid"],"usp":"Easy campus carry","brand_name":"CampusFlow","brand_voice":"Friendly and practical","target_audience":"college_students","campaign_goal":"Conversions","platforms":["instagram"],"language":"en-US"}
PROFILE = {"tone":"Friendly, energetic, practical","vocabulary_level":"Conversational, plain","slang_tolerance":"Light","motivations":["value"],"objections":["price"],"emotional_triggers":["belonging"],"best_platforms":["instagram"],"preferred_content_formats":["short video"],"words_styles_to_avoid":["corporate jargon"]}
BRIEF = {"core_message":"CampusFlow keeps practical hydration close.","tone":"Friendly and practical","emotional_hook":"Ready throughout the day","key_benefits":["700 ml capacity","Leak-resistant lid","Easy campus carry"],"audience_profile_reference":"college_students","dos_and_donts":{"dos":["Use product facts"],"donts":["Invent claims"]},"prompt_version":"brief_v1"}


def test_create_brief():
    response = client.post("/campaigns/brief", json={"product_input":INPUT,"audience_profile":PROFILE})
    assert response.status_code == 200
    assert response.json()["prompt_version"] == "brief_v1"


def test_edit_brief():
    response = client.put("/campaigns/brief", json={"product_input":INPUT,"audience_profile":PROFILE,"brief":BRIEF})
    assert response.status_code == 200
    assert response.json()["core_message"] == BRIEF["core_message"]


def test_generate():
    response = client.post("/campaigns/generate", json={"product_input":INPUT,"audience_profile":PROFILE,"brief":BRIEF})
    assert response.status_code == 200
    assert response.json()["modules"]["description"]["status"] == "success"
    assert response.json()["modules"]["promo"]["status"] == "success"


def test_regenerate_description():
    response = client.post("/campaigns/description/regenerate", json={"product_input":INPUT,"audience_profile":PROFILE,"brief":BRIEF})
    assert response.status_code == 200
    assert response.json()["section"] == "description"


def test_regenerate_promo():
    response = client.post("/campaigns/promo/regenerate", json={"product_input":INPUT,"audience_profile":PROFILE,"brief":BRIEF})
    assert response.status_code == 200
    assert response.json()["section"] == "promo"


def test_invalid_section():
    response = client.post("/campaigns/archive/regenerate", json={"product_input":INPUT,"audience_profile":PROFILE,"brief":BRIEF})
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "SECTION_NOT_FOUND"
