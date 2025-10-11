"""
Module for anime theme songs retrieval from MyAnimeList.

This module provides classes to retrieve and manage anime theme songs
from MyAnimeList, with support for both YouTube and Spotify as music sources.
"""

import json
import os
import re
import time
from typing import Any, Optional

from selenium import webdriver

from project.malapi import MALAPI, mal_api_retrieve_anime
from project.youtube import yt_search

# Spotify imports with error handling
try:
    import spotipy
    from spotipy.oauth2 import SpotifyOAuth

    SPOTIFY_AVAILABLE = True
except ImportError:
    SPOTIFY_AVAILABLE = False
    print("⚠️  Spotify not available - install spotipy package")
except Exception as e:
    SPOTIFY_AVAILABLE = False
    print(f"⚠️  Spotify initialization error: {e}")


class SpotifyManager:
    """
    Manages Spotify API interactions and credential loading.

    This class handles Spotify authentication, track searching, and
    provides a clean interface for Spotify operations.

    Attributes
    ----------
    client_id : str
        Spotify API client ID
    client_secret : str
        Spotify API client secret
    sp : spotipy.Spotify
        Authenticated Spotify client instance
    """

    def __init__(self):
        """Initialize Spotify manager and load credentials."""
        self.client_id = None
        self.client_secret = None
        self.sp = None
        if SPOTIFY_AVAILABLE:
            self._load_credentials()
            if self.client_id and self.client_secret:
                self._initialize_spotify()

    def _load_credentials(self) -> None:
        """
        Load Spotify credentials from .secret/spotify_api.json.

        Raises
        ------
        FileNotFoundError
            If credentials file doesn't exist
        json.JSONDecodeError
            If credentials file contains invalid JSON
        """
        try:
            with open(MALAPI.spotify_keys, "r", encoding="utf-8") as f:
                creds = json.load(f)
            self.client_id = creds.get("Client ID")
            self.client_secret = creds.get("Client secret")
            if not self.client_id or not self.client_secret:
                print(
                    "⚠️  Spotify credentials not found or incomplete in .secret/spotify_api.json"
                )
            else:
                print("✅ Spotify credentials loaded successfully")
        except FileNotFoundError:
            print(
                "⚠️  Spotify credentials file not found: .secret/spotify_api.json"
            )
        except Exception as e:
            print(f"⚠️  Error loading Spotify credentials: {e}")

    def _initialize_spotify(self) -> None:
        """
        Initialize Spotify client with authentication.

        Tests the connection by making a simple API call to ensure
        credentials are valid and the client is working.
        """
        try:
            self.sp = spotipy.Spotify(
                auth_manager=SpotifyOAuth(
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    redirect_uri="http://127.0.0.1:8888/callback",
                    scope="user-library-read playlist-modify-public",
                )
            )
            # Test the connection
            self.sp.current_user()
            print(
                "✅ Spotify client initialized and authenticated successfully"
            )
        except Exception as e:
            print(f"❌ Failed to initialize Spotify client: {e}")
            self.sp = None

    def is_available(self) -> bool:
        """
        Check if Spotify is available and authenticated.

        Returns
        -------
        bool
            True if Spotify client is available and authenticated
        """
        return self.sp is not None

    def search_track(
        self, song_name: str, artist: str, anime_title: str
    ) -> str:
        """
        Search Spotify for a track and return its URI.

        Uses multiple search strategies to find the best match for the track.
        Returns empty string if no match is found.

        Parameters
        ----------
        song_name : str
            Name of the song to search for
        artist : str
            Artist of the song
        anime_title : str
            Title of the anime (used as fallback search term)

        Returns
        -------
        str
            Spotify track URI if found, empty string otherwise
        """
        if not self.sp:
            return ""

        if not song_name or song_name.strip() == "":
            print("  ⚠️  Skipping - empty song name")
            return ""

        def clean_query(text: str) -> str:
            """Clean text for Spotify search by removing problematic characters."""
            if not text:
                return ""
            return (
                text.replace('"', "")
                .replace("\\", "")
                .replace("(", "")
                .replace(")", "")
                .strip()
            )

        # Try different search strategies in order of specificity
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
                print(f"  [Spotify] Searching: '{query}'")
                results = self.sp.search(q=query, type="track", limit=5)

                if results["tracks"]["items"]:
                    # Get the best match (first result)
                    track = results["tracks"]["items"][0]
                    spotify_uri = track["uri"]
                    print(
                        f"  ✅ [Spotify] Found: {track['name']} - {track['artists'][0]['name']}"
                    )
                    return spotify_uri

            except Exception as e:
                print(f"  ❌ [Spotify] Search error for '{query}': {e}")
                continue

        print(f"  ❌ [Spotify] No results found for: {song_name}")
        return ""


