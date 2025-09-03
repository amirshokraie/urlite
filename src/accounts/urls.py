from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    UserRegisterAPIView,
    UserRetrieveAPIView,
    PasswordChangeAPIView,
)

app_name = "accounts"

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path("register/", UserRegisterAPIView.as_view(), name="register"),
    path("me/", UserRetrieveAPIView.as_view(), name="me"),
    path("password-change/", PasswordChangeAPIView.as_view(), name="pw_change"),
]
