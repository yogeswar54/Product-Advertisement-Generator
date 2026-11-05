import io

from fastapi.testclient import TestClient
from PIL import Image

from app.main import app

client = TestClient(app)
INPUT = {"product_name":"CampusFlow Bottle","category":"Reusable water bottle","key_features":["700 ml capacity","Leak-resistant lid"],"usp":"Easy campus carry","brand_voice":"Friendly and practical","target_audience":"college_students","campaign_goal":"Conversions","platforms":["instagram"],"language":"en-US"}
PROFILE = {"tone":"Friendly and practical","vocabulary_level":"Plain","slang_tolerance":"Low","motivations":["value"],"objections":["price"],"emotional_triggers":["confidence"],"best_platforms":["instagram"],"preferred_content_formats":["short video"],"words_styles_to_avoid":["jargon"]}
BRIEF = {"core_message":"Practical hydration","tone":"Friendly and practical","emotional_hook":"Readiness","key_benefits":["700 ml capacity","Leak-resistant lid","Easy carry"],"audience_profile_reference":"college_students","dos_and_donts":{"dos":["Use facts"],"donts":["Invent claims"]},"prompt_version":"brief_v1"}
REQUEST = {"product_input":INPUT,"audience_profile":PROFILE,"brief":BRIEF}


def test_regenerate_visuals():
    response = client.post("/campaigns/visuals/regenerate", json=REQUEST)
    assert response.status_code == 200


def test_regenerate_one_concept():
    response = client.post("/campaigns/visuals/regenerate?concept=1", json=REQUEST)
    assert response.status_code == 200


def test_generate_mock_asset():
    from app.services.asset_storage import METADATA_PATH
    METADATA_PATH.unlink(missing_ok=True)
    response = client.post("/campaigns/visuals/images", json={"request":REQUEST,"concept_index":0,"format":"square_social_post"})
    assert response.status_code == 200
    assert response.json()["placeholder"] is True


def test_unknown_asset():
    response = client.get("/assets/not-an-asset-id")
    assert response.status_code == 404
