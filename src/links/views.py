from django.utils import timezone
from django.shortcuts import redirect, get_object_or_404
from django.views import View
from django.http import HttpResponseGone, Http404
from rest_framework.generics import CreateAPIView, ListAPIView
from django.views import View
from rest_framework import permissions
from rest_framework import status
from .serializers import LinkCreateSerializer, LinkListSerializer
from .models import Link
from .services.base62 import decoder as _decode_base64
from .services import cache as _cache
from .services.analytics import LinkAnalytics
from . import helpers


class LinkCreateAPIView( CreateAPIView):
    serializer_class = LinkCreateSerializer

class RedirectView(View):
    def get(self, request, code: str):
        # 1) Fast-fail if tombstoned
        if _cache.is_tombstoned(code):
            return HttpResponseGone("Link expired")

        # 2) Try cache
        url = _cache.get_cached_url(code)

        # 3) Fallback to DB
        if not url:
            link = self._get_link_or_404(code)
        if link.is_expired:
            _cache.mark_expired(code)
            return HttpResponseGone("Link expired")

        # Cache fresh mapping
        expire_ts = int(link.expire_at.timestamp()) if link.expire_at else None
        _cache.cache_url(code, link.original_url, expire_ts)
        url = link.original_url

        # 4) Record analytics, then redirect
        self._record(request, code)
        return redirect(url)

    @staticmethod
    def _get_link_or_404(code: str) -> Link:
        link_id = _decode_base64(code)
        qs = Link.objects.only("original_url", "expire_at")
        return get_object_or_404(qs, pk=link_id)

    def _record(self, request, code: str) -> None:
        ip = helpers.get_client_ip(request)
        ua = helpers.get_user_agent(request)
        LinkAnalytics.record_visit(code, ip, ua)
    
class UserLinkListAPIView(ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LinkListSerializer

    def get_queryset(self):
        return (
            Link.objects.filter(created_by=self.request.user)
            .only("original_url", "expire_at", "created_at")
            .order_by("-created_at")
        )