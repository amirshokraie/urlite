from urllib.parse import urljoin
from django.conf import settings
from django.utils import timezone
from rest_framework import serializers
from rest_framework.reverse import reverse
from .models import Link


class LinkCreateSerializer(serializers.ModelSerializer):
    original_url = serializers.URLField(write_only=True, max_length=2048)
    expire_at = serializers.DateTimeField(required=False, allow_null=True)
    short_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Link
        fields = ("original_url", "expire_at", "short_url")

    def validate_expire_at(self, value):
        if value and value <= timezone.now():
            raise serializers.ValidationError("expire_at must be in the future.")
        return value

    def create(self, validated_data):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        created_by = user if (user and user.is_authenticated) else None
        return Link.objects.create(created_by=created_by, **validated_data)

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
