# ADR-E4: Per-Campaign Brand Kit

- **Status:** Accepted for Stage 12; implementation is opt-in.

## Context

Stage 6 already defines visual palettes, on-image text, and a WCAG contrast check. Stage 9
persists campaigns and exports DOCX/PDF packages. There is no brand-kit object or logo-upload API.
Stage 1 identifies user-supplied asset rights as an unresolved risk. SVG can contain active
content, and neither a font name nor a user's confirmation proves license rights.

## Options

1. Add global brand configuration shared across campaigns.
2. Add a per-campaign brand kit, with optional raster logo upload, validated colors, font note, and
   user rights confirmation.
3. Defer brand assets and only accept palette suggestions as plain text.

## Decision

Choose option 2 behind `ENHANCE_BRAND_KIT=off` by default. Store the kit with its campaign, not as
global user state. Validate primary/secondary hex colors. Accept only supported raster logo
formats, enforce the existing configured upload-size limit, verify the image, and re-encode it
before storing under the configured asset storage root. Reject SVG uploads. Apply the saved colors
as preferred visual palette values, use the existing contrast check for every text overlay, and
include the logo in previews and DOCX/PDF only when the owner uploaded it.

Require the exact confirmation “I have the rights to use this logo and font.” Treat it as a
user-entered confirmation only. Persist a font category or name and a licensing note; never assert
that rights were verified.

## Consequences

- No campaign receives a logo or colors unless the feature is enabled and a user supplied them.
- Asset files remain within the configured storage folder and are linked to a campaign.
- SVG script risks are avoided by rejection; safe raster re-encoding limits metadata and format
  ambiguity.
- Existing visual contrast logic is reused; low-contrast overlays must be reported rather than
  silently accepted.
- A campaign-scoped kit increases asset and schema surface area and requires tests for deletion,
  duplication, export, and feature-flag-off behavior.