class ThemeSong:
    """
    Class to store anime theme song information.

    Handles parsing of theme song data from MAL API and retrieval of
    music URLs from either YouTube or Spotify based on configuration.

    Parameters
    ----------
    theme_song : Any
        JSON containing information about the theme song from MAL API
    use_spotify : bool, optional
        Whether to use Spotify instead of YouTube (default: False)
    spotify_manager : SpotifyManager, optional
        Spotify manager instance for API calls (default: None)

    Attributes
    ----------
    id : int
        ID of the theme song
    anime_id : int
        ID of the theme song anime
    text : str
        The full text of the theme song
    index : str
        Integer for index, useful if anime has multiple theme songs
    name : str
        Name of the theme song
    artist : str
        Artist of the theme song
    episode : str
        Episodes for which the theme song is used
    yt_url : str
        YouTube URL for the theme song
    yt_query : str
        YouTube search query used to find the theme song
    spotify_uri : str
        Spotify URI for the theme song
    use_spotify : bool
        Whether Spotify is used as the music source
    spotify_manager : SpotifyManager
        Spotify manager instance for API calls
    """

    def __init__(
        self,
        theme_song: Any,
        use_spotify: bool = False,
        spotify_manager: Optional[SpotifyManager] = None,
    ) -> None:
        self.id: int
        self.anime_id: int
        self.text: str
        self.index: Optional[str]
        self.name: str
        self.artist: str
        self.episode: Optional[str]
        self.yt_url: str = ""
        self.yt_query: str = ""
        self.spotify_uri: str = ""
        self.use_spotify = use_spotify
        self.spotify_manager = spotify_manager

        if theme_song:
            self.id = theme_song["id"]
            self.anime_id = theme_song["anime_id"]
            self.text = theme_song["text"]
            self._parse_text()
            self._retrieve_urls()

    def _parse_text(self) -> None:
        """
        Parse theme song text using regex to extract components.

        Extracts song name, artist, index, and episode information
        from the raw theme song text using regular expressions.
        """
        pattern = (
            r"(?:#(?P<index>\d+):)?"
            + r"\s*\"(?P<name>[^\"]+)\""
            + r"\s*(?:by\s+(?P<artist>(?:(?!\s+\([^()]*ep[^()]+\)$).)+))?"
            + r"\s*(?:\((?P<episode>[^()]*ep[^()]+)\)$)?"
        )

        match = re.search(pattern, self.text)
        if match:
            self.index = match.group("index")
            self.name = match.group("name")
            self.artist = match.group("artist")
            self.episode = match.group("episode")
        else:
            # Fallback parsing if regex fails
            self.name = "Unknown"
            self.artist = "Unknown"
            self.index = None
            self.episode = None

    def _retrieve_urls(self) -> None:
        """
        Retrieve music URLs based on the selected service.

        If Spotify is enabled and available, attempts to find the track
        on Spotify. Falls back to YouTube if Spotify search fails or
        if Spotify is not configured.
        """
        if (
            self.use_spotify
            and self.spotify_manager
            and self.spotify_manager.is_available()
        ):
            self._retrieve_spotify_uri()
            # For Spotify mode, ONLY use Spotify - don't fall back to YouTube
            if not self.spotify_uri:
                print(f"  ❌ [Spotify] No Spotify URI found for: {self.name}")
                # In Spotify mode, we don't want YouTube URLs at all
                self.yt_url = ""
                self.yt_query = ""
        else:
            # Use YouTube as primary service (not Spotify mode)
            self._retrieve_yt_url()
            # Clear Spotify URI when using YouTube mode
            self.spotify_uri = ""

    def _retrieve_yt_url(self) -> None:
        """
        Retrieve YouTube URL for the theme song.

        Searches YouTube for the theme song and caches the results
        to avoid repeated searches for the same song.
        """
        try:
            with open(MALAPI.yt, "r", encoding="utf-8") as youtube_json:
                youtube_data = json.load(youtube_json)
            if str(self.id) in youtube_data:
                yt_url_list = youtube_data[str(self.id)]
            else:
                print(f"  [YouTube] Searching: {self.name} by {self.artist}")
                yt_url_list = yt_search(f"{self.name}" + f" by {self.artist}")
                youtube_data[str(self.id)] = yt_url_list
                with open(MALAPI.yt, "w", encoding="utf-8") as youtube_json:
                    json.dump(youtube_data, youtube_json, indent=4)
            self.yt_url = yt_url_list[0]
            self.yt_query = yt_url_list[-1]
            print(f"  ✅ [YouTube] Found: {self.name}")
        except Exception as e:
            print(f"  ❌ [YouTube] Error: {e}")
            self.yt_url = ""
            self.yt_query = ""

    def _retrieve_spotify_uri(self) -> None:
        """
        Retrieve Spotify URI for this track.

        Checks cache first to avoid repeated API calls for the same song.
        If not found in cache, searches Spotify and updates the cache.
        """
        uri_cache = {}
        try:
            with open(MALAPI.spotify, "r", encoding="utf-8") as f:
                uri_cache = json.load(f)
                print(
                    f"  📁 Loaded Spotify cache with {len(uri_cache)} entries"
                )

            # Debug: Check if our specific song ID exists
            song_id_str = str(self.id)
            if song_id_str in uri_cache:
                cached_uri = uri_cache[song_id_str]
                print(
                    f"  🔍 Cache HIT for song ID {song_id_str}: '{cached_uri}'"
                )
            else:
                print(f"  🔍 Cache MISS for song ID {song_id_str}")
                # Debug: show first few keys to verify format
                sample_keys = list(uri_cache.keys())[:3]
                print(f"  🔍 Sample cache keys: {sample_keys}")

        except Exception as e:
            print(f"  ⚠️  Error loading Spotify cache: {e}")
            uri_cache = {}

        # Check cache first - this works even without Spotify API
        song_id_str = str(self.id)
        if song_id_str in uri_cache:
            cached_uri = uri_cache[song_id_str]
            if cached_uri and cached_uri.strip():  # Check if URI is not empty
                self.spotify_uri = cached_uri
                print(
                    f"  ✅ [Spotify] Found in cache: {self.name} -> {cached_uri}"
                )
                return
            else:
                # Cached as not found, don't search again
                self.spotify_uri = ""
                print(f"  ✅ [Spotify] Cached as not found: {self.name}")
                return

        # Rest of the method remains the same...
        # Only try API search if we have a working Spotify connection
        if not self.spotify_manager or not self.spotify_manager.is_available():
            print(
                f"  ⚠️  [Spotify] Skipping API search for '{self.name}' - Spotify not available"
            )
            self.spotify_uri = ""
            return

        # Actually search Spotify via API (only if cache miss AND API available)
        anime_title = Anime.id_to_title(self.anime_id)
        self.spotify_uri = self.spotify_manager.search_track(
            self.name, self.artist, anime_title
        )

        # Update cache with the result (even if empty)
        uri_cache[song_id_str] = self.spotify_uri
        try:
            with open(MALAPI.spotify, "w", encoding="utf-8") as f:
                json.dump(uri_cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"  ⚠️  Could not update Spotify cache: {e}")

    def json_encode(self) -> dict[str, Any]:
        """
        Encode theme song data to JSON-serializable dictionary.

        Returns
        -------
        dict[str, Any]
            Dictionary containing all theme song data
        """
        out: dict[str, Any] = {}
        out["id"] = self.id
        out["anime_id"] = self.anime_id
        out["text"] = self.text
        out["index"] = self.index
        out["name"] = self.name
        out["artist"] = self.artist
        out["episode"] = self.episode
        out["yt_url"] = self.yt_url
        out["yt_query"] = self.yt_query
        out["spotify_uri"] = self.spotify_uri
        out["use_spotify"] = self.use_spotify

        return out

    @staticmethod
    def json_decode(theme_song: dict[str, Any]) -> "ThemeSong":
        """
        Create ThemeSong instance from JSON data.

        Parameters
        ----------
        theme_song : dict[str, Any]
            Dictionary containing theme song data

        Returns
        -------
        ThemeSong
            New ThemeSong instance with decoded data
        """
        out = ThemeSong(None)
        out.id = theme_song["id"]
        out.anime_id = theme_song["anime_id"]
        out.text = theme_song["text"]
        out.index = theme_song["index"]
        out.name = theme_song["name"]
        out.artist = theme_song["artist"]
        out.episode = theme_song["episode"]
        out.yt_url = theme_song["yt_url"]
        out.yt_query = theme_song["yt_query"]
        out.spotify_uri = theme_song.get("spotify_uri", "")
        out.use_spotify = theme_song.get("use_spotify", False)

        return out

    def __repr__(self) -> str:
        """Return string representation of ThemeSong."""
        service = (
            "Spotify" if self.use_spotify and self.spotify_uri else "YouTube"
        )
        return (
            "ThemeSong("
            + f"ID: {self.id}, "
            + f"Anime_ID: {self.anime_id}, "
            + f"Service: {service}, "
            + f"Name: {self.name}, "
            + f"Spotify_URI: {self.spotify_uri}"
            + ")"
        )


