from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import User

class CachedAnime(models.Model):
    anime_id = models.IntegerField(unique=True)
    title_romaji = models.CharField(max_length=255)
    title_english = models.CharField(max_length=255, null=True, blank=True)
    title_native = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    genres = ArrayField(models.CharField(max_length=50), blank=True, default=list)
    average_score = models.FloatField(null=True, blank=True)
    popularity = models.IntegerField(default=0)
    episodes = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=50)
    cover_image = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title_english or self.title_romaji

class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class UserRecommendationCache(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    recommended_anime = models.ManyToManyField(CachedAnime)
    favorite_genres = ArrayField(models.CharField(max_length=50), blank=True, default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Recommendations for {self.user.username}"

    class Meta:
        indexes = [
            models.Index(fields=['updated_at']),
        ]
