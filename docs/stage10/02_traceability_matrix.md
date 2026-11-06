# Requirements Traceability Matrix

| Requirement | MoSCoW | Test IDs | Type | Status | Evidence |
|---|---|---|---|---|---|
| FR-01 | Must | Existing Stage 3 input suite | Unit/API | Pass | `backend/tests/stage3/` |
| FR-02 | Must | Existing input validation suite | Unit/API | Pass | `backend/tests/stage3/test_inputs.py` |
| FR-03 | Should | TC-CMP-001 | Manual/API | Partial | Draft API exists; dedicated Stage 10 test pending |
| FR-04 | Must | Existing audience suite | Unit/API | Pass | `backend/tests/stage3/` |
| FR-05 | Could | Existing audience suite | Unit/API | Partial | Custom notes supported in existing tests |
| FR-06 | Must | Existing brief suite | Unit/API | Pass | `backend/tests/stage3/` |
| FR-07 | Must | Existing brief suite | Unit/API | Pass | Brief used by orchestrator tests |
| FR-08 | Should | TC-UI-004 | E2E/manual | Partial | Streamlit hook not automated |
| FR-09 | Must | Existing description suite | Unit/API | Pass | `backend/tests/stage3/` |
| FR-10 | Must | Existing quality suite | Unit | Pass | `backend/tests/test_stage8_quality.py` |
| FR-11 | Must | Existing promo suite | Unit/API | Pass | `backend/tests/stage4/` |
| FR-12 | Should | Existing promo suite | Unit/API | Pass | Promo variants assertions |
| FR-13 | Must | Existing social suite | Unit/API | Pass | `backend/tests/stage5/` |
| FR-14 | Must | Existing calendar suite | Unit/API | Pass | `backend/tests/stage5/` |
| FR-15 | Must | Existing social hashtag/rule suite | Unit/API | Pass | `backend/tests/stage5/` |
| FR-16 | Must | Existing visual suite | Unit/API | Pass | `backend/tests/stage6/` |
| FR-17 | Should | Existing visual suite | Unit/API | Pass | `backend/tests/stage6/` |
| FR-18 | Must | Existing video suite | Unit/API | Pass | `backend/tests/stage7/` |
| FR-19 | Must | Existing video suite | Unit/API | Pass | `backend/tests/stage7/` |
| FR-20 | Could | Existing media provider suite | Unit | Partial | Optional provider mock coverage |
| FR-21 | Won't | N/A | N/A | Not testable | Explicitly deferred final video assembly |
| FR-22 | Must | Existing quality suite | Unit | Pass | Quality tests |
| FR-23 | Must | Existing quality suite | Unit | Pass | Unsupported fact tests |
| FR-24 | Should | Existing quality suite | Unit/API | Pass | Report model tests |
| FR-25 | Must | TC-EXP-001, Stage 9 export suite | Unit/API | Pass | `backend/tests/test_stage9_export.py` |
| FR-26 | Should | TC-EXP-002 | Unit/API | Partial | DOCX/PDF/ZIP implemented; Markdown not in Stage 9 scope |
| FR-27 | Won't | N/A | N/A | Not testable | Limited history/versioning implemented but full FR remains deferred |
| NFR-01 | Must | TC-PERF-001 | Performance | Partial | Run required; estimate not used as measured result |
| NFR-02 | Should | TC-PERF-002 | Performance | Partial | Real-provider timing not configured |
| NFR-03 | Should | TC-COST-001 | Cost | Partial | Mock no vendor cost measured |
| NFR-04 | Must | TC-REL-001 | Reliability | Partial | Mock partial-failure behavior tested in existing suites |
| NFR-05 | Must | TC-REL-002, Stage 9 persistence tests | Reliability/API | Partial | Database recovery implementation pending fault coverage |
| NFR-06 | Could | N/A | Deployment | Not testable here | Requires production deployment measurement |
| NFR-07 | Must | TC-SEC-007, TC-SEC-008 | Security | Partial | Repo secret patterns and sanitization checked |
| NFR-08 | Must | Existing quality/security tests | Quality/security | Pass | Human-review labels and restricted-category checks |
| NFR-09 | Must | TC-SEC-001 | Security | Pass | Prompt-injection and sanitization samples |
| NFR-10 | Should | TC-A11Y-001 | Accessibility/manual | Partial | Streamlit labels exist; automated browser audit not run |
| NFR-11 | Could | Existing language model tests | Unit | Not testable here | English-only MVP assumption |
| NFR-12 | Must | Existing UI and validation tests | UI/API | Partial | Retention behavior not browser-tested |
| NFR-13 | Should | TC-SEC-008 | Security | Partial | Repository/prompt logs require production audit |
| NFR-14 | Should | Provider tests | Unit | Pass | Hosted/mock provider abstraction |
| NFR-15 | Should | Stage 9 JSON/API tests | API | Pass | Campaign JSON package export |
