from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("", include("api.urls")),
    path("admin/", admin.site.urls),
    path("login", TokenObtainPairView.as_view()),
    path("login/refresh", TokenRefreshView.as_view()),
]
