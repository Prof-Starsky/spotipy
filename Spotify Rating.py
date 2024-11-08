import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json
import random

# Spotify API credentials (replace with your client ID and client secret)
SPOTIPY_CLIENT_ID = 'Fill this in'
SPOTIPY_CLIENT_SECRET = 'Fill this in'
SPOTIPY_REDIRECT_URI = 'https://developer.spotify.com/'

# Initialize Spotify API connection with spotipy
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope="playlist-read-private playlist-read-collaborative"
))

# Load or create the ratings file
try:
    with open('song_ratings.json', 'r') as f:
        song_ratings = json.load(f)
except FileNotFoundError:
    song_ratings = {}

# Function to get playlists
def get_user_playlists():
    playlists = sp.current_user_playlists()
    return playlists['items']

# Function to get songs from a playlist
def get_playlist_tracks(playlist_id):
    tracks = []
    results = sp.playlist_tracks(playlist_id)
    tracks.extend(results['items'])
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks

# Function to rate songs and save ratings
def rate_songs():
    playlists = get_user_playlists()
    print("Select a playlist to rate songs:")
    for i, playlist in enumerate(playlists):
        print(f"{i + 1}: {playlist['name']}")
    playlist_index = int(input("Enter the playlist number: ")) - 1
    selected_playlist = playlists[playlist_index]

    # Retrieve songs from the selected playlist
    tracks = get_playlist_tracks(selected_playlist['id'])

    # Shuffle tracks for a random order
    random.shuffle(tracks)

    for track in tracks:
        song_id = track['track']['id']

        if song_id in song_ratings:
            continue

        song_name = track['track']['name']
        artist_name = track['track']['artists'][0]['name']
        
        # Display song info and get rating
        print(f"\nSong: {song_name} by {artist_name}")
        rating = input("Rate this song out of 10 (or leave blank to skip): ")

        if rating == "999":
            print("Rating session ended.")
            break
        

        # Save rating if provided
        if rating:
            song_ratings[song_id] = {
                "name": song_name,
                "artist": artist_name,
                "rating": rating
            }

            # Save ratings to a file
            with open('song_ratings.json', 'w') as f:
                json.dump(song_ratings, f, indent=4)

# Run the rating function
rate_songs()