class Anime:
    """
    Class to store anime information.

    Parameters
    ----------
    anime_id : str, optional
        Anime ID from MAL API
    use_spotify : bool, optional
        Whether to use Spotify for theme songs (default: False)
    spotify_manager : SpotifyManager, optional
        Spotify manager instance (default: None)

    Attributes
    ----------
    id : str
        Anime ID from MAL API
    title : str
        Anime title
    picture : str
        URL to the anime picture
    opening_themes : list[ThemeSong]
        List of anime opening themes
    ending_themes : list[ThemeSong]
        List of anime ending themes
    use_spotify : bool
        Whether Spotify is used for theme songs
    spotify_manager : SpotifyManager
        Spotify manager instance
    """

    def __init__(
        self,
        anime_id: Optional[str] = None,
        use_spotify: bool = False,
        spotify_manager: Optional[SpotifyManager] = None,
    ) -> None:
        self.id: str = ""
        self.title: str = ""
        self.picture: str = ""
        self.opening_themes: list[ThemeSong] = []
        self.ending_themes: list[ThemeSong] = []
        self.use_spotify = use_spotify
        self.spotify_manager = spotify_manager

        if anime_id:
            try:
                with open(
                    MALAPI.anime_cache.format(anime_id), "r", encoding="utf-8"
                ) as anime_json:
                    anime_data = json.load(anime_json)
                if anime_data:
                    if "id" in anime_data:
                        self.id = anime_data["id"]
                    if "title" in anime_data:
                        self.title = anime_data["title"]
                    if "main_picture" in anime_data:
                        anime_picture = anime_data["main_picture"]
                        if "medium" in anime_picture:
                            self.picture = anime_picture["medium"]
                        elif "large" in anime_picture:
                            self.picture = anime_picture["large"]
                    if "opening_themes" in anime_data:
                        for opening_theme in anime_data["opening_themes"]:
                            self.opening_themes.append(
                                ThemeSong(
                                    opening_theme, use_spotify, spotify_manager
                                )
                            )
                    if "ending_themes" in anime_data:
                        for ending_theme in anime_data["ending_themes"]:
                            self.ending_themes.append(
                                ThemeSong(
                                    ending_theme, use_spotify, spotify_manager
                                )
                            )
                else:
                    print(
                        f"Anime with id {anime_id} not found in cache. "
                        + "First retrieve the anime through the MAL API."
                    )
            except FileNotFoundError as file_err:
                print(file_err)

    def json_encode(self) -> dict[str, Any]:
        """
        Encode anime data to JSON-serializable dictionary.

        Returns
        -------
        dict[str, Any]
            Dictionary containing all anime data
        """
        out: dict[str, Any] = {}
        out["id"] = self.id
        out["title"] = self.title
        out["picture"] = self.picture
        out["opening_themes"] = [
            theme.json_encode() for theme in self.opening_themes
        ]
        out["ending_themes"] = [
            theme.json_encode() for theme in self.ending_themes
        ]
        out["use_spotify"] = self.use_spotify

        return out

    @staticmethod
    def json_decode(anime: dict[str, Any]) -> "Anime":
        """
        Create Anime instance from JSON data.

        Parameters
        ----------
        anime : dict[str, Any]
            Dictionary containing anime data

        Returns
        -------
        Anime
            New Anime instance with decoded data
        """
        out = Anime(None)
        out.id = anime["id"]
        out.title = anime["title"]
        out.picture = anime["picture"]
        out.opening_themes = [
            ThemeSong.json_decode(theme) for theme in anime["opening_themes"]
        ]
        out.ending_themes = [
            ThemeSong.json_decode(theme) for theme in anime["ending_themes"]
        ]
        out.use_spotify = anime.get("use_spotify", False)

        return out

    @staticmethod
    def id_to_title(anime_id: int) -> str:
        """
        Convert anime MAL ID to title.

        Parameters
        ----------
        anime_id : int
            MAL anime ID

        Returns
        -------
        str
            Anime title, or empty string if not found
        """
        try:
            with open(
                MALAPI.anime_cache.format(anime_id), "r", encoding="utf-8"
            ) as anime_json:
                anime_data = json.load(anime_json)
            if anime_data and "title" in anime_data:
                return anime_data["title"]
            else:
                print(
                    f"Anime with id {anime_id} not found in cache. "
                    + "First retrieve the anime through the MAL API."
                )
                return ""
        except FileNotFoundError as file_err:
            print(file_err)
            return ""

    def __repr__(self) -> str:
        """Return string representation of Anime."""
        spotify_songs = len(
            [
                t
                for t in self.opening_themes + self.ending_themes
                if t.spotify_uri
            ]
        )
        service = "Spotify" if self.use_spotify else "YouTube"
        return (
            "Anime("
            + f"ID: {self.id}, "
            + f"Title: {self.title}, "
            + f"Service: {service}, "
            + f"Spotify songs: {spotify_songs}/{len(self.opening_themes) + len(self.ending_themes)}"
            + ")"
        )


