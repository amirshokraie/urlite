from django.urls import path

from .views import LinkCreateAPIView, RedirectAPIView

app_name = "links"

urlpatterns = [
    path('create/', LinkCreateAPIView.as_view(), name='create_link'),
    path('r/<str:code>/', RedirectAPIView.as_view(), name='redirect'),
]
