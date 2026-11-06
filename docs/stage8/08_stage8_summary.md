# Stage 8 Summary

## What Was Built

- Fact ledger for supplied product facts and numbers.
- Configured rule checks for unsupported facts, absolute claims, restricted categories, instruction echo, and personal data.
- Quality reports with module scores, severity, status, and rules/prompt versions.
- Safe mechanical auto-fix with reversible before/after diffs.
- Finding acknowledgement and section-regeneration actions.
- Campaign approval and revocation state.
- Quality API routes and a Streamlit Quality tab.
- Mock judge prompt files and deterministic mock judge support.
- Stage 8 fixture and evaluation script.

## Run in Mock Mode

```powershell
$env:LLM_PROVIDER="mock"
$env:QUALITY_LLM_JUDGE="off"
$env:PYTHONPATH="backend"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
python -m streamlit run frontend/app.py
```

## Live Judge Mode

Set `QUALITY_LLM_JUDGE=on` and use approved hosted provider credentials locally. Judge output is advisory for soft judgments; hard rule failures remain blocking. Judge calls are cached by content, rules version, prompt version, and model name.

## Test and Evaluation Results

- Full Stages 3-8 suite: 118 tests passed.
- Stage 8 focused suite: 6 tests passed.
- Quality core is above the required coverage target in the measured modules.
- Evaluation used the deterministic mock provider, not a real model.

## Scoring

The report applies severity weights from `config/quality_rules.json`: overall score starts at 100 and subtracts the configured weight for each finding. Scores are relative indicators, not guarantees.

## Status Rules

- `blocked`: an open critical finding.
- `needs_review`: an open major finding, no critical finding.
- `pass_with_warnings`: warnings or info only.
- `pass`: no findings.

## Rules and Prompt Versions

- Rules: `quality-rules-v1`
- Judge prompts: `judge_tone_v1`, `judge_consistency_v1`, `judge_facts_v1`

## Assumptions and Corrections

- Referenced Stage 2 quality documents and schemas were absent; minimal compatible Stage 8 contracts were restored from the Stage 8 attachment and repository conventions.
- `quality_rules.json` was malformed in the repository and was replaced with the starting reviewed configuration.
- In-memory campaign quality and approval state is retained for the MVP because persistence is outside this stage.
- Personal, medical, financial, alcohol, and tobacco lists remain starting versions requiring expansion.

## Open Questions Before Stage 9

1. Approve persistence for quality reports and campaign approvals.
2. Select hosted judge vendors and compliance thresholds.
3. Confirm jurisdiction-specific legal review requirements.
4. Define export signing and approval evidence format.

## Stage 9 Preview

Stage 9 Package Assembly, Editing, and Export will consume the approved Stage 8 report ID, campaign approval state, quality finding status, fact ledger, and rules/prompt versions before allowing export.
