# User Guide

Use the provided water bottle example or enter your own supported product. Keep the provider in
mock mode for a local demonstration because mock mode requires no API key.

1. Enter the product name, category, features, price, USP, brand, voice, goal, platforms, and language. Hindi is selectable only when `ENHANCE_HINDI=on`.
2. Select a predefined persona or add custom audience notes. Custom notes supplement, rather than replace, the persona.
3. Review the campaign brief and edit it if needed.
4. Generate the campaign. Review Descriptions, Promo, Social, Visuals, and Video.
5. Run quality checks and apply safe fixes where offered.
6. Resolve or acknowledge findings, then approve the current quality report.
7. Open History to duplicate, reopen, or delete campaigns. Deletion requires confirmation.
8. Edit text inline and use Revert to restore the last stored value.
9. Export JSON, DOCX, PDF, or ZIP only when approval permits it.

All exports are drafts. Automated checks do not guarantee factual accuracy, legality, regulatory
compliance, rights clearance, or advertising performance. Human review is required before publishing.

## Optional campaign brand kit

When `ENHANCE_BRAND_KIT=on`, Campaign settings offers an optional per-campaign brand kit with
colors, a font name/category and licensing note, and an optional PNG, JPEG, or WebP logo. SVG logos
are rejected. Confirming logo/font rights is your responsibility; the checkbox does not verify
ownership or licensing. Uploaded logos are re-encoded and stored with the campaign under the
configured local asset storage folder. The Visuals tab shows a color-and-logo overlay preview, and
uploaded logos are embedded in DOCX and PDF exports. Brand-color contrast warnings require review.

Hindi generation is opt-in. Hindi output has not been reviewed by a native speaker. Hindi
readability is not measured, and PDF/ZIP exports are unavailable until a Devanagari-capable font is
embedded. DOCX and JSON remain available, subject to normal campaign approval.
