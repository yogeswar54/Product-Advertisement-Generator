import os

from app.image_providers.base import ImageProvider
from app.image_providers.hosted import HostedImageProvider
from app.image_providers.mock import MockImageProvider


def get_image_provider() -> ImageProvider:
    return MockImageProvider() if os.getenv("IMAGE_PROVIDER", "mock").lower() == "mock" else HostedImageProvider()
