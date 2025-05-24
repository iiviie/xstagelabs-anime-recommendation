from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from .models import CachedAnime, Genre, UserRecommendationCache
from .serializers import CachedAnimeSerializer, GenreSerializer
from core.anilist import AniListAPI
from users.models import UserProfile, AnimePreference
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging

logger = logging.getLogger(__name__)

class AnimeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CachedAnimeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CachedAnime.objects.all()

    @action(detail=False, methods=['get'])
    def search(self, request):
        search_query = request.query_params.get('q', '')
        genre = request.query_params.get('genre', '')
        page = int(request.query_params.get('page', 1))
        
        try:
            # Search AniList API
            response = AniListAPI.search_anime(search=search_query, genre=genre, page=page)
            
            # Cache the results
            media_list = response.get('data', {}).get('Page', {}).get('media', [])
            for media in media_list:
                CachedAnime.objects.update_or_create(
                    anime_id=media['id'],
                    defaults={
                        'title_romaji': media['title']['romaji'],
                        'title_english': media['title']['english'],
                        'title_native': media['title']['native'],
                        'description': media['description'],
                        'genres': media['genres'],
                        'average_score': media['averageScore'],
                        'popularity': media['popularity'],
                        'episodes': media['episodes'],
                        'status': media['status'],
                        'cover_image': media['coverImage']['large'] if media['coverImage'] else None
                    }
                )
            
            return Response(response['data'])
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def recommendations(self, request):
        user_profile = UserProfile.objects.get(user=request.user)
        user_preferences = AnimePreference.objects.filter(user=request.user)
        
        # Get user's favorite genres
        favorite_genres = user_profile.favorite_genres
        
        # Get user's watched anime
        watched_anime = user_profile.watched_anime
        
        # Find anime with similar genres that the user hasn't watched
        recommended_anime = CachedAnime.objects.filter(
            genres__overlap=favorite_genres
        ).exclude(
            anime_id__in=watched_anime
        ).order_by('-average_score')[:10]
        
        serializer = self.get_serializer(recommended_anime, many=True)
        return Response(serializer.data)

class GenreViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def refresh(self, request):
        try:
            # Get genres from AniList API
            genres = AniListAPI.get_genre_list()
            
            # Update local genre database
            for genre_name in genres:
                Genre.objects.get_or_create(name=genre_name)
            
            return Response({'status': 'genres refreshed'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class AnimeSearchView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('q', openapi.IN_QUERY, description="Search query", type=openapi.TYPE_STRING),
            openapi.Parameter('genre', openapi.IN_QUERY, description="Genre filter", type=openapi.TYPE_STRING),
            openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER),
        ],
        operation_description="Search anime by name or genre",
        responses={200: CachedAnimeSerializer(many=True)}
    )
    def get(self, request):
        try:
            search_query = request.query_params.get('q', '')
            genre = request.query_params.get('genre', '')
            page = int(request.query_params.get('page', 1))
            
            logger.info(f"Searching for anime with query: {search_query}, genre: {genre}, page: {page}")
            
            # Search AniList API
            response = AniListAPI.search_anime(
                search=search_query, 
                genre=genre, 
                page=page
            )
            
            logger.info(f"AniList API Response: {response}")
            
            if not response.get('data'):
                logger.error(f"No data in response: {response}")
                return Response({'error': 'No results found'}, status=status.HTTP_404_NOT_FOUND)
            
            page_data = response.get('data', {}).get('Page', {})
            media_list = page_data.get('media', [])
            
            if not media_list:
                logger.warning(f"No media found in response for query: {search_query}")
                return Response({
                    'page_info': page_data.get('pageInfo', {}),
                    'results': []
                })
            
            # Cache the results
            cached_anime = []
            
            for media in media_list:
                if not media:
                    continue
                    
                try:
                    anime, created = CachedAnime.objects.update_or_create(
                        anime_id=media['id'],
                        defaults={
                            'title_romaji': media['title']['romaji'],
                            'title_english': media['title'].get('english'),
                            'title_native': media['title'].get('native'),
                            'description': media.get('description'),
                            'genres': media.get('genres', []),
                            'average_score': media.get('averageScore'),
                            'popularity': media.get('popularity', 0),
                            'episodes': media.get('episodes'),
                            'status': media.get('status', 'UNKNOWN'),
                            'cover_image': media.get('coverImage', {}).get('large')
                        }
                    )
                    cached_anime.append(anime)
                except Exception as cache_error:
                    logger.error(f"Error caching anime {media.get('id')}: {str(cache_error)}")
                    continue
            
            serializer = CachedAnimeSerializer(cached_anime, many=True)
            return Response({
                'page_info': page_data.get('pageInfo', {}),
                'results': serializer.data
            })
            
        except Exception as e:
            logger.error(f"Error in anime search: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Failed to fetch anime data. Please try again later.'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class AnimeRecommendationsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    CACHE_DURATION = timedelta(hours=24)  # Cache recommendations for 24 hours

    @swagger_auto_schema(
        operation_description="Get personalized anime recommendations based on user preferences",
        responses={200: CachedAnimeSerializer(many=True)}
    )
    def get(self, request):
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            favorite_genres = user_profile.favorite_genres
            watched_anime = user_profile.watched_anime
            
            if not favorite_genres:
                return Response(
                    {'error': 'Please set your favorite genres to get recommendations'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if we have valid cached recommendations
            cache, created = UserRecommendationCache.objects.get_or_create(
                user=request.user,
                defaults={'favorite_genres': favorite_genres}
            )

            # If cache exists and is still valid (less than 24 hours old and genres haven't changed)
            if not created and cache.updated_at > timezone.now() - self.CACHE_DURATION \
                and set(cache.favorite_genres) == set(favorite_genres):
                # Return cached recommendations, excluding newly watched anime
                recommendations = cache.recommended_anime.exclude(anime_id__in=watched_anime)[:10]
                serializer = CachedAnimeSerializer(recommendations, many=True)
                return Response(serializer.data)
            
            # If cache is invalid or doesn't exist, fetch new recommendations
            response = AniListAPI.get_recommendations_by_genres(
                genres=favorite_genres,
                per_page=20
            )
            
            if not response.get('data'):
                return Response({'error': 'No recommendations found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Cache and filter recommendations
            media_list = response.get('data', {}).get('Page', {}).get('media', [])
            recommended_anime = []
            
            for media in media_list:
                if not media or media['id'] in watched_anime:
                    continue
                    
                anime, created = CachedAnime.objects.update_or_create(
                    anime_id=media['id'],
                    defaults={
                        'title_romaji': media['title']['romaji'],
                        'title_english': media['title'].get('english'),
                        'title_native': media['title'].get('native'),
                        'description': media.get('description'),
                        'genres': media.get('genres', []),
                        'average_score': media.get('averageScore'),
                        'popularity': media.get('popularity', 0),
                        'episodes': media.get('episodes'),
                        'status': media.get('status', 'UNKNOWN'),
                        'cover_image': media.get('coverImage', {}).get('large')
                    }
                )
                recommended_anime.append(anime)
            
            # Update cache
            cache.recommended_anime.set(recommended_anime)
            cache.favorite_genres = favorite_genres
            cache.save()
            
            # Limit to top 10 recommendations
            recommended_anime = recommended_anime[:10]
            serializer = CachedAnimeSerializer(recommended_anime, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error in anime recommendations: {str(e)}")
            return Response(
                {'error': 'Failed to fetch recommendations. Please try again later.'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
