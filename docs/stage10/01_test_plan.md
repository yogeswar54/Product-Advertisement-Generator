# Stage 10 Test Plan

## Strategy

Automated unit, API, integration, reliability, security, metrics, and mock-mode smoke tests verify
the implemented Stages 1–9 behavior. Browser E2E coverage is required before release, but the
current Streamlit UI does not expose Playwright automation hooks; Playwright is the selected tool
and the flows in this plan remain executable once those hooks are available.

## Environments

- Mock mode: no API key and no network access required.
- Live mode: optional; real vendor metrics are recorded only when credentials are configured.

## Entry and exit criteria

- Entry: Stage 3–9 suites pass.
- Exit: no critical or major defects, full automated suite passes, security suite passes, and any
  unrun browser/human checks are documented rather than represented as passed.

## Defect severity

- Critical: security breach, data loss, export bypass, or unusable core flow.
- Major: core requirement fails without a safe workaround.
- Minor: limited incorrect behavior with a workaround.
- Cosmetic: visual or copy issue without functional impact.
