version: calendar_v1
temperature: 0.4
max_tokens: 1200

[SYSTEM]
Create a seven-day campaign calendar using only selected platforms and supplied facts. Posting time slots are estimated suggestions that must be tested. Never invent social proof.
[AUDIENCE INJECTION]
Audience: {{audience_name}}
Tone: {{audience_tone}}
Motivations: {{audience_motivations}}
[BRIEF INJECTION]
Core message: {{core_message}}
Goal: {{campaign_goal}}
[PLATFORM RULES]
Selected platforms: {{selected_platforms}}
{{platform_rules}}
[OUTPUT FORMAT]
Return a JSON object with exactly a "calendar" array of seven entries matching social_output.schema.json. No markdown.
