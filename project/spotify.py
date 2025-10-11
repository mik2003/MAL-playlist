import json
import os
from typing import Any, Dict, List

import spotipy
from spotipy.oauth2 import SpotifyOAuth


class SpotifySearcher:
    def __init__(self, client_id: str, client_secret: str):
        self.sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri="http://127.0.0.1:8888/callback",
                scope="user-library-read playlist-modify-public",
            )
        )
        self.cache_file = "spotify_uri_cache.json"
        self.uri_cache = self._load_cache()

    def _load_cache(self) -> Dict[str, str]:
        """Load existing URI cache"""
        if os.path.exists(self.cache_file):
            with open(self.cache_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save_cache(self):
        """Save URI cache to file"""
        with open(self.cache_file, "w", encoding="utf-8") as f:
            json.dump(self.uri_cache, f, indent=2, ensure_ascii=False)

    def search_spotify_track(
        self, song_name: str, artist: str, anime_title: str, song_id: str
    ) -> str:
        """
        Search Spotify for a track and return its URI

        Returns:
            Spotify URI if found, empty string if not found
        """
        # Check cache first
        if song_id in self.uri_cache:
            return self.uri_cache[song_id]

        # Clean up the search query
        def clean_query(text):
            if not text:
                return ""
            # Remove common problematic characters for Spotify search
            return (
                text.replace('"', "")
                .replace("\\", "")
                .replace("(", "")
                .replace(")", "")
                .strip()
            )

        # Try different search strategies
        search_queries = [
            f"{clean_query(song_name)} {clean_query(artist)}",
            f"{clean_query(song_name)}",
            f"{clean_query(song_name)} {clean_query(anime_title)}",
            f"{clean_query(song_name)} by {clean_query(artist)}",
            f"{clean_query(anime_title)} {clean_query(song_name)}",
        ]

        # Remove empty queries and duplicates
        search_queries = [q for q in search_queries if q.strip()]
        search_queries = list(dict.fromkeys(search_queries))

        for query in search_queries:
            try:
                print(f"  Searching: '{query}'")
                results = self.sp.search(q=query, type="track", limit=5)

                if results["tracks"]["items"]:
                    # Get the best match
                    track = results["tracks"]["items"][0]
                    spotify_uri = track["uri"]

                    # Cache the result
                    self.uri_cache[song_id] = spotify_uri
                    self._save_cache()

                    print(
                        f"  ✅ Found: {track['name']} - {track['artists'][0]['name']}"
                    )
                    return spotify_uri

            except Exception as e:
                print(f"  ❌ Search error for '{query}': {e}")
                continue

        # If no results found
        print(f"  ❌ No Spotify match found for: {song_name}")
        self.uri_cache[song_id] = ""
        self._save_cache()
        return ""

    def process_animelist(self, animelist_file: str, output_file: str):
        """Process entire anime list and save Spotify URIs"""
        print(f"Loading anime list from: {animelist_file}")

        with open(animelist_file, "r", encoding="utf-8") as f:
            animelist_data = json.load(f)

        spotify_data = {
            "username": animelist_data.get("username", ""),
            "spotify_uris": {},
            "songs_without_spotify": [],
        }

        total_songs = 0
        found_songs = 0

        for anime in animelist_data.get("anime", []):
            anime_title = anime.get("title", "Unknown Anime")
            anime_id = anime.get("id", "")

            print(f"\n🎌 Processing: {anime_title}")

            # Process opening themes
            for theme in anime.get("opening_themes", []):
                total_songs += 1
                song_id = str(theme.get("id", f"op_{anime_id}_{total_songs}"))
                song_name = theme.get("name", "")
                artist = theme.get("artist", "")

                if not song_name:
                    print(f"  ⚠️ Skipping - no song name")
                    continue

                print(f"  🎵 OP: {song_name} - {artist}")

                spotify_uri = self.search_spotify_track(
                    song_name, artist, anime_title, song_id
                )

                if spotify_uri:
                    found_songs += 1
                    spotify_data["spotify_uris"][song_id] = {
                        "uri": spotify_uri,
                        "name": song_name,
                        "artist": artist,
                        "anime": anime_title,
                        "type": "opening",
                    }
                else:
                    spotify_data["songs_without_spotify"].append(
                        {
                            "id": song_id,
                            "name": song_name,
                            "artist": artist,
                            "anime": anime_title,
                            "type": "opening",
                        }
                    )

            # Process ending themes
            for theme in anime.get("ending_themes", []):
                total_songs += 1
                song_id = str(theme.get("id", f"ed_{anime_id}_{total_songs}"))
                song_name = theme.get("name", "")
                artist = theme.get("artist", "")

                if not song_name:
                    print(f"  ⚠️ Skipping - no song name")
                    continue

                print(f"  🎵 ED: {song_name} - {artist}")

                spotify_uri = self.search_spotify_track(
                    song_name, artist, anime_title, song_id
                )

                if spotify_uri:
                    found_songs += 1
                    spotify_data["spotify_uris"][song_id] = {
                        "uri": spotify_uri,
                        "name": song_name,
                        "artist": artist,
                        "anime": anime_title,
                        "type": "ending",
                    }
                else:
                    spotify_data["songs_without_spotify"].append(
                        {
                            "id": song_id,
                            "name": song_name,
                            "artist": artist,
                            "anime": anime_title,
                            "type": "ending",
                        }
                    )

        # Save results
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(spotify_data, f, indent=2, ensure_ascii=False)

        print(f"\n🎉 Processing complete!")
        print(f"📊 Total songs processed: {total_songs}")
        print(f"✅ Found on Spotify: {found_songs}")
        print(
            f"❌ Not found on Spotify: {len(spotify_data['songs_without_spotify'])}"
        )
        print(f"💾 Results saved to: {output_file}")


def create_spotify_playlist(
    spotify_data_file: str, playlist_name: str = "Anime Themes Collection"
):
    """Create a Spotify playlist from the found URIs"""
    # Load Spotify credentials
    with open("project/.secret/spotify_api.json", "r") as f:
        spotify_creds = json.load(f)

    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=spotify_creds["Client ID"],
            client_secret=spotify_creds["Client secret"],
            redirect_uri="http://127.0.0.1:8888/callback",
            scope="playlist-modify-public",
        )
    )

    with open(spotify_data_file, "r", encoding="utf-8") as f:
        spotify_data = json.load(f)

    # Get all Spotify URIs
    spotify_uris = [
        data["uri"] for data in spotify_data["spotify_uris"].values()
    ]

    if not spotify_uris:
        print("❌ No Spotify URIs found to create playlist")
        return

    print(f"🎵 Creating Spotify playlist with {len(spotify_uris)} songs...")

    # Get current user
    user = sp.current_user()

    # Create playlist
    playlist = sp.user_playlist_create(
        user=user["id"],
        name=playlist_name,
        public=True,
        description=f"Anime themes collection from {spotify_data['username']}'s MAL list",
    )

    # Add tracks in batches (Spotify limit: 100 per request)
    for i in range(0, len(spotify_uris), 100):
        batch = spotify_uris[i : i + 100]
        sp.playlist_add_items(playlist["id"], batch)
        print(f"  Added batch {i//100 + 1}/{(len(spotify_uris)-1)//100 + 1}")

    print(
        f"✅ Spotify playlist created: {playlist['external_urls']['spotify']}"
    )
    return playlist["external_urls"]["spotify"]