class AnimeList:
    """
    Class to store User's anime list information.

    Parameters
    ----------
    username : str, optional
        User's MyAnimeList username
    use_spotify : bool, optional
        Whether to use Spotify for theme songs (default: False)

    Attributes
    ----------
    username : str
        User's MyAnimeList username
    use_spotify : bool
        Whether Spotify is used for theme songs
    spotify_manager : SpotifyManager
        Spotify manager instance
    anime : list[Anime]
        List of anime in the user's list
    """

    def __init__(
        self, username: Optional[str] = None, use_spotify: bool = False
    ) -> None:
        self.username = username
        self.use_spotify = use_spotify
        self.spotify_manager = SpotifyManager() if use_spotify else None
        self.anime: list[Anime] = []
        offset = 0
        while True and username is not None:
            try:
                with open(
                    MALAPI.animelist_cache.format(username, offset),
                    "r",
                    encoding="utf-8",
                ) as animelist_json:
                    animelist_data = json.load(animelist_json)
                if animelist_data:
                    if "data" in animelist_data:
                        n = len(animelist_data["data"]) + offset
                        i = 0 + offset
                        for anime in animelist_data["data"]:
                            i += 1
                            print(
                                f"({i:0{len(str(n))}d}/{n}) Initializing "
                                + f"anime '{anime['node']['title']}'"
                            )
                            self.anime.append(
                                Anime(
                                    anime["node"]["id"],
                                    use_spotify,
                                    self.spotify_manager,
                                )
                            )
                else:
                    print(
                        f"{username} anime list not found in cache. "
                        + "First retrieve the anime list through the MAL API."
                    )
                if "next" in animelist_data["paging"]:
                    offset += 100
                else:
                    break
            except FileNotFoundError as file_err:
                print(file_err)
                break
        self.anime.reverse()

    def json_encode(self) -> dict[str, Any]:
        """
        Encode anime list data to JSON-serializable dictionary.

        Returns
        -------
        dict[str, Any]
            Dictionary containing all anime list data
        """
        out: dict[str, Any] = {}
        out["username"] = self.username
        out["use_spotify"] = self.use_spotify
        out["anime"] = [anime.json_encode() for anime in self.anime]

        return out

    @staticmethod
    def json_decode(anime_list: dict[str, Any]) -> "AnimeList":
        """
        Create AnimeList instance from JSON data.

        Parameters
        ----------
        anime_list : dict[str, Any]
            Dictionary containing anime list data

        Returns
        -------
        AnimeList
            New AnimeList instance with decoded data
        """
        out = AnimeList(None)
        out.username = anime_list["username"]
        out.use_spotify = anime_list.get("use_spotify", False)
        out.anime = [Anime.json_decode(anime) for anime in anime_list["anime"]]

        return out

    def __repr__(self) -> str:
        """Return string representation of AnimeList."""
        total_songs = sum(
            len(anime.opening_themes) + len(anime.ending_themes)
            for anime in self.anime
        )
        spotify_songs = sum(
            len(
                [
                    t
                    for t in anime.opening_themes + anime.ending_themes
                    if t.spotify_uri
                ]
            )
            for anime in self.anime
        )
        service = "Spotify" if self.use_spotify else "YouTube"
        return (
            "AnimeList("
            + f"Username: {self.username}, "
            + f"Service: {service}, "
            + f"Anime count: {len(self.anime)}, "
            + f"Spotify songs: {spotify_songs}/{total_songs}"
            + ")"
        )

    @staticmethod
    def mal_scrape(username: str, use_spotify: bool = False) -> "AnimeList":
        """
        Retrieve User's MyAnimeList by scraping MAL website.

        Parameters
        ----------
        username : str
            User's MyAnimeList username
        use_spotify : bool
            Whether to use Spotify for theme songs

        Returns
        -------
        AnimeList
            Initialised AnimeList object
        """
        anime_list_raw = AnimeList.raw(username, update_cache=True)

        n = len(anime_list_raw)

        print(f"Found list of {n} anime for {username}!")
        print("Initializing anime list...")

        anime_list = AnimeList(None, use_spotify)
        anime_list.username = username

        i = 0
        for anime in anime_list_raw:
            i += 1
            print(f"({i:0{len(str(n))}d}/{n}) {anime[1]}")
            mal_api_retrieve_anime(anime[0], anime[1])
            anime_list.anime.append(
                Anime(anime[0], use_spotify, anime_list.spotify_manager)
            )

        return anime_list

    @staticmethod
    def raw(username: str, update_cache: bool = False) -> list[list[str]]:
        """
        Retrieve User's raw MyAnimeList.

        Parameters
        ----------
        username : str
            User's MyAnimeList username
        update_cache : bool, optional
            If true, anime list will be retrieved from the web regardless
            of cache status, and cache is updated (default: False)

        Returns
        -------
        list[list[str]]
            List of entries in anime list. Each entry contains the
            MyAnimeList anime page URL and the anime title.
        """

        if not update_cache and os.path.exists(
            MALAPI.animelist_raw_cache.format(username)
        ):
            print(f"Anime list for {username} already in cache.")

            with open(
                MALAPI.animelist_raw_cache.format(username),
                "r",
                encoding="utf-8",
            ) as animelist_json:
                anime_list_raw = json.loads(animelist_json.read())
        else:
            print(f"Scraping anime list for {username} from MyAnimeList...")

            # Initialize a headless Firefox browser.
            options = webdriver.FirefoxOptions()
            options.add_argument("--headless")
            driver = webdriver.Firefox(options=options)

            # Load the MAL page
            driver.get(MALAPI.url_animelist.format(username))

            # Scroll to the bottom of the page multiple times
            num_scrolls = 5
            for _ in range(num_scrolls):
                # Scroll to the bottom of the page
                driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);"
                )
                # Wait for some time to let content load
                time.sleep(2)

            # Extract anime titles
            anime_list_raw = re.findall(
                r'<a href="/anime/(\d+)/[^"]+" class="link sort">([^<]+)</a>',
                driver.page_source,
            )

            # Terminate browser
            driver.quit()
            with open(
                MALAPI.animelist_raw_cache.format(username),
                "w",
                encoding="utf-8",
            ) as animelist_json:
                animelist_json.write(json.dumps(anime_list_raw, indent=4))

        return anime_list_raw

    @staticmethod
    def full(
        username: str, update_cache: bool = False, use_spotify: bool = False
    ) -> "AnimeList":
        """
        Retrieve User's full MyAnimeList.

        Parameters
        ----------
        username : str
            User's MyAnimeList username
        update_cache : bool, optional
            If true, anime list will be retrieved from the web regardless
            of cache status, and cache is updated (default: False)
        use_spotify : bool, optional
            Whether to use Spotify for theme songs (default: False)

        Returns
        -------
        AnimeList
            Initialised AnimeList object
        """

        if not update_cache and os.path.exists(
            MALAPI.animelist_full_cache.format(username)
        ):
            print(f"Anime list for {username} already in cache.")

            with open(
                MALAPI.animelist_full_cache.format(username),
                "r",
                encoding="utf-8",
            ) as animelist_json:
                anime_list_full = AnimeList.json_decode(
                    json.loads(animelist_json.read())
                )
        else:
            anime_list_full = AnimeList.mal_scrape(username, use_spotify)

            with open(
                MALAPI.animelist_full_cache.format(username),
                "w",
                encoding="utf-8",
            ) as animelist_json:
                animelist_json.write(json.dumps(anime_list_full.json_encode()))

        return anime_list_full

    def json_encode_songs(self, filename: str) -> None:
        """
        Encode all theme songs to JSON file.

        Creates separate files based on the music service used:
        - songs_spotify.json for Spotify-based songs
        - songs_youtube.json for YouTube-based songs

        Parameters
        ----------
        filename : str
            Base filename for the output JSON file
        """
        songs: dict[str, Any] = {}
        spotify_songs_count = 0
        youtube_songs_count = 0

        for anime in self.anime:
            for op in anime.opening_themes:
                if self.use_spotify:
                    # Spotify mode: only include songs with Spotify URIs
                    if op.spotify_uri and op.spotify_uri.strip():
                        songs[str(op.id)] = op.json_encode()
                        spotify_songs_count += 1
                    # else:
                    #     print(f"  ⚠️  Skipping '{op.name}' - no Spotify URI")
                else:
                    # YouTube mode: only include songs with YouTube URLs
                    if op.yt_url and op.yt_url.strip():
                        songs[str(op.id)] = op.json_encode()
                        youtube_songs_count += 1
                    else:
                        print(f"  ⚠️  Skipping '{op.name}' - no YouTube URL")

            for ed in anime.ending_themes:
                if self.use_spotify:
                    # Spotify mode: only include songs with Spotify URIs
                    if ed.spotify_uri and ed.spotify_uri.strip():
                        songs[str(ed.id)] = ed.json_encode()
                        spotify_songs_count += 1
                    # else:
                    #     print(f"  ⚠️  Skipping '{ed.name}' - no Spotify URI")
                else:
                    # YouTube mode: only include songs with YouTube URLs
                    if ed.yt_url and ed.yt_url.strip():
                        songs[str(ed.id)] = ed.json_encode()
                        youtube_songs_count += 1
                    else:
                        print(f"  ⚠️  Skipping '{ed.name}' - no YouTube URL")

        # Determine the actual filename based on service
        if self.use_spotify:
            actual_filename = os.path.join(
                "docs", "data", "songs_spotify.json"
            )
            print(
                f"💚 Saving {spotify_songs_count} Spotify songs to: {actual_filename}"
            )
        else:
            actual_filename = os.path.join(
                "docs", "data", "songs_youtube.json"
            )
            print(
                f"🔴 Saving {youtube_songs_count} YouTube songs to: {actual_filename}"
            )

        with open(actual_filename, "w", encoding="utf-8") as songs_json:
            songs_json.write(json.dumps(songs, indent=2, ensure_ascii=False))

        # Print final statistics
        if self.use_spotify:
            print(
                f"✅ Successfully saved {spotify_songs_count} Spotify songs to {actual_filename}"
            )
            if spotify_songs_count == 0:
                print(
                    "❌ No Spotify songs found! Check your Spotify credentials and internet connection."
                )
        else:
            print(
                f"✅ Successfully saved {youtube_songs_count} YouTube songs to {actual_filename}"
            )

    def create_spotify_playlist(
        self, playlist_name: str = "Anime Themes Collection"
    ) -> str:
        """
        Create a Spotify playlist from the found URIs.

        Parameters
        ----------
        playlist_name : str, optional
            Name for the Spotify playlist (default: "Anime Themes Collection")

        Returns
        -------
        str
            URL of the created Spotify playlist, or empty string if failed
        """
        if not self.spotify_manager or not self.spotify_manager.is_available():
            print("❌ Spotify is not available. Cannot create playlist.")
            return ""

        # Collect all Spotify URIs
        spotify_uris = []
        for anime in self.anime:
            for theme in anime.opening_themes + anime.ending_themes:
                if theme.spotify_uri:
                    spotify_uris.append(theme.spotify_uri)

        if not spotify_uris:
            print("❌ No Spotify URIs found to create playlist")
            return ""

        print(
            f"🎵 Creating Spotify playlist with {len(spotify_uris)} songs..."
        )

        # Get current user
        user = self.spotify_manager.sp.current_user()

        # Create playlist
        playlist = self.spotify_manager.sp.user_playlist_create(
            user=user["id"],
            name=playlist_name,
            public=True,
            description=f"Anime themes collection from {self.username}'s MAL list",
        )

        # Add tracks in batches (Spotify limit: 100 per request)
        for i in range(0, len(spotify_uris), 100):
            batch = spotify_uris[i : i + 100]
            self.spotify_manager.sp.playlist_add_items(playlist["id"], batch)
            print(
                f"  Added batch {i//100 + 1}/{(len(spotify_uris)-1)//100 + 1}"
            )

        print(
            f"✅ Spotify playlist created: {playlist['external_urls']['spotify']}"
        )
        return playlist["external_urls"]["spotify"]


