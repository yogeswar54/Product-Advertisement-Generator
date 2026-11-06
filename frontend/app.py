from __future__ import annotations

import html
from io import BytesIO
import json
import os

import requests
import streamlit as st
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

API_BASE = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
PLATFORM_OPTIONS = ["instagram", "linkedin", "x", "facebook", "whatsapp"]
PLATFORM_RULES = json.loads((Path(__file__).resolve().parents[1] / "config/platform_rules.json").read_text(encoding="utf-8"))
VISUAL_FORMATS = json.loads((Path(__file__).resolve().parents[1] / "config/visual_formats.json").read_text(encoding="utf-8"))
VOICE_OPTIONS = json.loads((Path(__file__).resolve().parents[1] / "config/voice_options.json").read_text(encoding="utf-8"))


def feature_enabled(name: str) -> bool:
    value = os.getenv(name, "off").strip().lower()
    if value not in {"off", "on"}:
        raise ValueError(f"{name} must be off or on")
    return value == "on"


ENHANCE_HINDI = feature_enabled("ENHANCE_HINDI")
ENHANCE_BRAND_KIT = feature_enabled("ENHANCE_BRAND_KIT")

st.set_page_config(page_title="Product Advertisement Generator", page_icon="P", layout="wide")
st.title("AI-Based Product Advertisement Generator")
st.caption("Stage 3: product setup and audience selection")


def copy_button(label: str, text: str, key: str) -> None:
    safe_text = json.dumps(text, ensure_ascii=True)
    st.markdown(
        f'<button type="button" id="copy-{key}" onclick="navigator.clipboard.writeText({safe_text})">{html.escape(label)}</button>',
        unsafe_allow_html=True,
    )


def api_get(path: str) -> tuple[bool, object]:
    try:
        response = requests.get(API_BASE + path, timeout=10)
        response.raise_for_status()
        return True, response.json()
    except requests.RequestException as exc:
        return False, str(exc)


def render_brand_overlay(brand_kit: dict[str, object], logo_bytes: bytes | None) -> Image.Image:
    preview = Image.new("RGBA", (960, 360), str(brand_kit["primary_color"]))
    draw = ImageDraw.Draw(preview)
    if logo_bytes:
        with Image.open(BytesIO(logo_bytes)) as logo_file:
            logo = logo_file.convert("RGBA")
            logo.thumbnail((260, 210), Image.Resampling.LANCZOS)
            preview.alpha_composite(logo, (660, 45))
    draw.text((40, 260), "Aa", fill=str(brand_kit["secondary_color"]), font=ImageFont.load_default(size=48))
    return preview.convert("RGB")


if "validated_input" not in st.session_state:
    st.session_state.validated_input = None
if "audience_profile" not in st.session_state:
    st.session_state.audience_profile = None

steps = st.tabs(["1. Product", "2. Audience", "3. Campaign settings", "4. Review"])

with steps[0]:
    st.subheader("Product details")
    product_name = st.text_input("Product name *", placeholder="CampusFlow Reusable Bottle", key="product_name")
    category = st.text_input("Category *", placeholder="Reusable water bottle", key="category")
    usp = st.text_area("Unique selling point *", placeholder="Keeps water cold and is easy to carry", max_chars=300, key="usp")
    key_features_text = st.text_area("Key features *", placeholder="700 ml capacity\nLeak-resistant lid\nBPA-free materials", help="Enter one feature per line. Maximum 12.", key="key_features")
    brand_name = st.text_input("Brand name", placeholder="CampusFlow", key="brand_name")
    brand_voice = st.text_input("Brand voice *", placeholder="Friendly, practical, and energetic", key="brand_voice")
    price = st.number_input("Price", min_value=0.0, step=0.01, value=None, key="price")
    competitor_info = st.text_area("Competitor information (optional)", max_chars=1500, key="competitor_info")

