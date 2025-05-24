from django.urls import path
from .views import (
    UserRegistrationView,
    UserLoginView,
    UserPreferencesView
)

urlpatterns = [
    path('auth/register/', UserRegistrationView.as_view(), name='user-registration'),
    path('auth/login/', UserLoginView.as_view(), name='user-login'),
    path('user/preferences/', UserPreferencesView.as_view(), name='user-preferences'),
] 