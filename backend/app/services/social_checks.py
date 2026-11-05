import re
from app.models.input import CampaignInput
from app.models.stage4 import Warning
from app.models.stage5 import SocialOutput
from app.services.platform_rules import load_platform_rules

RISKY_CLAIMS = ("clinically proven", "#1 best", "guaranteed results", "cures", "treats")


def run_social_checks(product: CampaignInput, social: SocialOutput, selected_platforms: list[str]) -> list[Warning]:
    rules = load_platform_rules()
    warnings: list[Warning] = []
    texts: list[str] = []
    supplied = re.findall(r"(?<!\w)\d+(?:\.\d+)?(?:%)?(?!\w)", product_facts(product))
    post_map = {"instagram": lambda p: p.caption if p else "", "linkedin": lambda p: p.post if p else "", "x": lambda p: p.post if p else "", "facebook": lambda p: p.post if p else "", "whatsapp": lambda p: p.message if p else ""}
    for platform in selected_platforms:
        post = getattr(social, platform)
        text = post_map[platform](post)
        texts.append(text.lower())
        if len(text) > rules[platform]["max_characters"]:
            warnings.append(Warning(code="SOCIAL_LENGTH_LIMIT", message=f"{platform} content exceeds its configurable {rules[platform]['max_characters']} character limit."))
        for claim in RISKY_CLAIMS:
            if claim in text.lower():
                warnings.append(Warning(code="RISKY_CLAIM_WORD", message=f"{platform} contains the starting risky-claim term '{claim}'."))
        found_numbers = re.findall(r"(?<!\w)\d+(?:\.\d+)?(?:%)?(?!\w)", text)
        if any(number not in supplied for number in found_numbers):
            warnings.append(Warning(code="UNSUPPORTED_NUMBER", message=f"{platform} contains a number not supplied in product input."))
    normalized = [re.sub(r"\\W+", " ", text).strip().lower() for text in texts]
    if len(normalized) != len(set(normalized)):
        warnings.append(Warning(code="DUPLICATE_SOCIAL_COPY", message="Near-duplicate content was detected across selected platforms."))
    if len(social.calendar) != 7:
        warnings.append(Warning(code="CALENDAR_INCOMPLETE", message="The social calendar must contain exactly 7 days."))
    for entry in social.calendar:
        if entry.platform not in selected_platforms:
            warnings.append(Warning(code="CALENDAR_UNSELECTED_PLATFORM", message=f"Calendar contains unselected platform '{entry.platform}'."))
    return warnings


def product_facts(product: CampaignInput) -> str:
    facts = [product.product_name, product.category, product.usp, " ".join(product.key_features)]
    if product.price is not None:
        facts.append(str(product.price))
    return " ".join(facts)
