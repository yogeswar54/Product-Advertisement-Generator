from app.models.audience import AudienceProfileRequest, CustomAudience
from app.modules.audience_profiler import bias_matches, custom_profile, normalize_tone_preference, profile_audience


def test_all_personas_profile():
    for persona_id in [
        "college_students", "young_professionals", "working_parents", "fitness_enthusiasts",
        "senior_citizens", "small_business_owners", "tech_enthusiasts", "luxury_shoppers",
        "budget_conscious_shoppers", "rural_first_time_online_buyers",
    ]:
        profile = profile_audience(AudienceProfileRequest(persona_id=persona_id))
        assert profile.tone
        assert profile.best_platforms


def test_custom_audience():
    profile = profile_audience(AudienceProfileRequest(custom_audience=CustomAudience(age_range="18-24", interests=["value"], pain_points=["limited time"])))
    assert profile.vocabulary_level == "Conversational, plain"


def test_persona_override():
    profile = profile_audience(AudienceProfileRequest(persona_id="college_students", overrides={"tone": "Warm and direct"}))
    assert profile.tone == "Warm and direct"


def test_bias_guard():
    try:
        profile_audience(AudienceProfileRequest(custom_audience=CustomAudience(interests=["all women are careless shoppers"])))
    except ValueError as exc:
        assert "stereotype" in str(exc)
    else:
        raise AssertionError("Stereotyped custom audience should fail")


def test_bias_pattern_detector():
    assert bias_matches("All young people are lazy customers") is True


def test_senior_custom_audience_defaults():
    profile = custom_profile(CustomAudience(age_range="65-70", interests=["community"], pain_points=["small text"]))
    assert profile.vocabulary_level == "Plain and accessible"
    assert profile.best_platforms == ["facebook", "whatsapp"]


def test_default_custom_audience_profile():
    profile = custom_profile(CustomAudience())
    assert profile.tone == "Clear, practical, and trustworthy"
    assert profile.motivations == ["practical value", "ease of use"]


def test_tone_preference_sanitization():
    assert normalize_tone_preference(" Warm! and direct", "Default") == "Warm and direct"
    assert normalize_tone_preference("!!!", "Default") == "Default"


def test_unknown_profile_override_is_rejected():
    try:
        profile_audience(AudienceProfileRequest(persona_id="college_students", overrides={"unknown_field": "value"}))
    except ValueError as exc:
        assert "Unsupported audience profile overrides" in str(exc)
    else:
        raise AssertionError("Unknown profile override should fail")
