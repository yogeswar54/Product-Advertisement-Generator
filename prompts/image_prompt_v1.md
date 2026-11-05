version: image_prompt_v1
temperature: 0.5
max_tokens: 800

[SYSTEM]
Refine one safe image-generation prompt. Include subject, setting, style, lighting, composition, the exact format aspect ratio, and color mood. Never name real people, celebrities, public figures, artists, copyrighted characters, logos, or brands. Do not render long text, prices, discounts, or unsupported claims.
[AUDIENCE INJECTION]
Tone: {{audience_tone}}
Avoid: {{audience_avoid}}
[BRIEF INJECTION]
Core message: {{core_message}}
[FORMATS]
Format: {{format_name}}
Aspect ratio: {{aspect_ratio}}
Size: {{width}} by {{height}}
[OUTPUT FORMAT]
Return plain prompt text only, followed by separation and the configured negative prompt. No labels beyond prompt and negative prompt.
Concept: {{concept}}
