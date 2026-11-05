from app.models.audience import AudienceProfileRequest
from app.models.input import CampaignInput
from app.models.stage4 import CampaignBrief
from app.modules.audience_profiler import profile_audience
from app.modules.video_generator import generate_video_scripts
from app.providers.mock import MockProvider

PERSONAS=["college_students","young_professionals","working_parents","fitness_enthusiasts"]
PRODUCT=CampaignInput(product_name="CampusFlow Bottle",category="Reusable water bottle",key_features=["700 ml capacity","Leak-resistant lid"],usp="Easy campus carry",brand_voice="Friendly and practical",target_audience="college_students",campaign_goal="Conversions",platforms=["instagram"],language="en-US")
BRIEF=CampaignBrief(core_message="Practical hydration",tone="Friendly and practical",emotional_hook="Readiness",key_benefits=["700 ml capacity","Leak-resistant lid","Easy carry"],audience_profile_reference="college_students",dos_and_donts={"dos":["Use facts"],"donts":["Invent claims"]},prompt_version="brief_v1")


def main():
    print("Source: mock provider")
    for persona in PERSONAS:
        audience=profile_audience(AudienceProfileRequest(persona_id=persona))
        video=generate_video_scripts(MockProvider(),PRODUCT.model_copy(update={"target_audience":persona}),audience,BRIEF.model_copy(update={"audience_profile_reference":persona}))
        script=video.scripts_30
        print(persona+": "+script.hook+" | "+script.narration+" | "+script.scenes[0].music_mood)

if __name__ == "__main__":
    main()