with steps[1]:
    st.subheader("Audience selection")
    ok, personas = api_get("/personas")
    if not ok:
        st.error("Could not load personas. Confirm the backend is running on " + API_BASE)
        personas = []
    persona_names = {persona["name"]: persona["id"] for persona in personas}
    persona_names["Custom audience"] = "__custom__"
    selected_name = st.selectbox("Choose an audience *", list(persona_names), key="audience_name")
    custom = None
    if persona_names[selected_name] == "__custom__":
        age_range = st.text_input("Age range", placeholder="18-24")
        interests = st.text_input("Interests", placeholder="campus life, value, convenience")
        income_level = st.text_input("Income level", placeholder="Student budget")
        location = st.text_input("Location", placeholder="Urban campus")
        pain_points = st.text_input("Pain points", placeholder="limited budget, busy schedule")
        tone_preference = st.text_input("Tone preference", placeholder="Friendly and practical")
        custom = {
            "age_range": age_range or None,
            "interests": [item.strip() for item in interests.split(",") if item.strip()],
            "income_level": income_level or None,
            "location": location or None,
            "pain_points": [item.strip() for item in pain_points.split(",") if item.strip()],
            "tone_preference": tone_preference or None,
        }
    else:
        base_id = persona_names[selected_name]
        st.info(persona_names[selected_name] + " selected")
        override_mode = st.checkbox("Override selected persona fields")
        overrides = {}
        if override_mode:
            override_tone = st.text_input("Override tone")
            override_vocab = st.text_input("Override vocabulary level")
            if override_tone:
                overrides["tone"] = override_tone
            if override_vocab:
                overrides["vocabulary_level"] = override_vocab

with steps[2]:
    st.subheader("Campaign settings")
    campaign_goal = st.text_input("Campaign goal *", placeholder="Increase product-page conversions", key="campaign_goal")
    platforms = st.multiselect("Platforms *", PLATFORM_OPTIONS, key="platforms")
    if ENHANCE_HINDI:
        language_choice = st.selectbox("Language *", ["English (en-US)", "Hindi (hi)", "Other"], key="language_choice")
        if language_choice == "Hindi (hi)":
            language = "hi"
        elif language_choice == "English (en-US)":
            language = "en-US"
        else:
            language = st.text_input("Language tag *", value="en-US", key="language_custom")
    else:
        language = st.text_input("Language *", value="en-US", key="language")
    brand_kit = None
    brand_logo_upload = None
    if ENHANCE_BRAND_KIT:
        st.subheader("Optional campaign brand kit")
        if st.checkbox("Use a campaign brand kit", key="enable_brand_kit"):
            brand_kit = {
                "name": st.text_input("Brand kit name", max_chars=100, key="brand-kit-name"),
                "primary_color": st.text_input("Primary color (hex)", value="#17324D", key="brand-kit-primary"),
                "secondary_color": st.text_input("Secondary color (hex)", value="#FFFFFF", key="brand-kit-secondary"),
                "font": st.text_input("Font category or name", max_chars=100, key="brand-kit-font"),
                "font_licensing_note": st.text_input("Font licensing note", max_chars=300, key="brand-kit-font-license"),
                "rights_confirmed": st.checkbox("I have the rights to use this logo and font.", key="brand-kit-rights"),
            }
            brand_logo_upload = st.file_uploader(
                "Optional logo (PNG, JPEG, or WebP; SVG is not accepted)",
                type=["png", "jpg", "jpeg", "webp"],
                key="brand-kit-logo",
            )
            st.caption("Rights confirmation is user-provided; the application does not verify logo or font rights.")

