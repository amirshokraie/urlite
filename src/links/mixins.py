from urllib.parse import urljoin
from django.conf import settings
from rest_framework.reverse import reverse
from .models import Link


class ShortURLMixin:
    def get_short_url(self, obj: Link) -> str:
        request = self.context.get("request")
        # absolute when request is present
        absolute_or_path = reverse("links:redirect", kwargs={"code": obj.code}, request=request)
        if request:
            return absolute_or_path
        # fallback to BASE_URL (or return relative path)
        base = getattr(settings, "BASE_URL", "").rstrip("/")
        return (
            urljoin(base + "/", absolute_or_path.lstrip("/")) 
            if base 
            else absolute_or_path
        )