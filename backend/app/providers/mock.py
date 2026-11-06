from __future__ import annotations

import json
import re
from typing import Any

from app.providers.base import LLMProvider, ProviderResult, ProviderUsage


class MockProvider(LLMProvider):
    """Offline, deterministic provider for demo mode and tests."""

    def generate_json(self, system: str, user: str, schema: dict[str, Any], temperature: float, max_tokens: int) -> ProviderResult:
        title = schema.get("title", "")
        if "Judge" in title or "judge" in user.lower():
            data = {"score": 90, "pass": True, "reasons": ["Mock deterministic judge found no material issue."], "offending_text": []}
        elif title == "Video Output":
            example = json.loads((__import__('pathlib').Path(__file__).resolve().parents[3] / "schemas/examples/video_output.example.json").read_text(encoding="utf-8"))
            data = example
        elif title == "Visual Output":
            example = json.loads((__import__('pathlib').Path(__file__).resolve().parents[3] / "schemas/examples/visual_output.example.json").read_text(encoding="utf-8"))
            data = example
        elif title == "Campaign Brief":
            audience = "college_students"
            data = {"core_message":"CampusFlow keeps practical hydration close throughout the day.","tone":"Friendly, energetic, practical","emotional_hook":"Effortless readiness between classes","key_benefits":["700 ml capacity","leak-resistant lid","easy campus carry"],"audience_profile_reference":audience,"dos_and_donts":{"dos":["Use supplied bottle facts","Keep campus language direct"],"donts":["Invent health results","Use forced slang"]},"prompt_version":"brief_v1"}
        elif title == "Social Output":
            selected = [platform for platform in ("instagram", "linkedin", "x", "facebook", "whatsapp") if platform in user.lower()]
            if "Generate only" in user:
                match = re.search(r"Generate only the '([^']+)'", user)
                selected = [match.group(1)] if match else []
            selected = selected or ["instagram"]
            data = {platform: None for platform in ("instagram", "linkedin", "x", "facebook", "whatsapp")}
            post_types = ["teaser", "feature highlight", "benefit story", "social proof placeholder", "offer or CTA", "user-engagement question", "recap"]
            slots = ["Morning, estimated", "Late morning, estimated", "Lunch, estimated", "Afternoon, estimated", "Late afternoon, estimated", "Evening, estimated", "Morning, estimated"]
            data.update({
                "instagram":{"caption":"CampusFlow carries 700 ml from class to class with a leak-resistant lid.","hashtags":["CampusFlow","ReusableBottle","CampusCarry"],"carousel_slide_ideas":["700 ml capacity","Leak-resistant lid","Campus carry"],"reel_hook":"From class to class, keep water close."},
                "linkedin":{"post":"CampusFlow pairs 700 ml capacity with a leak-resistant lid for practical campus routines.","hashtags":["CampusFlow","ReusableBottle","CampusCarry"]},
                "x":{"post":"CampusFlow: 700 ml capacity and a leak-resistant lid for campus carry.","thread":[]},
                "facebook":{"post":"A water bottle for campus routines: CampusFlow has a 700 ml capacity and leak-resistant lid.","question_or_poll":"What helps your daily campus routine?"},
                "whatsapp":{"message":"CampusFlow: 700 ml capacity and a leak-resistant lid for easy campus carry. See the bottle details."},
                "calendar":[{"day":day,"platform":selected[(day-1)%len(selected)],"post_type":post_types[day-1],"topic":"CampusFlow bottle benefit" if day != 4 else "[Add a real customer review here]","post_reference":f"{selected[(day-1)%len(selected)]}.content","suggested_time_slot":slots[day-1]} for day in range(1,8)],
                "prompt_version":"social_v1"})
            for platform in ("instagram", "linkedin", "x", "facebook", "whatsapp"):
                if platform not in selected:
                    data[platform] = None
            if "calendar" not in user.lower() and "Create a seven" in "":
                pass
        elif title == "Description Output":
            data = {"short":"CampusFlow is a 700 ml reusable bottle with a leak-resistant lid for straightforward campus carry.","medium":"CampusFlow combines a 700 ml capacity with a leak-resistant lid for campus routines. Its practical shape supports easy movement between classes, study sessions, and refills. Choose a bottle designed around simple daily carry and clear product details.","long":"CampusFlow brings practical 700 ml capacity to everyday campus routines. A leak-resistant lid supports straightforward packing between classes, while the reusable design makes refills easy to plan around campus water stations. Carry it through study sessions and the ride home without adding complicated setup to the day. Review the supplied care and material details before use, and wash the bottle according to its instructions.","seo_keywords":["reusable water bottle","campus bottle","700 ml bottle","leak-resistant lid"],"prompt_version":"description_v1"}
        else:
            data = {"headlines":["Campus days, ready to refill","Keep water close between classes","A 700 ml campus companion","Carry less, refill simple","CampusFlow: daily bottle, easy carry"],"taglines":["Ready for every class","Refill and keep moving","Made for the campus day","Carry water with confidence","Simple hydration, anywhere"],"ad_copy_variants":[{"style":"banner","copy":"CampusFlow is a 700 ml reusable bottle with a leak-resistant lid for straightforward daily carry."},{"style":"email","copy":"Between classes and study sessions, CampusFlow keeps water within reach. Review capacity and care details before choosing."},{"style":"search-ad","copy":"Explore a 700 ml reusable bottle with a leak-resistant lid. Check CampusFlow features before choosing."}],"ctas":["See the bottle","Choose CampusFlow","Check features","View details","Get CampusFlow"],"ab_variants":[{"angle":"urgency","id":"A","copy":"Plan today's campus routine with CampusFlow ready for the next refill."},{"angle":"trust","id":"B","copy":"Check the supplied 700 ml capacity and leak-resistant lid details before choosing CampusFlow."},{"angle":"fun","id":"C","copy":"One bottle, class to class. Let CampusFlow keep your routine flowing."}],"prompt_version":"promo_v1"}
        text = json.dumps(data, ensure_ascii=True)
        return ProviderResult(text=text, usage=ProviderUsage(input_tokens=350, output_tokens=max(80, len(text.split())), estimated=True), model="mock-v1")
