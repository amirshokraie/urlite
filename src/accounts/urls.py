from django.urls import path
from .views import (
    UserRegisterAPIView,
    UserRetrieveAPIView,
    PasswordChangeAPIView,
)

app_name = "accounts"

urlpatterns = [
    path("register/", UserRegisterAPIView.as_view(), name="register"),
    path("me/", UserRetrieveAPIView.as_view(), name="me"),
    path("password-change/", PasswordChangeAPIView.as_view(), name="pw_change"),
]
