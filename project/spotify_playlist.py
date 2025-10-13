import json

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from project.malapi import MALAPI


def create_spotify_playlist():
    # Load Spotify API credentials
    with open(MALAPI.spotify_keys, "r", encoding="utf-8") as f:
        spotify_keys = json.load(f)

    # Load Spotify URIs from cache
    with open(MALAPI.spotify, "r", encoding="utf-8") as f:
        spotify_uris = json.load(f)

    # Extract just the URIs as a list
    track_uris = list(spotify_uris.values())

    # Set up Spotify authentication
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=spotify_keys["Client ID"],
            client_secret=spotify_keys["Client secret"],
            redirect_uri="http://127.0.0.1:8888/callback",  # Spotify default redirect URI
            scope="playlist-modify-public playlist-modify-private",
        )
    )

    # Get current user's ID
    user_id = sp.current_user()["id"]

    # Create a new playlist
    playlist_name = "MyAnimePlaylist"
    playlist_description = "Playlist created from MAL anime tracks"

    playlist = sp.user_playlist_create(
        user=user_id,
        name=playlist_name,
        public=True,
        description=playlist_description,
    )

    # Add tracks to the playlist in batches (Spotify API limit is 100 tracks per request)
    batch_size = 100
    for i in range(0, len(track_uris), batch_size):
        batch = track_uris[i : i + batch_size]
        sp.playlist_add_items(playlist_id=playlist["id"], items=batch)

    print(f"Successfully created playlist: {playlist_name}")
    print(f"Playlist ID: {playlist['id']}")
    print(f"Playlist URL: {playlist['external_urls']['spotify']}")
    print(f"Added {len(track_uris)} tracks to the playlist")

    return playlist


if __name__ == "__main__":
    create_spotify_playlist()
