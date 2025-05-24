"""
URL configuration for xstagelabs project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import TokenRefreshView
from users.views import UserRegistrationView, UserLoginView, UserPreferencesView
from anime.views import AnimeSearchView, AnimeRecommendationsView

# Schema view for Swagger documentation
schema_view = get_schema_view(
    openapi.Info(
        title="Anime Recommendation System API",
        default_version='v1',
        description="A REST API service for an Anime Recommendation System using AniList GraphQL API",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('anime.urls')),  # Prefix all API routes with /api/
    path('api/', include('users.urls')),  # Prefix all API routes with /api/
    # Documentation
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # Authentication endpoints
    path('auth/register/', UserRegistrationView.as_view(), name='register'),
    path('auth/login/', UserLoginView.as_view(), name='login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Anime endpoints
    path('anime/search/', AnimeSearchView.as_view(), name='anime-search'),
    path('anime/recommendations/', AnimeRecommendationsView.as_view(), name='anime-recommendations'),
    
    # User preferences endpoint
    path('user/preferences/', UserPreferencesView.as_view(), name='user-preferences'),
    # Serve frontend for all other routes
    re_path(r'^.*', TemplateView.as_view(template_name='frontend/index.html')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
