from django.utils import timezone
from django.shortcuts import redirect, get_object_or_404
from django.views import View
from django.http import HttpResponseGone, Http404
from rest_framework.generics import CreateAPIView
from django.views import View
from rest_framework.response import Response
from rest_framework import status
from .serializers import LinkCreateSerializer
from .models import Link
from .services.base62 import decoder as _decode_base64


class LinkCreateAPIView( CreateAPIView):
    serializer_class = LinkCreateSerializer

class RedirectView(View):
    def get(self, request, code, **kw):
        
        # DB fallback
        link = self._get_link_or_404(code)
        if link.is_expired:
            return HttpResponseGone("Link expired")
        
        return redirect(link.original_url)
    
    @staticmethod
    def _get_link_or_404(code: str) -> Link:
        link_id = _decode_base64(code)
        qs = Link.objects.only("original_url", "expire_at")
        return get_object_or_404(qs, pk=link_id)