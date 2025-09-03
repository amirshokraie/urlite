from django.shortcuts import redirect
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import LinkCreateSerializer
from .models import Link


class LinkCreateAPIView( CreateAPIView):
    serializer_class = LinkCreateSerializer

class RedirectAPIView(APIView):
    def get(self, request, code, **kw):
        pass