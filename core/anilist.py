import requests
import requests_cache
from django.conf import settings
from typing import Dict, List, Optional, Union
import logging
from datetime import timedelta

logger = logging.getLogger(__name__)

# Install cache with a 1-hour expiration
requests_cache.install_cache(
    'anilist_cache',
    backend='sqlite',
    expire_after=timedelta(hours=1)
)

class AniListAPI:
    API_URL = 'https://graphql.anilist.co'

    @staticmethod
    def execute_query(query: str, variables: Dict = None) -> Dict:
        """Execute a GraphQL query against the AniList API."""
        try:
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            }
            response = requests.post(
                AniListAPI.API_URL,
                json={'query': query, 'variables': variables or {}},
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"AniList API request failed: {str(e)}")
            raise

    @classmethod
    def search_anime(cls, search: str = None, genre: str = None, page: int = 1, per_page: int = 10) -> Dict:
        """Search for anime by title or genre."""
        query = """
        query ($search: String, $genre: String, $page: Int, $perPage: Int) {
            Page(page: $page, perPage: $perPage) {
                pageInfo {
                    total
                    currentPage
                    lastPage
                    hasNextPage
                    perPage
                }
                media(type: ANIME, search: $search, genre: $genre, sort: POPULARITY_DESC) {
                    id
                    title {
                        romaji
                        english
                        native
                    }
                    description(asHtml: false)
                    genres
                    averageScore
                    popularity
                    episodes
                    status
                    coverImage {
                        large
                    }
                    startDate {
                        year
                        month
                        day
                    }
                    endDate {
                        year
                        month
                        day
                    }
                }
            }
        }
        """
        
        # Clean up search parameters
        variables = {
            'page': page,
            'perPage': per_page
        }
        
        if search and search.strip():
            variables['search'] = search.strip()
            
        if genre and genre.strip():
            variables['genre'] = genre.strip()
            
        logger.info(f"Executing AniList search query with variables: {variables}")
        
        try:
            result = cls.execute_query(query, variables)
            logger.info(f"AniList search response: {result}")
            return result
        except Exception as e:
            logger.error(f"Error executing AniList search query: {str(e)}", exc_info=True)
            raise

    @classmethod
    def get_anime_details(cls, anime_id: int) -> Dict:
        """Get detailed information about a specific anime."""
        query = """
        query ($id: Int!) {
            Media(id: $id, type: ANIME) {
                id
                title {
                    romaji
                    english
                    native
                }
                description
                genres
                averageScore
                popularity
                episodes
                status
                coverImage {
                    large
                }
                startDate {
                    year
                    month
                    day
                }
                endDate {
                    year
                    month
                    day
                }
            }
        }
        """
        variables = {'id': anime_id}
        return cls.execute_query(query, variables)

    @classmethod
    def get_genre_list(cls) -> List[str]:
        """Get a list of all available genres."""
        query = """
        query {
            GenreCollection
        }
        """
        response = cls.execute_query(query)
        return response.get('data', {}).get('GenreCollection', [])

    @classmethod
    def get_recommendations_by_genres(cls, genres: List[str], page: int = 1, per_page: int = 20) -> Dict:
        """Get anime recommendations based on genres."""
        query = """
        query ($genres: [String], $page: Int, $perPage: Int) {
            Page(page: $page, perPage: $perPage) {
                media(type: ANIME, genre_in: $genres, sort: [SCORE_DESC, POPULARITY_DESC]) {
                    id
                    title {
                        romaji
                        english
                        native
                    }
                    description
                    genres
                    averageScore
                    popularity
                    episodes
                    status
                    coverImage {
                        large
                    }
                }
            }
        }
        """
        variables = {
            'genres': genres,
            'page': page,
            'perPage': per_page
        }
        return cls.execute_query(query, variables) 