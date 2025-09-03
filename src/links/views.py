from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import LinkCreateSerializer


class LinkCreateAPIView( CreateAPIView):
    serializer_class = LinkCreateSerializer