with steps[3]:
    st.subheader("Review")
    if st.button("Validate and profile", type="primary"):
        payload = {
            "product_name": st.session_state.product_name,
            "category": st.session_state.category,
            "key_features": [item.strip() for item in st.session_state.key_features.splitlines() if item.strip()],
            "price": None if st.session_state.price == 0 else st.session_state.price,
            "usp": st.session_state.usp,
            "brand_name": st.session_state.brand_name,
            "brand_voice": st.session_state.brand_voice,
            "target_audience": persona_names[selected_name] if persona_names[selected_name] != "__custom__" else "custom",
            "campaign_goal": st.session_state.campaign_goal,
            "platforms": st.session_state.platforms,
            "language": language,
            "product_image": None,
            "competitor_info": st.session_state.competitor_info,
        }
        if brand_kit is not None:
            payload["brand_kit"] = brand_kit
        try:
            validation = requests.post(API_BASE + "/inputs/validate", json=payload, timeout=10)
            validation.raise_for_status()
            st.session_state.validated_input = validation.json()
            audience_request = {"persona_id": persona_names[selected_name]} if persona_names[selected_name] != "__custom__" else {"custom_audience": custom}
            audience_request["language"] = language
            audience_request["overrides"] = overrides if "overrides" in locals() else {}
            profiling = requests.post(API_BASE + "/audiences/profile", json=audience_request, timeout=10)
            profiling.raise_for_status()
            st.session_state.audience_profile = profiling.json()
            st.success("Input and audience profile validated.")
        except requests.HTTPError as exc:
            try:
                detail = exc.response.json()["error"]
                st.error(detail["message"])
                if detail.get("field"):
                    st.caption("Field: " + detail["field"])
            except (KeyError, ValueError, AttributeError):
                st.error("Validation failed. Check the required fields.")
        except requests.RequestException as exc:
            st.error("Could not reach the backend: " + str(exc))

    if st.session_state.validated_input:
        st.json(st.session_state.validated_input)
    if st.session_state.audience_profile:
        st.subheader("Audience profile")
        st.json(st.session_state.audience_profile)
        if st.session_state.validated_input.get("warnings"):
            st.warning("Prompt-injection warning detected. Review the generated text carefully.")
        flags = st.session_state.validated_input.get("flags", {})
        if flags.get("restricted_category"):
            st.warning(flags["restricted_category_note"])

    st.divider()
    st.subheader("Campaign Brief")
    provider_mode = os.getenv("LLM_PROVIDER", "mock")
    if provider_mode == "mock":
        st.info("Demo mode (mock provider): no API key or internet required.")
    else:
        st.info("Hosted LLM provider mode. Live usage may incur provider charges; check current pricing.")

    if st.session_state.validated_input and st.session_state.audience_profile:
        if st.button("Create Campaign Brief"):
            try:
                response = requests.post(API_BASE + "/campaigns/brief", json={
                    "product_input": st.session_state.validated_input["validated"],
                    "audience_profile": st.session_state.audience_profile,
                }, timeout=30)
                response.raise_for_status()
                st.session_state.campaign_brief = response.json()
            except requests.RequestException as exc:
                st.error("Could not create the campaign brief: " + str(exc))
        if "campaign_brief" not in st.session_state:
            st.session_state.campaign_brief = None
        if st.session_state.campaign_brief:
            brief = st.session_state.campaign_brief
            edited_core = st.text_area("Core message", value=brief["core_message"])
            edited_tone = st.text_input("Tone", value=brief["tone"])
            edited_hook = st.text_area("Emotional hook", value=brief["emotional_hook"])
            if st.button("Save brief edits"):
                brief["core_message"] = edited_core
                brief["tone"] = edited_tone
                brief["emotional_hook"] = edited_hook
                st.session_state.campaign_brief = brief
                st.success("Campaign brief saved for generation.")
            if st.button("Generate text package", type="primary"):
                with st.spinner("Generating descriptions and promotional copy..."):
                    try:
                        response = requests.post(API_BASE + "/campaigns/generate", json={
                            "product_input": st.session_state.validated_input["validated"],
                            "audience_profile": st.session_state.audience_profile,
                            "brief": st.session_state.campaign_brief,
                        }, timeout=60)
                        response.raise_for_status()
                        st.session_state.generation = response.json()
                        st.session_state.saved_campaign_id = None
                    except requests.RequestException as exc:
                        st.error("Generation failed: " + str(exc))
            if st.session_state.get("generation"):
                generation = st.session_state.generation
                if not st.session_state.get("saved_campaign_id"):
                    section_names = {
                        "description": "descriptions",
                        "promo": "promo",
                        "social": "social",
                        "visual": "visuals",
                        "video": "video",
                    }
                    saved_outputs = {}
                    for module_name, section_name in section_names.items():
                        module = generation.get("modules", {}).get(module_name, {})
                        saved_outputs[section_name] = {
                            "status": "ready" if module.get("status") == "success" else module.get("status", "missing"),
                            "content": module.get("output", {}),
                        }
                    try:
                        saved = requests.post(API_BASE + "/campaigns", json={
                            "name": st.session_state.validated_input["validated"]["product_name"],
                            "inputs": {
                                **st.session_state.validated_input["validated"],
                                "audience": st.session_state.audience_profile,
                            },
                            "brief": st.session_state.campaign_brief,
                            "outputs": saved_outputs,
                            "quality": generation.get("quality"),
                        }, timeout=20)
                        saved.raise_for_status()
                        st.session_state.saved_campaign_id = saved.json()["id"]
                    except requests.RequestException as exc:
                        st.error("Generated content is available, but campaign history could not be saved: " + str(exc))
                campaign_id = st.session_state.get("saved_campaign_id")
                if campaign_id and brand_logo_upload is not None and st.session_state.get("brand_kit_logo_campaign_id") != campaign_id:
                    try:
                        uploaded = requests.put(
                            API_BASE + f"/campaigns/{campaign_id}/brand-kit/logo",
                            data=brand_logo_upload.getvalue(),
                            headers={"Content-Type": brand_logo_upload.type or "application/octet-stream"},
                            timeout=30,
                        )
                        uploaded.raise_for_status()
                        st.session_state.brand_kit_logo_asset_id = uploaded.json()["id"]
                        st.session_state.brand_kit_logo_campaign_id = campaign_id
                        st.success("Brand logo validated and stored with this campaign.")
                    except requests.RequestException as exc:
                        st.error("Campaign was saved, but the brand logo could not be attached: " + str(exc))
                result_tabs = st.tabs(["Descriptions", "Promo", "Social", "Visuals", "Video", "Quality"])
                with result_tabs[0]:
                    description = generation["modules"]["description"]
                    if description["status"] == "success":
                        output = description["output"]
                        for label in ["short", "medium", "long"]:
                            st.text_area(label.title(), value=output[label])
                            copy_button("Copy " + label, output[label], "description-" + label)
                        st.write("SEO keywords: " + ", ".join(output["seo_keywords"]))
                        if st.button("Regenerate description"):
                            response = requests.post(API_BASE + "/campaigns/description/regenerate", json={
                                "product_input": st.session_state.validated_input["validated"],
                                "audience_profile": st.session_state.audience_profile,
                                "brief": st.session_state.campaign_brief,
                            }, timeout=60)
                            response.raise_for_status()
                            st.session_state.generation["modules"]["description"] = {"status":"success", "output":response.json()["output"]}
                            st.success("Description regenerated.")
                            st.rerun()
                    else:
                        st.error(description.get("error", "Description generation failed."))
                with result_tabs[1]:
                    promo = generation["modules"]["promo"]
                    if promo["status"] == "success":
                        output = promo["output"]
                        for key in ["headlines", "taglines", "ctas"]:
                            st.write(key.title())
                            for item in output[key]:
                                st.code(item)
                                copy_button("Copy", item, "promo-" + key + str(len(item)))
                        st.write("Ad copy variants")
                        for item in output["ad_copy_variants"]:
                            st.markdown("**" + item["style"] + "**")
                            st.code(item["copy"])
                        st.write("A/B variants")
                        for item in output["ab_variants"]:
                            st.markdown("**" + item["angle"] + "**")
                            st.code(item["copy"])
                        if st.button("Regenerate promo"):
                            response = requests.post(API_BASE + "/campaigns/promo/regenerate", json={
                                "product_input": st.session_state.validated_input["validated"],
                                "audience_profile": st.session_state.audience_profile,
                                "brief": st.session_state.campaign_brief,
                            }, timeout=60)
                            response.raise_for_status()
                            st.session_state.generation["modules"]["promo"] = {"status":"success", "output":response.json()["output"]}
                            st.success("Promo regenerated.")
                            st.rerun()
                    else:
                        st.error(promo.get("error", "Promo generation failed."))
                with result_tabs[2]:
                    social = generation["modules"].get("social", {})
                    if social.get("status") == "success":
                        output = social["output"]
                        for platform in st.session_state.platforms:
                            post = output.get(platform)
                            if not post:
                                continue
                            text = post.get("caption") or post.get("post") or post.get("message") or ""
                            limit = PLATFORM_RULES[platform]["max_characters"]
                            color = "green" if len(text) <= limit else "red"
                            with st.container(border=True):
                                st.subheader(platform.title())
                                st.text_area("Post", value=text, key="social-" + platform, disabled=True)
                                st.markdown(f"Characters: :{color}[{len(text)} / {limit}]")
                                copy_button("Copy post", text, "social-" + platform)
                                hashtags = post.get("hashtags", [])
                                if hashtags:
                                    hashtag_text = " ".join(hashtags)
                                    st.write(hashtag_text)
                                    copy_button("Copy hashtags", hashtag_text, "hashtags-" + platform)
                                if st.button("Regenerate " + platform, key="regen-social-" + platform):
                                    response = requests.post(API_BASE + "/campaigns/social/regenerate", params={"platform": platform}, json={
                                        "product_input": st.session_state.validated_input["validated"], "audience_profile": st.session_state.audience_profile, "brief": st.session_state.campaign_brief,
                                    }, timeout=60)
                                    response.raise_for_status()
                                    st.success(platform.title() + " regenerated.")
                        st.subheader("7-day content calendar")
                        st.caption("Posting time slots are estimated suggestions to be tested.")
                        st.dataframe([{
                            "Day": entry["day"], "Platform": entry["platform"], "Post type": entry["post_type"], "Topic": entry["topic"], "Estimated time": entry["suggested_time_slot"]
                        } for entry in output["calendar"]], use_container_width=True, hide_index=True)
                        if st.button("Regenerate calendar"):
                            response = requests.post(API_BASE + "/campaigns/social/calendar/regenerate", json={
                                "product_input": st.session_state.validated_input["validated"], "audience_profile": st.session_state.audience_profile, "brief": st.session_state.campaign_brief,
                            }, timeout=60)
                            response.raise_for_status()
                            output["calendar"] = response.json()["calendar"]
                            st.success("Calendar regenerated.")
                            st.rerun()
                    else:
                        st.error(social.get("error", "Social generation failed. Retry an individual platform."))
                with result_tabs[3]:
                    visual = generation["modules"].get("visual", {})
                    if visual.get("status") == "success":
                        saved_brand_kit = st.session_state.validated_input["validated"].get("brand_kit")
                        if saved_brand_kit:
                            logo_bytes = None
                            logo_asset_id = st.session_state.get("brand_kit_logo_asset_id")
                            if logo_asset_id:
                                logo_response = requests.get(API_BASE + "/assets/" + logo_asset_id, timeout=15)
                                logo_response.raise_for_status()
                                logo_bytes = logo_response.content
                            st.subheader("Brand kit overlay preview")
                            st.image(render_brand_overlay(saved_brand_kit, logo_bytes), use_container_width=True)
                            st.caption("Preview colors and logo only; text/background contrast is checked in the quality warnings.")
                            if any(item.get("code") == "VISUAL_BRAND_LOW_CONTRAST" for item in generation.get("warnings", [])):
                                st.warning("Brand color contrast is below the WCAG 4.5:1 text-overlay threshold.")
                        for index, concept in enumerate(visual["output"]["concepts"]):
                            with st.container(border=True):
                                st.subheader(concept["name"])
                                st.write(concept["idea"])
                                st.write("**Scene:** " + concept["scene"])
                                st.write("**Mood and lighting:** " + concept["mood_and_lighting"])
                                palette = concept["color_palette"]
                                swatches = " ".join(f'<span style="background:{color["hex"]};padding:8px 14px;color:#000;border:1px solid #999" title="{color["role"]}">{color["hex"]}</span>' for color in palette)
                                st.markdown(swatches, unsafe_allow_html=True)
                                st.write("Typography: " + concept["typography"]["heading_style"] + " / " + concept["typography"]["body_style"])
                                st.write("On-image text: " + concept["on_image_text"]["headline"] + " - " + concept["on_image_text"]["cta"])
                                for format_name, prompt in concept["image_prompts"].items():
                                    format_config = VISUAL_FORMATS[format_name]
                                    st.caption(format_config["name"] + " - " + format_config["aspect_ratio"] + " - " + str(format_config["width"]) + "x" + str(format_config["height"]))
                                    st.text_area(format_name + " prompt", value=prompt, key=f"visual-prompt-{index}-{format_name}")
                                    copy_button("Copy image prompt", prompt, f"prompt-{index}-{format_name}")
                                    if st.button("Generate image", key=f"generate-image-{index}-{format_name}", help="May use configured image-provider cost"):
                                        try:
                                            response = requests.post(API_BASE + "/campaigns/visuals/images", json={
                                                "request": {"product_input": st.session_state.validated_input["validated"], "audience_profile": st.session_state.audience_profile, "brief": st.session_state.campaign_brief},
                                                "concept_index": index, "format": format_name,
                                            }, timeout=60)
                                            response.raise_for_status()
                                            asset = response.json()
                                            st.image(API_BASE + "/assets/" + asset["id"] if "id" in asset else None, caption=("Placeholder image (demo mode)" if asset.get("placeholder") else "Generated image"), use_container_width=True)
                                        except requests.RequestException as exc:
                                            st.error("Image generation failed: " + str(exc))
                                    copy_button("Copy negative prompt", concept["negative_prompt"], f"negative-{index}-{format_name}")
                                if st.button("Regenerate concept", key=f"regen-visual-{index}"):
                                    response = requests.post(API_BASE + "/campaigns/visuals/regenerate", params={"concept": index}, json={
                                        "product_input": st.session_state.validated_input["validated"], "audience_profile": st.session_state.audience_profile, "brief": st.session_state.campaign_brief,
                                    }, timeout=60)
                                    response.raise_for_status()
                                    st.success("Concept regeneration requested.")
                    else:
                        st.error(visual.get("error", "Visual concept generation failed."))
                with result_tabs[4]:
                    video = generation["modules"].get("video", {})
                    if video.get("status") == "success":
                        st.warning("Synthetic voice disclosure: AI-generated narration should be disclosed where required. Voice cloning is out of scope.")
                        for duration in (15, 30, 60):
                            script = video["output"].get(str(duration))
                            if not script:
                                continue
                            with st.container(border=True):
                                st.subheader(str(duration) + " seconds - " + script["title"])
                                st.write("**Hook:** " + script["hook"])
                                st.write("**Concept:** " + script["concept"])
                                st.dataframe([{"Scene":scene["scene_number"],"Start":scene["start"],"End":scene["end"],"Visual":scene["visual"],"On-screen text":scene["on_screen_text"],"Music":scene["music_mood"]} for scene in script["scenes"]], use_container_width=True, hide_index=True)
                                st.text_area("Narration", value=script["narration"], key=f"video-narration-{duration}")
                                copy_button("Copy narration", script["narration"], f"video-copy-{duration}")
                                full_script = script["narration"] + "\n" + "\n".join(scene["on_screen_text"] + " - " + scene["visual"] for scene in script["scenes"])
                                copy_button("Copy full script", full_script, f"video-full-{duration}")
                                st.caption("Estimated spoken duration: " + str(script["estimated_spoken_seconds"]) + " seconds; target " + str(duration) + " seconds")
                                if st.button("Regenerate " + str(duration) + " seconds", key=f"regen-video-{duration}"):
                                    response = requests.post(API_BASE + "/campaigns/video/regenerate", params={"duration":duration}, json={
                                        "product_input": st.session_state.validated_input["validated"], "audience_profile": st.session_state.audience_profile, "brief": st.session_state.campaign_brief,
                                    }, timeout=60)
                                    response.raise_for_status()
                                    st.success(str(duration) + "-second script regenerated.")
                        voice_style = st.selectbox("Voice style", VOICE_OPTIONS["styles"])
                        voice_pace = st.selectbox("Voice pace", VOICE_OPTIONS["paces"])
                        voice_language = st.selectbox("Voice language", VOICE_OPTIONS["languages"])
                        st.caption("Audio generations configured limit: " + os.getenv("TTS_LIMIT_PER_CAMPAIGN", "6") + " per campaign. Estimated cost: check current provider pricing.")
                        if st.button("Generate voice-over", help="Uses up to one configured TTS generation"):
                            duration = st.selectbox("Voice-over duration", [15,30,60], key="voice-duration")
                            response = requests.post(API_BASE + "/campaigns/video/voiceover", json={
                                "request":{"product_input":st.session_state.validated_input["validated"],"audience_profile":st.session_state.audience_profile,"brief":st.session_state.campaign_brief},
                                "duration":duration,"voice":voice_style,"pace":voice_pace,"language":voice_language,
                            }, timeout=60)
                            response.raise_for_status()
                            asset = response.json()
                            st.audio(API_BASE + "/assets/" + asset["id"])
                            if asset.get("placeholder"):
                                st.caption("Placeholder audio (demo mode)")
                            audio_content = requests.get(API_BASE + "/assets/" + asset["id"], timeout=20)
                            audio_content.raise_for_status()
                            st.download_button("Download voice-over", audio_content.content, file_name=asset["id"] + ".wav", mime="audio/wav", key="download-voiceover")
                        if st.button("Build draft video", help="Starts a background FFmpeg job when FFmpeg is available"):
                            duration = st.selectbox("Draft video duration", [15,30,60], key="assembly-duration")
                            response = requests.post(API_BASE + "/campaigns/video/assemble", json={
                                "request":{"product_input":st.session_state.validated_input["validated"],"audience_profile":st.session_state.audience_profile,"brief":st.session_state.campaign_brief},"duration":duration,
                            }, timeout=60)
                            response.raise_for_status()
                            st.session_state.video_job = response.json()["job_id"]
                    else:
                        st.error(video.get("error", "Video script generation failed. Individual durations may be retried."))
                    if st.session_state.get("video_job"):
                        job = requests.get(API_BASE + "/jobs/" + st.session_state.video_job, timeout=10)
                        job.raise_for_status()
                        status = job.json()
                        st.progress(status["progress"] / 100)
                        st.write(status["status"])
                        if status.get("error"):
                            st.error(status["error"])
                        if status["status"] == "completed" and status.get("asset_id"):
                            asset_url = API_BASE + "/assets/" + status["asset_id"]
                            st.video(asset_url)
                            st.caption("Placeholder video (demo mode)" if os.getenv("TTS_PROVIDER", "mock") == "mock" else "Draft video")
                            video_content = requests.get(asset_url, timeout=20)
                            video_content.raise_for_status()
                            st.download_button("Download draft video", video_content.content, file_name=status["asset_id"] + ".mp4", mime="video/mp4", key="download-video")
                with result_tabs[5]:
                    quality = generation.get("quality")
                    if quality is not None:
                        status = quality["overall_status"]
                        severity_icon = {"pass": "PASS", "pass_with_warnings": "WARNING", "needs_review": "MAJOR", "blocked": "BLOCKED"}
                        st.subheader(f"{severity_icon[status]} - Quality score: {quality['overall_score']:.0f}/100")
                        st.write("Automated checks reduce risk but do not provide legal or regulatory advice.")
                        cols = st.columns(max(1, len(quality["module_scores"])))
                        for column, (module, score) in zip(cols, quality["module_scores"].items()):
                            column.metric(module.title(), f"{score:.0f}")
                        if not quality["findings"]:
                            st.success("No issues found.")
                        for finding in quality["findings"]:
                            icon = {"info": "INFO", "warning": "WARNING", "major": "MAJOR", "critical": "CRITICAL"}[finding["severity"]]
                            with st.expander(f"{icon} - {finding['check_name']} - {finding['module']}"):
                                st.write(finding["explanation"])
                                st.code(finding["text"])
                                st.caption("Suggested fix: " + finding["suggested_fix"])
                                if finding["auto_fix_available"]:
                                    if st.button("Apply auto-fix", key=f"quality-fix-{finding['id']}"):
                                        response = requests.post(
                                            API_BASE + "/campaigns/quality/autofix",
                                            params={"campaign_reference": st.session_state.validated_input["validated"]["product_name"].lower()},
                                            json={"finding_ids": [finding["id"]]},
                                            timeout=30,
                                        )
                                        response.raise_for_status()
                                        st.json(response.json()["diffs"])
                        critical_or_major = any(f["status"] == "open" and f["severity"] in {"critical", "major"} for f in quality["findings"])
                        if critical_or_major:
                            st.button("Approve campaign", disabled=True, help="Fix or acknowledge critical and major findings before approval.")
                        else:
                            st.button("Approve campaign", disabled=False)
                    elif generation.get("quality_error"):
                        st.error(generation["quality_error"])
                    else:
                        st.info("No quality report is available. Run the quality check again.")
                for warning in generation["warnings"]:
                    st.warning(warning["message"])
                st.caption("Estimated tokens used: " + str(generation["estimated_tokens_used"]))

