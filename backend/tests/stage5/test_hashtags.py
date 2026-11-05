from app.services.hashtags import build_hashtags, clean_hashtags, camel_case


def test_camel_case():
    assert camel_case("Campus water bottle") == "campusWaterBottle"
    assert camel_case("---") == ""


def test_hashtag_cleaning_and_deduplication():
    result = clean_hashtags(["Campus bottle", "#campus bottle", "clinically_proven", "#Reusable-Bottle"], 2, 5)
    assert len(result) == len(set(result))
    assert "#clinicallyProven" not in result
    assert all(tag.startswith("#") and " " not in tag for tag in result)


def test_hashtags_respect_range():
    tags = clean_hashtags(["Campus", "Bottle", "Student", "Campus"], 2, 3)
    assert len(tags) <= 3


def test_claim_and_duplicate_tags_are_removed():
    tags = clean_hashtags(["Clinically proven", "Campus Flow", "Campus Flow", "!!!"], 0, 5)
    assert "#clinicallyProven" not in tags
    assert tags.count("#campusFlow") == 1


def test_build_hashtags_includes_campaign_goal():
    tags = build_hashtags("CampusFlow Bottle", "Reusable bottle", "college_students", "Launch awareness", 2, 5)
    assert "#newproduct" in tags
