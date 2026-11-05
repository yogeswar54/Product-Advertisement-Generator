from __future__ import annotations

import io
import re
from pathlib import Path

from PIL import Image, ImageDraw

from app.image_providers.base import ImageProvider, ImageProviderResult


class MockImageProvider(ImageProvider):
    def generate_image(self, prompt: str, negative_prompt: str, width: int, height: int, reference_image: Path | None = None) -> ImageProviderResult:
        colors = re.findall(r"#[0-9A-Fa-f]{6}", prompt)
        color = colors[0] if colors else "#D9E5F2"
        image = Image.new("RGB", (width, height), color)
        draw = ImageDraw.Draw(image)
        draw.rectangle((int(width * 0.08), int(height * 0.08), int(width * 0.92), int(height * 0.92)), outline="#172033", width=max(2, width // 240))
        label = "Placeholder image"
        draw.text((int(width * 0.12), int(height * 0.12)), label, fill="#172033")
        output = io.BytesIO()
        image.save(output, format="PNG")
        return ImageProviderResult(content=output.getvalue(), provider="mock", model="mock-image-v1")
