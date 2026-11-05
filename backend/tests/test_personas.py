from app.modules.persona_library import get_persona, list_personas

ALLOWED_PLATFORMS = {"instagram", "linkedin", "x", "facebook", "whatsapp"}


def test_exactly_ten_personas_load():
    assert len(list_personas()) == 10


def test_every_persona_valid():
    for persona in list_personas():
        assert persona.id
        assert persona.name
        assert persona.best_platforms
        assert set(persona.best_platforms).issubset(ALLOWED_PLATFORMS)


def test_tech_platform_correction():
    persona = get_persona("tech_enthusiasts")
    assert "youtube-style short video" not in persona.best_platforms
    assert "youtube-style short video" not in persona.preferred_content_formats
    assert "Instagram Reels" in persona.preferred_content_formats


def test_unknown_persona():
    try:
        get_persona("unknown")
    except LookupError:
        return
    raise AssertionError("Unknown persona should fail")
