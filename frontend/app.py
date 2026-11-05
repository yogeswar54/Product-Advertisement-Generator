from __future__ import annotations

import html
import json
import os

import requests
import streamlit as st
from pathlib import Path

API_BASE = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
PLATFORM_OPTIONS = ["instagram", "linkedin", "x", "facebook", "whatsapp"]
PLATFORM_RULES = json.loads((Path(__file__).resolve().parents[1] / "config/platform_rules.json").read_text(encoding="utf-8"))
VISUAL_FORMATS = json.loads((Path(__file__).resolve().parents[1] / "config/visual_formats.json").read_text(encoding="utf-8"))
VOICE_OPTIONS = json.loads((Path(__file__).resolve().parents[1] / "config/voice_options.json").read_text(encoding="utf-8"))

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
    language = st.text_input("Language *", value="en-US", key="language")

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
            "language": st.session_state.language,
            "product_image": None,
            "competitor_info": st.session_state.competitor_info,
        }
        try:
            validation = requests.post(API_BASE + "/inputs/validate", json=payload, timeout=10)
            validation.raise_for_status()
            st.session_state.validated_input = validation.json()
            audience_request = {"persona_id": persona_names[selected_name]} if persona_names[selected_name] != "__custom__" else {"custom_audience": custom}
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
                    except requests.RequestException as exc:
                        st.error("Generation failed: " + str(exc))
            if st.session_state.get("generation"):
                generation = st.session_state.generation
                result_tabs = st.tabs(["Descriptions", "Promo", "Social", "Visuals", "Video"])
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
                for warning in generation["warnings"]:
                    st.warning(warning["message"])
                st.caption("Estimated tokens used: " + str(generation["estimated_tokens_used"]))
