# Defect Log

| ID | Description | Steps to reproduce | Severity | Related test | Status | Fix summary |
|---|---|---|---|---|---|---|
| DEF-001 | Export allowed when the latest approved quality report was marked outdated. | Mark the report outdated; request another export. | Critical | `backend/tests/test_stage9_api.py::test_campaign_history_edit_approval_and_export_flow` | Fixed | Export gate now rejects outdated quality reports before rendering. |
| DEF-002 | JavaScript URL text was retained after normalization. | Normalize `javascript:alert(1)` through the text sanitizer. | Major | `tests/security/test_stage10_safety.py::test_stage10_xss_is_sanitized` | Fixed | Normalization now converts dangerous URL schemes to a non-executable `blocked:` scheme. |
| DEF-003 | Prompt-injection instructions in user-controlled product fields were not consistently flagged by input and content-quality checks. | Submit instruction-override and secret-exfiltration phrases in supported product text fields. | Major | `tests/security/test_stage10_safety.py::test_stage10_prompt_injection_samples_are_not_echoed` | Fixed | Expanded shared detection patterns and added 24 representative malicious-input cases across validation and quality checks. |
