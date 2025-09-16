from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),  # ✅ Primero accounts
    path("", include("fake_store_api.urls")),     # ✅ Después fake_store_api
]