def load_spotify_credentials():
    """Load Spotify credentials from .secret/spotify_api.json"""
    try:
        with open("project/.secret/spotify_api.json", "r") as f:
            creds = json.load(f)
        return creds["Client ID"], creds["Client secret"]
    except FileNotFoundError:
        print("❌ File not found: .secret/spotify_api.json")
        print(
            "Please create .secret/spotify_api.json with your Spotify API credentials:"
        )
        print(
            """
{
    "Client ID": "your_spotify_client_id_here",
    "Client secret": "your_spotify_client_secret_here"
}
"""
        )
        return None, None
    except KeyError as e:
        print(f"❌ Missing key in .secret/spotify_api.json: {e}")
        return None, None


if __name__ == "__main__":
    # Load Spotify credentials from .secret file
    client_id, client_secret = load_spotify_credentials()

    if not client_id or not client_secret:
        exit(1)

    # Initialize the searcher
    searcher = SpotifySearcher(client_id, client_secret)

    # Process your anime list
    animelist_file = (
        "docs/data/animelist.json"  # Your existing animelist.json file
    )
    output_file = "docs/data/spotify_uris.json"

    if not os.path.exists(animelist_file):
        print(f"❌ File not found: {animelist_file}")
        print(
            "Please make sure your animelist.json file exists in the same directory"
        )
        exit(1)

    # Search for all Spotify URIs
    searcher.process_animelist(animelist_file, output_file)

    # Optional: Create Spotify playlist automatically
    if len(searcher.uri_cache) > 0:
        create_playlist = (
            input("\nCreate Spotify playlist? (y/n): ").lower().strip()
        )
        if create_playlist == "y":
            playlist_url = create_spotify_playlist(output_file)
            print(f"🎉 Playlist URL: {playlist_url}")
    else:
        print("No Spotify URIs found to create a playlist.")
