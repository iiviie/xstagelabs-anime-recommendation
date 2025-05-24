from django.urls import path
from .views import AnimeSearchView, AnimeRecommendationsView

urlpatterns = [
    path('anime/search/', AnimeSearchView.as_view(), name='anime-search'),
    path('anime/recommendations/', AnimeRecommendationsView.as_view(), name='anime-recommendations'),
] 