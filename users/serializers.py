from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, AnimePreference
from .validators import validate_password_strength

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password_strength]
    )

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        UserProfile.objects.create(user=user)
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = UserProfile
        fields = ('id', 'username', 'email', 'favorite_genres', 'watched_anime')

class AnimePreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnimePreference
        fields = ('id', 'anime_id', 'rating', 'created_at') 