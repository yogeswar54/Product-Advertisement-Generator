# Stage 7 Summary

## What Was Built

- Configurable 15, 30, and 60-second video formats and voice options.
- Versioned video script prompt and reusable-bottle examples.
- Video Script Generator with JSON repair and continuous scene tables.
- Spoken-duration, timeline, hook, CTA, claim, copyright, and stage-direction checks.
- Mock and hosted-compatible TTS providers.
- Local WAV audio storage, metadata, limits, and placeholder audio.
- User-triggered mock FFmpeg assembly jobs with progress and safe media serving.
- Video regeneration, voice-over, assembly, and job-status APIs.
- Streamlit Video tab with scripts, scene tables, narration copy, audio player, job progress, and disclosure.
- Four-persona video comparison script.
- Configuration-backed speaking pace, voice pace multipliers, and draft-video resolution.
- Cache reuse for identical TTS requests and download controls for audio/video assets.

## Generation Approach

Stage 7 uses one structured text-model call for all three durations. This keeps one campaign brief and prompt context consistent and makes partial-duration retries available after schema validation. The implementation also accepts a per-duration regenerate request.

## Orchestration Choice

Video scripts run in the same brief-first parallel text generation wave as description, promo, social, and visual concepts. Audio and assembly are separate user-triggered actions and are never invoked by default generation.

## Prompt Version

- `video_script_v1`

## Mock Mode

```powershell
$env:LLM_PROVIDER="mock"
$env:TTS_PROVIDER="mock"
$env:IMAGE_PROVIDER="mock"
$env:PYTHONPATH="backend"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
python -m streamlit run frontend/app.py
```

Mock video assembly depends on FFmpeg being installed. If FFmpeg is absent, the API returns an install-hint job failure without blocking the rest of the app.

## Live Mode

Stage 1 did not select named text or speech vendors. Configure approved hosted-compatible endpoints and keys locally:

```powershell
$env:LLM_PROVIDER="hosted"
$env:LLM_API_KEY="set-through-local-environment-only"
$env:TTS_PROVIDER="hosted"
$env:TTS_API_KEY="set-through-local-environment-only"
$env:TTS_API_BASE_URL="approved-provider-base-url"
$env:TTS_MODEL="approved-tts-model"
```

## Test Results

- Full Stages 3-7 suite: 112 tests passed.
- Stage 7 focused suite: 21 tests passed.
- Stage 7 new-module coverage: 92%.
- Video schema and example validate under Draft 2020-12.
- Mock WAV synthesis produces valid local audio.
- Mock assembly reports asynchronous progress and fails gracefully without FFmpeg.
- Live provider calls were not run without keys.

## Assumptions

- Configurable defaults use the base words-per-second and pace multipliers in `config/voice_options.json`.
- Duration tolerance is checked at 20 seconds in the starting implementation and should be tightened after evidence.
- Voice disclosure is mandatory in the UI as a policy reminder, not legal advice.
- Draft assembly resolution and codec settings are modest defaults requiring verification.

## Corrections

1. Referenced Stage 2 video documents and `video_output.schema.json` were absent; minimal contracts were reconstructed from Stage 1 and this Stage 7 attachment.
2. TTS and LLM vendors remain unresolved because Stage 1 named hosted services but no vendor.
3. Prompt loading now supports the underscored `video_script_v1` name.
4. Asset metadata can distinguish image, audio, and video records without changing database schema.

## Open Questions Before Stage 8

1. Approve hosted text and TTS vendors.
2. Confirm production duration tolerance and speaking pace.
3. Confirm FFmpeg installation in deployment environments.
4. Choose final resolution and codec settings for draft videos.
5. Confirm legal disclosure text for the supported jurisdictions.

## Stage 8 Preview

Stage 8 Quality, Safety, and Consistency will reuse video scripts, duration/timeline checks, TTS metadata, campaign briefs, visual/social/text outputs, provider retry/repair, and asset identifiers to produce one campaign-wide quality report. It should not replace the Stage 7 lightweight warnings.

## Suggestions for Later

- Exact rendered audio-duration comparison.
- Captions and burned-in subtitles.
- Persistent assembly job queue.
- Cloud media storage and transcoding.