st.divider()
st.header("Campaign history and exports")
try:
    history_response = requests.get(API_BASE + "/campaigns", timeout=10)
    history_response.raise_for_status()
    campaign_rows = history_response.json()
except requests.RequestException as exc:
    campaign_rows = []
    st.error("Campaign history is unavailable: " + str(exc))

if not campaign_rows:
    st.info("No campaigns saved yet.")
else:
    selected_campaign = st.selectbox(
        "Open a saved campaign",
        campaign_rows,
        format_func=lambda item: f"{item['name']} — {item['status']}",
        key="history_campaign",
    )
    selected_id = selected_campaign["id"]
    action_columns = st.columns(3)
    if action_columns[0].button("Duplicate campaign", key="history-duplicate"):
        response = requests.post(API_BASE + f"/campaigns/{selected_id}/duplicate", timeout=10)
        if response.ok:
            st.success("Campaign duplicated as a draft.")
            st.rerun()
        else:
            st.error(response.text)
    if action_columns[1].button("Delete campaign", key="history-delete"):
        st.session_state.confirm_campaign_delete = selected_id
    if st.session_state.get("confirm_campaign_delete") == selected_id:
        st.warning("Delete this campaign and its saved exports?")
        if st.button("Confirm delete", key="history-confirm-delete"):
            response = requests.delete(API_BASE + f"/campaigns/{selected_id}", params={"confirm": "true"}, timeout=10)
            if response.ok:
                st.session_state.confirm_campaign_delete = None
                st.rerun()
            else:
                st.error(response.text)
    try:
        package_response = requests.get(API_BASE + f"/campaigns/{selected_id}/package", timeout=10)
        package_response.raise_for_status()
        package = package_response.json()
        st.caption("Approval status: " + str(package["approval"]["status"]))
        st.write("Latest package summary")
        st.json({key: package[key] for key in ("quality_summary", "approval", "descriptions", "promo", "social", "visuals", "video")})
        st.subheader("Edit or revert a section")
        section_name = st.selectbox("Section", ["descriptions", "promo", "social", "visuals", "video"], key="history-section")
        section_data = package[section_name]["content"]
        edited_json = st.text_area("Section JSON", value=json.dumps(section_data, ensure_ascii=False, indent=2), height=220)
        edit_columns = st.columns(2)
        if edit_columns[0].button("Save section edit", key="history-save-section"):
            try:
                edited_value = json.loads(edited_json)
                response = requests.patch(
                    API_BASE + f"/campaigns/{selected_id}/sections/{section_name}",
                    json={"value": edited_value, "source": "manual_edit"},
                    timeout=15,
                )
                if response.ok:
                    st.success("Edit saved. Approval now needs review.")
                    st.rerun()
                else:
                    st.error(response.json().get("error", {}).get("message", response.text))
            except json.JSONDecodeError:
                st.error("Section JSON is invalid.")
        if edit_columns[1].button("Revert previous edit", key="history-revert-section"):
            response = requests.post(API_BASE + f"/campaigns/{selected_id}/sections/{section_name}/revert", timeout=10)
            if response.ok:
                st.success("Previous section value restored.")
                st.rerun()
            else:
                st.error(response.json().get("error", {}).get("message", response.text))
        if st.button("Run quality check on saved campaign", key="history-quality"):
            response = requests.post(API_BASE + f"/campaigns/{selected_id}/quality", timeout=20)
            if response.ok:
                st.session_state.history_quality = response.json()
                st.success("Quality report saved.")
            else:
                st.error(response.text)
        quality_data = st.session_state.get("history_quality")
        if quality_data and quality_data.get("campaign_reference") == selected_id:
            st.write("Quality status: " + quality_data["overall_status"])
            approver = st.text_input("Approved by", key="history-approver")
            if st.button("Approve current report", key="history-approve"):
                response = requests.post(
                    API_BASE + f"/campaigns/{selected_id}/approve",
                    params={"approved_by": approver or "user", "report_id": quality_data["report_id"]},
                    timeout=10,
                )
                if response.ok:
                    st.success("Campaign approved.")
                    st.rerun()
                else:
                    st.error(response.json().get("error", {}).get("message", response.text))
        export_format = st.selectbox("Export format", ["json", "docx", "pdf", "zip"], key="history-export-format")
        if st.button("Create export", key="history-export"):
            response = requests.post(
                API_BASE + f"/campaigns/{selected_id}/exports",
                json={"format": export_format},
                timeout=60,
            )
            if response.ok:
                export_id = response.json()["export_id"]
                download = requests.get(API_BASE + f"/exports/{export_id}", timeout=30)
                if download.ok:
                    st.download_button(
                        "Download export",
                        data=download.content,
                        file_name=f"{selected_campaign['name']}.{export_format}",
                        key=f"history-download-{export_id}",
                    )
                else:
                    st.error("Export was created, but download failed: " + download.text)
            else:
                st.error(response.json().get("error", {}).get("message", response.text))
        exports_response = requests.get(API_BASE + f"/campaigns/{selected_id}/exports", timeout=10)
        if exports_response.ok and exports_response.json():
            st.subheader("Export history")
            st.json(exports_response.json())
    except requests.RequestException as exc:
        st.error("Could not open this campaign: " + str(exc))
