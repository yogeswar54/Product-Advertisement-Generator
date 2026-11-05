# Stage 1 Input and Output Specification

Field names in this document are the canonical names used by campaign briefs, JSON samples, and implementation planning.

## 1. Input Fields

| Field name | Type | Required | Example | Validation rule |
|---|---|---|---|---|
| `product_name` | string | Yes | `FlowSip Reusable Bottle` | 1-100 characters; no control characters. |
| `category` | string | Yes | `Reusable water bottles` | 1-100 characters; free text with autocomplete. |
| `key_features` | array[string] | Yes | `["18-hour cold retention", "BPA-free materials", "700 ml capacity"]` | 1-12 unique items; each 1-120 characters. |
| `price` | string or number | No | `29.99` | If present, use a non-negative number and optional `currency` in a separate UI value. |
| `usp` | string | Yes | `A leak-resistant bottle with a wide, easy-clean opening` | 1-300 characters. |
| `brand_name` | string | No | `FlowSip` | 0-100 characters. |
| `brand_voice` | string/enum | Yes | `Friendly and practical` | Free text or one configured value, 1-100 characters. |
| `target_audience` | string/persona ID | Yes | `young_professionals` | Must match a persona ID in `data/personas.json` or a custom-audience label. |
| `campaign_goal` | enum/string | Yes | `Increase product-page conversions` | 1-150 characters; configured goals preferred. |
| `platforms` | array[enum] | Yes | `["instagram", "linkedin", "whatsapp"]` | 1-6 allowed values: instagram, linkedin, x, facebook, whatsapp. |
| `language` | string (BCP 47) | Yes | `en-US` | Supported locale format; MVP supports `en-US`. |
| `product_image` | image file or URL | No | Product PNG/URL | PNG/JPEG/WebP; maximum 10 MB; no executable or HTML content. |
| `competitor_info` | string | No | `Comparison notes provided by the user` | Maximum 1,500 characters; never copied from protected text. |

## 2. Outputs

| Output | Format | Length limit | Producing module |
|---|---|---|---|
| Short product description | string | 20-50 words | Description |
| Medium product description | string | 70-120 words | Description |
| Long product description | string | 180-300 words | Description |
| Headlines | array[string] | 3-8 items; 12-60 characters each | Promotional Text |
| Taglines | array[string] | 3 items; 3-12 words each | Promotional Text |
| Ad copy | string | 50-160 words | Promotional Text |
| CTAs | array[string] | 5-10 items; 1-6 words each | Promotional Text |
| A/B variants | array[object] | 2 variants; each 50-160 words | Promotional Text |
| Instagram post | object | Caption maximum 2,200 characters; 3-8 hashtags | Social Media |
| LinkedIn post | object | 1,500 characters recommended | Social Media |
| X/Twitter post | object | 280 characters | Social Media |
| Facebook post | object | 1,000 characters recommended | Social Media |
| WhatsApp post | object | 1,600 characters; 1-2 links | Social Media |
| 7-day content calendar | array[object] | Exactly 7 entries | Social Media |
| Visual concepts | array[object] | 3 concepts; each prompt 50-300 words | Visual Concepts |
| 15-second narration | object | Approximately 30-45 spoken words | Video |
| 30-second narration | object | Approximately 65-85 spoken words | Video |
| 60-second narration | object | Approximately 130-160 spoken words | Video |
| TTS audio | audio file | Optional MP3/WAV | Video |
| Campaign quality report | object | One entry per check category | Quality Check |
| Complete campaign package | JSON/Markdown/ZIP | No fixed total limit | Export |

## 3. Campaign Brief Object

```json
{
  "core_message": "string",
  "tone": "string",
  "emotional_hook": "string",
  "key_benefits": ["string"],
  "audience_profile_reference": "persona id",
  "dos_and_donts": {
    "dos": ["string"],
    "donts": ["string"]
  }
}
```

- `core_message`: one memorable sentence connecting the product to the audience need.
- `tone`: up to five tone descriptors shared by all modules.
- `emotional_hook`: the primary emotional or practical reason to act.
- `key_benefits`: three to five product benefits in audience language, not unsupported feature claims.
- `audience_profile_reference`: persona ID from `data/personas.json`.
- `dos_and_donts`: shared writing and visual constraints that downstream modules must follow.

## 4. Sample Input JSON

```json
{
  "product_name": "FlowSip Reusable Bottle",
  "category": "Reusable water bottle",
  "key_features": [
    "700 ml capacity",
    "Keeps water cold for up to 18 hours",
    "Leak-resistant lid",
    "BPA-free materials"
  ],
  "price": 29.99,
  "usp": "A wide-mouth bottle that is easy to clean and designed for daily commuting",
  "brand_name": "FlowSip",
  "brand_voice": "Friendly, practical, and energetic",
  "target_audience": "young_professionals",
  "campaign_goal": "Increase product-page conversions",
  "platforms": ["instagram", "linkedin", "whatsapp"],
  "language": "en-US",
  "product_image": null,
  "competitor_info": ""
}
```

## 5. Shortened Sample Output JSON

```json
{
  "campaign_brief": {
    "core_message": "Carry cold, fresh water through a busy workday without extra fuss.",
    "tone": "Practical, optimistic, concise",
    "emotional_hook": "Effortless control and everyday readiness",
    "key_benefits": [
      "Cold water for up to 18 hours",
      "Leak-resistant daily carry",
      "Wide opening for easy cleaning"
    ],
    "audience_profile_reference": "young_professionals",
    "dos_and_donts": {
      "dos": ["Use practical benefits", "Keep sentences direct"],
      "donts": ["Promise medical results", "Use extreme urgency"]
    }
  },
  "descriptions": {
    "short": "Meet FlowSip: a 700 ml bottle that keeps water cold for up to 18 hours and fits neatly into the rhythm of a busy workday.",
    "medium": "FlowSip pairs a 700 ml capacity with a leak-resistant lid and a wide opening that is simple to clean. Take cold water from morning meetings to evening plans."
  },
  "promotional": {
    "headlines": ["Cold water. Clearer commute."],
    "taglines": ["Refresh your routine"],
    "ctas": ["Choose FlowSip"],
    "ab_variants": [
      {"id": "A", "hook": "Daily convenience", "copy": "Make the workday simpler with cold water ready when you are."},
      {"id": "B", "hook": "Leak-resistance", "copy": "Carry a leak-resistant bottle from desk to evening without packing anxiety."}
    ]
  },
  "social": {
    "instagram": {"caption": "Cold water, clear priorities. FlowSip is ready for the commute.", "hashtags": ["#FlowSip", "#DailyHydration", "#ReusableBottle"]},
    "calendar": [
      {"day": 1, "platform": "instagram", "format": "carousel", "topic": "Desk-to-evening routine", "cta": "See the bottle"}
    ]
  },
  "visual_concepts": [
    {"scene": "Bottle beside a laptop in morning window light", "mood": "Calm and capable", "palette": ["#FFFFFF", "#1F4B99", "#7BB661"]}
  ],
  "video": {
    "15_seconds": {"duration": 15, "voice_over": "From desk to evening, FlowSip keeps cold water close and your routine moving.", "scenes": [{"start": 0, "end": 5, "visual": "Bottle on a desk", "on_screen_text": "Ready for the workday"}]}
  },
  "quality_report": {"status": "review_required", "warnings": ["Confirm the 18-hour claim against product test evidence"]}
}
```