# In the main section at the bottom:
if __name__ == "__main__":
    un = "mik2003"

    # Let user choose service
    # print("🎵 Choose music service:")
    # print("1. YouTube (default)")
    # print("2. Spotify")
    # choice = input("Enter choice (1 or 2): ").strip()

    # use_spotify = choice == "2"

    use_spotify = True

    if use_spotify:
        print("🎵 Using Spotify service...")

        # Test Spotify connection but don't exit if it fails
        spotify_manager = SpotifyManager()
        if not spotify_manager.is_available():
            print(
                "⚠️  Spotify API not available, but will use cached URIs if they exist"
            )
            print(
                "💡 To search for new songs, set up Spotify credentials in .secret/spotify_api.json"
            )
        else:
            print("✅ Spotify API connection successful!")

        print("💚 Only songs with Spotify URIs will be included")
        print("💚 Songs will be saved to: docs/data/songs_spotify.json")
    else:
        print("🎵 Using YouTube service...")
        print("🔴 Only songs with YouTube URLs will be included")
        print("🔴 Songs will be saved to: docs/data/songs_youtube.json")

    al = AnimeList.full(un, update_cache=True, use_spotify=use_spotify)

    # Debug: Check what we actually have before saving
    if use_spotify:
        total_songs = 0
        spotify_songs = 0

        for anime in al.anime:
            for theme in anime.opening_themes + anime.ending_themes:
                total_songs += 1
                if theme.spotify_uri:
                    spotify_songs += 1
                    print(
                        f"  ✅ Found Spotify URI for: {theme.name} -> {theme.spotify_uri}"
                    )
                # else:
                #     print(f"  ❌ No Spotify URI for: {theme.name}")

        print(f"\n📊 Spotify Results:")
        print(f"   Total songs: {total_songs}")
        print(f"   Found Spotify URIs: {spotify_songs}")
        print(f"   Not found: {total_songs - spotify_songs}")

    al.json_encode_songs("songs.json")
