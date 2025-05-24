from rest_framework import serializers
from .models import CachedAnime, Genre

class CachedAnimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CachedAnime
        fields = (
            'id', 'anime_id', 'title_romaji', 'title_english', 'title_native',
            'description', 'genres', 'average_score', 'popularity', 'episodes',
            'status', 'cover_image'
        )

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('id', 'name', 'description') 