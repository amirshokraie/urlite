from django.urls import path
from .views import (
    LinkCreateAPIView, 
    RedirectView,
    UserLinkListAPIView,
    AnalyticsAPIView,
    )

app_name = "links"

urlpatterns = [
    path('create/', LinkCreateAPIView.as_view(), name='create_link'),
    path('r/<str:code>/', RedirectView.as_view(), name='redirect'),
    path('list/', UserLinkListAPIView.as_view(), name='list_links'),
    path('analytics/<str:code>/', AnalyticsAPIView.as_view(), name='analytics'),
]
