from django.http.request import HttpRequest as DjangoRequest
from rest_framework.request import Request as RestFrameworkRequest


def get_client_ip(request: DjangoRequest | RestFrameworkRequest) -> str | None:
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        ip = xff.split(",")[0].strip()
        if ip:
            return ip
    return request.META.get("REMOTE_ADDR")


def get_user_agent(request: DjangoRequest | RestFrameworkRequest) -> str | None:
    return request.META.get("HTTP_USER_AGENT")