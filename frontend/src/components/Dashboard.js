import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import axios from '../config/axios';
import {
  Container,
  Grid,
  Card,
  CardContent,
  CardMedia,
  Typography,
  TextField,
  Button,
  Box,
  Chip,
  Rating,
  Paper,
  Autocomplete,
  Divider,
  Alert,
  ToggleButton,
  ToggleButtonGroup,
} from '@mui/material';

function Dashboard() {
  const [recommendations, setRecommendations] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [userPreferences, setUserPreferences] = useState({ favorite_genres: [], watched_anime: [] });
  const [availableGenres, setAvailableGenres] = useState([]);
  const [selectedGenres, setSelectedGenres] = useState([]);
  const [successMessage, setSuccessMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const { user } = useAuth();
  const navigate = useNavigate();
  const [preferencesMode, setPreferencesMode] = useState('ui'); // 'ui' or 'raw'
  const [rawPreferences, setRawPreferences] = useState('{\n  "favorite_genres": [],\n  "watched_anime": []\n}');

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }
    fetchUserPreferences();
    fetchAvailableGenres();
    fetchRecommendations();
  }, [user, navigate]);

  const fetchUserPreferences = async () => {
    try {
      const response = await axios.get('/user/preferences/', {
        headers: { Authorization: `Bearer ${user.token}` }
      });
      setUserPreferences(response.data);
      setSelectedGenres(response.data.favorite_genres);
    } catch (error) {
      console.error('Error fetching user preferences:', error);
    }
  };

  const fetchAvailableGenres = async () => {
    try {
      const response = await axios.get('/anime/genres/', {
        headers: { Authorization: `Bearer ${user.token}` }
      });
      setAvailableGenres(response.data.map(genre => genre.name));
    } catch (error) {
      console.error('Error fetching genres:', error);
    }
  };

  const fetchRecommendations = async () => {
    try {
      const response = await axios.get('/anime/recommendations/', {
        headers: { Authorization: `Bearer ${user.token}` }
      });
      setRecommendations(response.data);
    } catch (error) {
      console.error('Error fetching recommendations:', error);
    }
  };

  const handleSearch = async () => {
    try {
      const response = await axios.get(`/anime/search/?q=${searchQuery}`, {
        headers: { Authorization: `Bearer ${user.token}` }
      });
      setSearchResults(response.data.results || []);
    } catch (error) {
      console.error('Error searching anime:', error);
    }
  };

  const handleUpdatePreferences = async () => {
    try {
      let preferencesData;
      if (preferencesMode === 'ui') {
        preferencesData = {
          favorite_genres: selectedGenres,
          watched_anime: userPreferences.watched_anime
        };
      } else {
        try {
          preferencesData = JSON.parse(rawPreferences);
        } catch (e) {
          setErrorMessage('Invalid JSON format');
          return;
        }
      }

      await axios.put('/user/preferences/', preferencesData, {
        headers: { Authorization: `Bearer ${user.token}` }
      });
      setSuccessMessage('Preferences updated successfully!');
      setTimeout(() => setSuccessMessage(''), 3000);
      fetchRecommendations();
      fetchUserPreferences(); // Refresh the UI after update
    } catch (error) {
      setErrorMessage(error.response?.data?.error || 'Failed to update preferences');
      setTimeout(() => setErrorMessage(''), 3000);
    }
  };

  const handleRating = async (animeId, rating) => {
    try {
      await axios.post('/preferences/', {
        anime_id: animeId,
        rating: rating
      }, {
        headers: { Authorization: `Bearer ${user.token}` }
      });
      // Update watched anime list
      setUserPreferences(prev => ({
        ...prev,
        watched_anime: [...prev.watched_anime, animeId]
      }));
      fetchRecommendations();
      setSuccessMessage('Rating added successfully!');
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (error) {
      setErrorMessage('Failed to add rating');
      setTimeout(() => setErrorMessage(''), 3000);
    }
  };

  const AnimeCard = ({ anime }) => (
    <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <CardMedia
        component="img"
        height="200"
        image={anime.cover_image || 'https://via.placeholder.com/200x300'}
        alt={anime.title_english || anime.title_romaji}
      />
      <CardContent sx={{ flexGrow: 1 }}>
        <Typography gutterBottom variant="h6" component="div">
          {anime.title_english || anime.title_romaji}
        </Typography>
        <Box sx={{ mb: 1 }}>
          {anime.genres.map((genre, index) => (
            <Chip
              key={index}
              label={genre}
              size="small"
              sx={{ mr: 0.5, mb: 0.5 }}
            />
          ))}
        </Box>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          {anime.description?.slice(0, 150)}...
        </Typography>
        <Rating
          value={0}
          onChange={(event, newValue) => handleRating(anime.anime_id, newValue)}
        />
      </CardContent>
    </Card>
  );

  return (
    <Container sx={{ mt: 4, mb: 4 }}>
      {(successMessage || errorMessage) && (
        <Alert 
          severity={successMessage ? "success" : "error"} 
          sx={{ mb: 2 }}
        >
          {successMessage || errorMessage}
        </Alert>
      )}

      {/* User Preferences Section */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h5">
            Your Preferences
          </Typography>
          <ToggleButtonGroup
            value={preferencesMode}
            exclusive
            onChange={(e, newMode) => newMode && setPreferencesMode(newMode)}
            size="small"
          >
            <ToggleButton value="ui">UI Mode</ToggleButton>
            <ToggleButton value="raw">Raw JSON</ToggleButton>
          </ToggleButtonGroup>
        </Box>

        {preferencesMode === 'ui' ? (
          <Box sx={{ mb: 3 }}>
            <Autocomplete
              multiple
              value={selectedGenres}
              onChange={(event, newValue) => setSelectedGenres(newValue)}
              options={availableGenres}
              renderInput={(params) => (
                <TextField
                  {...params}
                  variant="outlined"
                  label="Favorite Genres"
                  placeholder="Select genres"
                />
              )}
              sx={{ mb: 2 }}
            />
            <Typography variant="subtitle1" gutterBottom>
              Watched Anime: {userPreferences.watched_anime.length}
            </Typography>
          </Box>
        ) : (
          <Box sx={{ mb: 3 }}>
            <TextField
              fullWidth
              multiline
              rows={8}
              value={rawPreferences}
              onChange={(e) => setRawPreferences(e.target.value)}
              variant="outlined"
              label="Raw JSON Preferences"
              sx={{ mb: 2, fontFamily: 'monospace' }}
              helperText="Enter preferences in JSON format"
            />
            <Typography variant="caption" display="block" gutterBottom sx={{ mb: 2 }}>
              Example format:
              <pre style={{ 
                background: '#2b2b2b', 
                padding: '8px', 
                borderRadius: '4px',
                color: '#e0e0e0',
                border: '1px solid #404040'
              }}>
{`{
  "favorite_genres": ["Action", "Comedy"],
  "watched_anime": []
}`}
              </pre>
            </Typography>
          </Box>
        )}

        <Button
          variant="contained"
          onClick={handleUpdatePreferences}
          sx={{ mt: 1 }}
        >
          Update Preferences
        </Button>
      </Paper>

      {/* Search Section */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h5" gutterBottom>
          Search Anime
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <TextField
            fullWidth
            label="Search Anime"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <Button
            variant="contained"
            onClick={handleSearch}
            sx={{ minWidth: '120px' }}
          >
            Search
          </Button>
        </Box>

        {searchResults.length > 0 && (
          <Box sx={{ mt: 3 }}>
            <Typography variant="h6" gutterBottom>
              Search Results
            </Typography>
            <Grid container spacing={3}>
              {searchResults.map((anime) => (
                <Grid item key={anime.id} xs={12} sm={6} md={4}>
                  <AnimeCard anime={anime} />
                </Grid>
              ))}
            </Grid>
          </Box>
        )}
      </Paper>

      {/* Recommendations Section */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          Recommended for You
        </Typography>
        <Button
          variant="outlined"
          onClick={fetchRecommendations}
          sx={{ mb: 3 }}
        >
          Refresh Recommendations
        </Button>
        <Grid container spacing={3}>
          {recommendations.map((anime) => (
            <Grid item key={anime.id} xs={12} sm={6} md={4}>
              <AnimeCard anime={anime} />
            </Grid>
          ))}
        </Grid>
      </Paper>
    </Container>
  );
}

export default Dashboard; 