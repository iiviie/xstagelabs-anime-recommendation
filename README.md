# Anime Recommendation System

A REST API service for an Anime Recommendation System that uses the AniList GraphQL API as its data source. Built with Django REST Framework, this system provides personalized anime recommendations based on user preferences and viewing history.

## Key Features

### 🚀 Core Features
- **Personalized Recommendations**: AI-driven anime suggestions based on user preferences and watch history
- **Advanced Search**: Search anime by title, genre, or multiple criteria
- **User Preference Management**: Track favorite genres and watched anime
- **Rating System**: Rate and review watched anime
- **Bulk Operations**: Support for bulk creation of anime preferences
- **Swagger Documentation**: Interactive API documentation at `http://13.202.72.59:8000/`
- **Docker Support**: Easy deployment with Docker and Docker Compose

### ⚡ Performance Optimizations
- **Two-Layer Caching System**:
  1. **API Response Cache**:
     - Caches AniList API responses for 1 hour
     - Reduces external API calls
     - Improves response times
     - Handles rate limiting efficiently
  
  2. **User Recommendations Cache**:
     - 24-hour cache for processed recommendations
     - Smart cache invalidation based on user activity
     - Database-level caching with indexes
     - Optimized for quick retrieval

### 🔒 Security Features
- **Strong Password Policy**:
  - Minimum 8 characters
  - Uppercase and lowercase letters
  - Numbers and special characters
  - Secure password validation
- **JWT Authentication**: Secure token-based auth system
- **Environment Variables**: Secure configuration management

### 📈 Technical Highlights
- **Modern Tech Stack**:
  - Django REST Framework
  - PostgreSQL Database
  - Docker & Docker Compose
  - Swagger/OpenAPI Documentation
- **Database Optimizations**:
  - Efficient data models with proper indexing
  - PostgreSQL array fields for better performance
  - Optimized query patterns
- **Scalability**:
  - Stateless architecture
  - Horizontal scaling support
  - Async operations with Gunicorn
  - Database connection pooling

## Production Deployment

The application is currently deployed on AWS EC2. You can access the production environment at the following endpoints:

### Production Endpoints
- **Frontend Application**: http://13.202.72.59:3000/login
- **Backend API & Swagger Documentation**: http://13.202.72.59:8000/

### Development Endpoints (Local)
- Frontend: http://localhost:3000
- Backend: http://localhost:8000

## Setup Instructions

### Using Docker (Recommended)

1. Make sure you have Docker and Docker Compose installed on your system.

2. Clone the repository:
```bash
git clone <repository-url>
cd xstagelabs-assignment
```

3. Build and start the containers:
```bash
docker-compose up --build
```

The application will be available at http://localhost:8000

### Docker Commands

- Stop containers:
```bash
docker-compose down
```

- View logs:
```bash
docker-compose logs -f
```

- Run migrations:
```bash
docker-compose exec web python manage.py migrate
```

- Create a superuser:
```bash
docker-compose exec web python manage.py createsuperuser
```

### Manual Setup (Alternative)

If you prefer not to use Docker, you can set up the project manually:

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up PostgreSQL database:
```bash
createdb anime_db
```

4. Apply migrations:
```bash
python manage.py migrate
```

5. Run the development server:
```bash
python manage.py runserver
```

## API Endpoints

### Authentication
- `POST /auth/register/` - Register a new user
  - Request body: `{ "username": "string", "email": "string", "password": "string" }`
  - Response: `{ "username": "string", "email": "string", "token": "string" }`

- `POST /auth/login/` - Login user
  - Request body: `{ "username": "string", "password": "string" }`
  - Response: `{ "token": "string" }`

### User Preferences
- `GET /user/preferences/` - Get user preferences
  - Response: `{ "favorite_genres": ["string"], "watched_anime": [number] }`

- `PUT /user/preferences/` - Update user preferences
  - Request body: `{ "favorite_genres": ["string"], "watched_anime": [number] }`

### Anime
- `GET /anime/search/` - Search anime by title or genre
  - Parameters:
    - `q` (optional): Search query
    - `genre` (optional): Genre filter
    - `page` (optional): Page number
  - Example Response:
```json
{
    "page_info": {
        "total": 5000,
        "currentPage": 1,
        "lastPage": 500,
        "hasNextPage": true,
        "perPage": 10
    },
    "results": [
        {
            "id": 21,
            "anime_id": 20,
            "title_romaji": "NARUTO",
            "title_english": "Naruto",
            "title_native": "NARUTO -ナルト-",
            "description": "Naruto Uzumaki, a hyperactive and knuckle-headed ninja, lives in Konohagakure, the Hidden Leaf village...",
            "genres": [
                "Action",
                "Adventure",
                "Comedy",
                "Drama",
                "Fantasy",
                "Supernatural"
            ],
            "average_score": 79.0,
            "popularity": 604380,
            "episodes": 220,
            "status": "FINISHED",
            "cover_image": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/medium/bx20-dE6UHbFFg1A5.jpg"
        }
    ]
}
```

- `GET /anime/recommendations/` - Get personalized anime recommendations
  - Example Response:
```json
[
    {
        "id": 1,
        "anime_id": 114129,
        "title_romaji": "Gintama: THE FINAL",
        "title_english": "Gintama: THE VERY FINAL",
        "title_native": "銀魂 THE FINAL",
        "description": "Gintama: THE FINAL is the 3rd and final film adaptation...",
        "genres": [
            "Action",
            "Comedy",
            "Drama",
            "Sci-Fi"
        ],
        "average_score": 91.0,
        "popularity": 45472,
        "episodes": 1,
        "status": "FINISHED",
        "cover_image": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/medium/bx114129-RLgSuh6YbeYx.jpg"
    }
]
```

### Anime Preferences
- `POST /preferences/` - Add anime preference
  - Request body: `{ "anime_id": number, "rating": number }`

- `POST /preferences/bulk_create/` - Add multiple anime preferences
  - Request body: `[{ "anime_id": number, "rating": number }]`

- `GET /preferences/` - List user's anime preferences

### Authentication
All endpoints except registration and login require JWT authentication. Include the JWT token in the Authorization header:
```
Authorization: Bearer <your_token>
```

## Development

The project uses:
- Django REST framework for the API
- PostgreSQL for the database
- JWT for authentication
- AniList GraphQL API for anime data
- Docker and Docker Compose for containerization

## Docker Commands

### Build and start containers
```bash
docker-compose up --build
```

### Stop containers
```bash
docker-compose down
```

### View logs
```bash
docker-compose logs -f
```

### Run migrations
```bash
docker-compose exec web python manage.py migrate
```

### Create a superuser
```bash
docker-compose exec web python manage.py createsuperuser
```

