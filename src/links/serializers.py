from django.utils import timezone
from rest_framework import serializers
from .models import Link
from .mixins import ShortURLMixin


class LinkCreateSerializer(ShortURLMixin, serializers.ModelSerializer):
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

    
class LinkListSerializer(ShortURLMixin, serializers.ModelSerializer):
    short_url = serializers.SerializerMethodField()

    class Meta:
        model = Link
        fields = ("original_url", "expire_at", "created_at", "short_url")