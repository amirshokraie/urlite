from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    # Accounts (JWT & user endpoints)
    path('api/accounts/', include('accounts.urls')),
    path('api/links/', include('links.urls'))
]
