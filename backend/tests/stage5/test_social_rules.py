from app.services.platform_rules import ALLOWED_PLATFORMS, load_platform_rules
from app.services.calendar_generator import validate_calendar
from app.models.stage5 import CalendarEntry


def test_all_platform_rules_load():
    rules = load_platform_rules()
    assert set(rules) == ALLOWED_PLATFORMS


def test_platform_limits_are_positive():
    for platform, rules in load_platform_rules().items():
        assert rules["max_characters"] > 0
        assert 0 <= rules["hashtag_count"]["min"] <= rules["hashtag_count"]["max"]


def test_valid_calendar_passes():
    entries = [CalendarEntry(day=day, platform="instagram", post_type=["teaser", "feature highlight", "benefit story", "social proof placeholder", "offer or CTA", "user-engagement question", "recap"][day-1], topic="CampusFlow", post_reference="instagram.caption", suggested_time_slot="Morning, estimated") for day in range(1, 8)]
    validate_calendar(entries, ["instagram"])


def test_calendar_rejects_unselected_platform():
    entries = [CalendarEntry(day=day, platform="linkedin" if day == 1 else "instagram", post_type=["teaser", "feature highlight", "benefit story", "social proof placeholder", "offer or CTA", "user-engagement question", "recap"][day-1], topic="CampusFlow", post_reference="instagram.caption", suggested_time_slot="Morning, estimated") for day in range(1, 8)]
    try:
        validate_calendar(entries, ["instagram"])
    except ValueError:
        return
    raise AssertionError("Unselected calendar platform should fail")
