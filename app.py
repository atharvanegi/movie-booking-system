import pickle
import streamlit as st
import requests
import os
import time

try:
    import pandas as pd
except ModuleNotFoundError as e:
    st.error(f"Pandas module not found: {e}")
    raise

st.set_page_config(page_title="Movie Recommender System", layout="wide")

# Title and subtitle
st.markdown("""
    <style>
    .header {
        font-size: 2.5em;
        font-weight: bold;
        color: #ffffff;
        text-align: center;
        margin: 0.5em;
        font-family: 'Arial', sans-serif;
    }
    .subheader {
        font-size: 1.5em;
        color: #dcdcdc;
        text-align: center;
        margin-bottom: 1em;
        font-family: 'Arial', sans-serif;
    }
    .recommendation-title {
        font-size: 1.8em;
        font-weight: bold;
        color: #ffffff;
        margin-top: 1em;
        font-family: 'Arial', sans-serif;
    }
    .movie-card {
        background-color: #444444;
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        color: #f0f2f6;
        transition: transform 0.3s, box-shadow 0.3s;
    }
    .movie-card:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    }
    .movie-title {
        font-size: 1.2em;
        margin-top: 0.5em;
        font-family: 'Arial', sans-serif;
    }
    .movie-info {
        font-size: 0.9em;
        color: #dcdcdc;
        margin-top: 0.5em;
        font-family: 'Arial', sans-serif;
    }
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #333333;
        color: #f0f2f6;
        text-align: center;
        padding: 10px;
        font-size: 0.9em;
        border-top: 1px solid #eaeaea;
        font-family: 'Arial', sans-serif;
    }
    .spinner {
        margin: 50px auto;
        border: 12px solid #f3f3f3; /* Light grey */
        border-top: 12px solid #3498db; /* Blue */
        border-radius: 50%;
        width: 60px;
        height: 60px;
        animation: spin 1.5s linear infinite;
    }
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="header">Welcome to the Movie Recommender System</div>', unsafe_allow_html=True)
st.markdown('<div class="subheader">Find your next favorite movie!</div>', unsafe_allow_html=True)

# Define paths and API key
movie_list_path = 'C:\\Users\\ss\\Desktop\\Movie-recommendation-system-main\\movie_list.pkl'
similarity_path = 'C:\\Users\\ss\\Desktop\\Movie-recommendation-system-main\\similarity.pkl'
omdb_api_key = '703e5401'  # Replace with your OMDb API key

# Check if files exist
if not os.path.exists(movie_list_path):
    st.error(f"File not found: {movie_list_path}")
    raise FileNotFoundError(f"File not found: {movie_list_path}")

if not os.path.exists(similarity_path):
    st.error(f"File not found: {similarity_path}")
    raise FileNotFoundError(f"File not found: {similarity_path}")

def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=60ed64fabaad011874b007e3ebc92ae4&language=en-US"
    data = requests.get(url).json()
    poster_path = data.get('poster_path', '')
    full_path = f"https://image.tmdb.org/t/p/w500/{poster_path}" if poster_path else None
    return full_path

def fetch_movie_details(movie_id, movie_title):
    tmdb_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=60ed64fabaad011874b007e3ebc92ae4&language=en-US"
    tmdb_data = requests.get(tmdb_url).json()
    title = tmdb_data.get('title', 'Unknown Title')
    genres = ', '.join(genre['name'] for genre in tmdb_data.get('genres', []))
    overview = tmdb_data.get('overview', 'No description available.')
    cast_url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key=60ed64fabaad011874b007e3ebc92ae4"
    cast_data = requests.get(cast_url).json()
    actors = ', '.join(actor['name'] for actor in cast_data.get('cast', [])[:5])  # Top 5 actors

    # Fetch IMDb rating
    omdb_url = f"http://www.omdbapi.com/?t={movie_title}&apikey={omdb_api_key}"
    omdb_data = requests.get(omdb_url).json()
    imdb_rating = omdb_data.get('imdbRating', 'N/A')

    return title, genres, actors, overview, imdb_rating

def get_google_search_link(movie_title):
    query = movie_title.replace(' ', '+')
    return f"https://www.google.com/search?q={query}"

def recommend(movie):
    time.sleep(2)  # Simulated delay
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    google_search_links = []
    movie_details = []
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        movie_name = movies.iloc[i[0]].title
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movie_name)
        google_search_links.append(get_google_search_link(movie_name))
        movie_details.append(fetch_movie_details(movie_id, movie_name))

    return recommended_movie_names, recommended_movie_posters, google_search_links, movie_details

movies = pd.read_pickle(movie_list_path)
similarity = pd.read_pickle(similarity_path)

movie_list = movies['title'].values
selected_movie = st.selectbox(
    "Select a movie you’ve enjoyed and would like to find similar recommendations for!",
    movie_list
)

if st.button('Show Recommendation'):
    with st.spinner('Fetching recommendations...'):
        recommended_movie_names, recommended_movie_posters, google_search_links, movie_details = recommend(
            selected_movie)

    st.markdown('<div class="recommendation-title">Here are some movies you might like:</div>', unsafe_allow_html=True)
    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            # Movie Card with hover effect
            st.markdown(f"""
                <div class='movie-card'>
                    <a href='{google_search_links[i]}' target='_blank'>
                        <img src='{recommended_movie_posters[i]}' style='width: 100%; border-radius: 8px;' />
                    </a>
                    <div class='movie-title'>
                        <a href='{google_search_links[i]}' target='_blank' style='text-decoration: none; color: #f0f2f6;'>{recommended_movie_names[i]}</a>
                    </div>
                    <div class='movie-info'><strong>Genres:</strong> {movie_details[i][1]}</div>
                    <div class='movie-info'><strong>Main Actors:</strong> {movie_details[i][2]}</div>
                    <div class='movie-info'><strong>Overview:</strong> {movie_details[i][3]}</div>
                    <div class='movie-info'><strong>IMDb Rating:</strong> {movie_details[i][4]}</div>
                </div>
            """, unsafe_allow_html=True)

# Add footer
st.markdown("""
    <div class="footer">
        Developed by Atharva Negi - Powered by Streamlit
    </div>
    """, unsafe_allow_html=True)
