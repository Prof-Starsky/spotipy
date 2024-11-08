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

try:
    with open('song_rankings.json', 'r') as f:
        song_rankings = json.load(f)
except FileNotFoundError:
    song_rankings = {}

# Function to get user playlists
def get_user_playlists():
    playlists = sp.current_user_playlists()
    return playlists['items']

# Function to get songs from multiple playlists
def get_playlist_tracks(playlist_ids):
    tracks = []
    for playlist_id in playlist_ids:
        results = sp.playlist_tracks(playlist_id)
        tracks.extend(results['items'])
        while results['next']:
            results = sp.next(results)
            tracks.extend(results['items'])
    return tracks

# Function to choose between songs from multiple playlists
def choose_songs():
    # Select multiple playlists
    playlists = get_user_playlists()
    print("Select playlists to compare songs from (comma-separated):")
    for i, playlist in enumerate(playlists):
        print(f"{i + 1}: {playlist['name']}")
    playlist_indices = input("Enter the playlist numbers (e.g., 1,3,5): ")
    playlist_indices = [int(i.strip()) - 1 for i in playlist_indices.split(',')]
    selected_playlist_ids = [playlists[i]['id'] for i in playlist_indices]
    
    # Retrieve and format songs from the selected playlists
    tracks = get_playlist_tracks(selected_playlist_ids)
    song_ids = [track['track']['id'] for track in tracks if track['track'] is not None]
    song_info = {track['track']['id']: {
                    "name": track['track']['name'],
                    "artist": track['track']['artists'][0]['name']}
                 for track in tracks if track['track'] is not None}

    # Main loop to choose between songs
    while True:
        # Select two unique random songs
        song1_id, song2_id = random.sample(song_ids, 2)
        song1 = song_info[song1_id]
        song2 = song_info[song2_id]

        # Display the two song choices
        print(f"\nWhich song do you prefer?")
        print(f"1: {song1['name']} by {song1['artist']}")
        print(f"2: {song2['name']} by {song2['artist']}")
        choice = input("Enter 1, 2, or 3 for a tie (or 'q' to quit): ")

        if choice.lower() == 'q':
            print("Exiting song comparison.")
            break

        # Initialize ranking records if not already present
        if song1_id not in song_rankings:
            song_rankings[song1_id] = {"wins": 0, "losses": 0, "draws": 0, "points": 0, "name": song1['name'], "artist": song1['artist']}
        if song2_id not in song_rankings:
            song_rankings[song2_id] = {"wins": 0, "losses": 0, "draws": 0, "points": 0, "name": song2['name'], "artist": song2['artist']}

        # Update rankings based on choice
        if choice == '1':  # Song 1 wins
            song_rankings[song1_id]["wins"] += 1
            song_rankings[song1_id]["points"] += 2
            song_rankings[song2_id]["losses"] += 1
        elif choice == '2':  # Song 2 wins
            song_rankings[song2_id]["wins"] += 1
            song_rankings[song2_id]["points"] += 2
            song_rankings[song1_id]["losses"] += 1
        elif choice == '3':  # Tie
            song_rankings[song1_id]["draws"] += 1
            song_rankings[song1_id]["points"] += 1
            song_rankings[song2_id]["draws"] += 1
            song_rankings[song2_id]["points"] += 1
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 'q'.")
            continue

        # Save rankings to a file
        with open('song_rankings.json', 'w') as f:
            json.dump(song_rankings, f, indent=4)

# Function to rank songs based on point percentage across multiple playlists
def display_rankings():
    # Calculate point percentage as points / (2 * total_matches)
    sorted_rankings = sorted(
        song_rankings.items(),
        key=lambda x: (
            (x[1]["points"] / (2 * (x[1]["wins"] + x[1]["losses"] + x[1]["draws"]))) if (x[1]["wins"] + x[1]["losses"] + x[1]["draws"]) > 0 else 0,
            x[1]["wins"],          # Most wins
            x[1]["draws"],         # Most draws
            -x[1]["losses"]        # Least losses
        ),
        reverse=True
    )

    print("\nSong Rankings (by point percentage):")
    for rank, (song_id, data) in enumerate(sorted_rankings, start=1):
        total_matches = data["wins"] + data["losses"] + data["draws"]
        max_points = 2 * total_matches  # For point percentage calculation
        point_percentage = (data["points"] / max_points) if total_matches > 0 else 0
        print(f"{rank}. {data['name']} by {data['artist']} - W: {data['wins']} | L: {data['losses']} | D: {data['draws']} | Score: {data['points']} | Point %: {point_percentage:.4f}")

# Run the program
choose_songs()
display_rankings()
