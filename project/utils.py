import json
import os
import re
import time
from dataclasses import dataclass
from typing import Any, Dict, List
from urllib.parse import quote

import requests
from selenium import webdriver


def json_read(path: str) -> Any:
    """
    Read and parse a JSON file.

    Parameters
    ----------
    path : str
        Path to the JSON file to read

    Returns
    -------
    Any
        Parsed JSON content
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@dataclass(frozen=True)
class Cache:
    """
    Cache management for anime and animethemes data.

    Provides static methods to retrieve and update cached data
    from various anime APIs.
    """

    anime = os.path.join("project", "cache", "anime", "{}.json")
    animelist = os.path.join("project", "cache", "animelist", "{}.json")
    animethemes = os.path.join("project", "cache", "animethemes", "{}.json")
    youtube = os.path.join("project", "cache", "youtube", "youtube.json")
    spotify = os.path.join("project", "cache", "spotify", "spotify.json")

    @staticmethod
    def retrieve_anime(anime_id: str, log: bool = False) -> Dict[str, Any]:
        """
        Retrieve anime data from cache or update if not present.

        Parameters
        ----------
        anime_id : str
            MyAnimeList anime ID
        log : bool, optional
            Whether to print log messages to console, by default False

        Returns
        -------
        Dict[str, Any]
            Anime data from MyAnimeList API
        """
        filepath = Cache.anime.format(anime_id)
        if not os.path.exists(filepath):
            if log:
                print(f"Cache miss for anime {anime_id}, updating...")
            Cache.update_anime(anime_id, log=log)
        else:
            if log:
                print(f"Retrieved anime {anime_id} from cache")
        return json_read(filepath)

    @staticmethod
    def retrieve_animelist(username: str, log: bool = False) -> Dict[str, str]:
        """
        Retrieve animelist data from cache or update if not present.

        Parameters
        ----------
        username : str
            User's MyAnimeList username
        log : bool, optional
            Whether to print log messages to console, by default False

        Returns
        -------
        Dict[str, Any]
            Anime data from MyAnimeList API
        """
        filepath = Cache.animelist.format(username)
        if not os.path.exists(filepath):
            if log:
                print(f"Cache miss for {username} animelist, updating...")
            Cache.update_animelist(username, log=log)
        else:
            if log:
                print(f"Retrieved {username} animellist from cache")
        return json_read(filepath)

    @staticmethod
    def retrieve_animethemes(
        anime_id: str, log: bool = False
    ) -> Dict[str, Any]:
        """
        Retrieve animethemes data from cache or update if not present.

        Parameters
        ----------
        anime_id : str
            MyAnimeList anime ID
        log : bool, optional
            Whether to print log messages to console, by default False

        Returns
        -------
        Dict[str, Any]
            Animethemes data from AnimeThemes API
        """
        filepath = Cache.animethemes.format(anime_id)
        if not os.path.exists(filepath):
            if log:
                print(f"Cache miss for animethemes {anime_id}, updating...")
            Cache.update_animethemes(anime_id, log=log)
        else:
            if log:
                print(f"Retrieved animethemes {anime_id} from cache")
        try:
            out = json_read(filepath)
        except json.decoder.JSONDecodeError:
            Cache.update_animethemes(anime_id, log=log)
            out = json_read(filepath)
        return out

    @staticmethod
    def retrieve_youtube(
        theme_id: str, title: str = "", artist: str = "", log: bool = False
    ) -> str:
        """
        Retrieve YouTube URL for theme from cache or update if not present.

        Parameters
        ----------
        theme_id : str
            MyAnimeList's ID for anime theme
        title : str, optional
            Theme title
        artist : str, optional
            Theme artist(s)
        log : bool, optional
            Whether to print log messages to console, by default False

        Returns
        -------
        str
            YouTube URL for theme
        """
        if os.path.exists(Cache.youtube):
            cache = json_read(Cache.youtube)
            if theme_id in cache:
                if log:
                    print(f"Retrieved theme with ID  {theme_id} from cache")
                return cache[theme_id]
        if title and artist:
            if log:
                print(
                    f"YouTube cache missing for theme with ID  {theme_id}, creating..."
                )
            Cache.update_youtube(theme_id, title, artist, log=log)
            cache = json_read(Cache.youtube)
            return cache[theme_id]
        raise AttributeError(
            "Cache.retrieve_youtube: title and/or artist not present, "
            + "unable to retrieve URL."
        )

    @staticmethod
    def retrieve_spotify(
        theme_id: str, title: str = "", artist: str = "", log: bool = False
    ) -> str:
        """
        Retrieve Spotify URI for theme from cache or update if not present.

        Parameters
        ----------
        theme_id : str
            MyAnimeList's ID for anime theme
        title : str, optional
            Theme title
        artist : str, optional
            Theme artist(s)
        log : bool, optional
            Whether to print log messages to console, by default False

        Returns
        -------
        str
            Spotify URI for theme
        """
        if os.path.exists(Cache.spotify):
            cache = json_read(Cache.spotify)
            if theme_id in cache:
                if log:
                    print(f"Retrieved theme with ID  {theme_id} from cache")
                return cache[theme_id]
        if title and artist:
            if log:
                print(
                    f"Spotify cache missing for theme with ID  {theme_id}, creating..."
                )
            Cache.update_spotify(theme_id, title, artist, log=log)
            cache = json_read(Cache.spotify)
            return cache[theme_id]
        raise AttributeError(
            "Cache.retrieve_spotify: title and/or artist not present, "
            + "unable to retrieve URI."
        )

    @staticmethod
    def update_anime(anime_id: str, log: bool = False) -> None:
        """
        Update anime cache with fresh data from MyAnimeList API.

        Parameters
        ----------
        anime_id : str
            MyAnimeList anime ID
        log : bool, optional
            Whether to print log messages to console, by default False
        """
        if log:
            print(f"Updating anime cache for ID: {anime_id}")

        with open(Cache.anime.format(anime_id), "w", encoding="utf-8") as f:
            json.dump(API.MAL.retrieve_anime(anime_id, log=log), f)

        if log:
            print(f"Successfully updated anime cache for ID: {anime_id}")

    @staticmethod
    def update_animelist(username: str, log: bool = False) -> None:
        """
        Update animelist cache with fresh data from MyAnimeList.

        Parameters
        ----------
        username : str
            User's MyAnimeList username
        log : bool, optional
            Whether to print log messages to console, by default False
        """
        if log:
            print(f"Updating animelist cache for username: {username}")

        with open(
            Cache.animelist.format(username), "w", encoding="utf-8"
        ) as f:
            json.dump(API.MAL.retrieve_animelist(username, log=log), f)

        if log:
            print(f"Successfully updated animelist cache for ID: {username}")

    @staticmethod
    def update_animethemes(anime_id: str, log: bool = False) -> None:
        """
        Update animethemes cache with fresh data from AnimeThemes API.

        Parameters
        ----------
        anime_id : str
            MyAnimeList anime ID
        log : bool, optional
            Whether to print log messages to console, by default False
        """
        if log:
            print(f"Updating animethemes cache for ID: {anime_id}")

        with open(
            Cache.animethemes.format(anime_id), "w", encoding="utf-8"
        ) as f:
            json.dump(API.AT.retrieve_anime(anime_id, log=log), f)

        if log:
            print(f"Successfully updated animethemes cache for ID: {anime_id}")

    @staticmethod
    def update_youtube(
        theme_id: str, title: str, artist: str, log: bool = False
    ) -> None:
        """
        Update anime theme cache with fresh data from YouTube.

        Parameters
        ----------
        theme_id : str
            MyAnimeList' anime theme ID
        title : str
            Theme title
        artist : str
            Theme artist(s)
        log : bool, optional
            Whether to print log messages to console, by default False
        """
        if log:
            print(f"Updating YouTube cache for ID: {theme_id}")

        if os.path.exists(Cache.youtube):
            cache = json_read(Cache.youtube)
        else:
            cache = {}

        cache[theme_id] = API.YT.get_theme_url(title=title, artist=artist)

        with open(Cache.youtube, "w", encoding="utf-8") as f:
            json.dump(cache, f)

        if log:
            print(
                f"Successfully updated YouTube cache for theme ID: {theme_id}"
            )

    @staticmethod
    def update_spotify(
        theme_id: str, title: str, artist: str, log: bool = False
    ) -> None:
        """
        Update anime theme cache with fresh data from Spotify.

        Parameters
        ----------
        theme_id : str
            MyAnimeList' anime theme ID
        title : str
            Theme title
        artist : str
            Theme artist(s)
        log : bool, optional
            Whether to print log messages to console, by default False
        """
        if log:
            print(f"Updating Spotify cache for ID: {theme_id}")

        if os.path.exists(Cache.spotify):
            cache = json_read(Cache.spotify)
        else:
            cache = {}

        cache[theme_id] = API.Spotify.get_theme_uri(title=title, artist=artist)

        with open(Cache.spotify, "w", encoding="utf-8") as f:
            json.dump(cache, f)

        if log:
            print(
                f"Successfully updated Spotify cache for theme ID: {theme_id}"
            )


@dataclass(frozen=True)
class API:
    """
    API client for various anime data sources.

    Provides access to MyAnimeList and AnimeThemes APIs with rate limiting.
    """

    # Sleep time between API calls [s]
    sleep_time = 2

    @dataclass(frozen=True)
    class MAL:
        """
        MyAnimeList API client.

        Provides methods to interact with the MyAnimeList API v2.
        """

        endpoint_v2 = "https://api.myanimelist.net/v2"
        keys = os.path.join("project", ".secret", "mal_api.json")
        anime = "/anime/{}?fields=opening_themes,ending_themes"
        animelist_url = (
            "https://myanimelist.net/animelist/{}?order=-5&status=2"
        )

        @staticmethod
        def params_client_id() -> dict[str, str]:
            """
            Get authentication headers for MyAnimeList API.

            Returns
            -------
            dict[str, str]
                Headers containing Client ID authentication
            """
            keys = json_read(API.MAL.keys)
            client_id = keys["Client_ID"]
            params = {"X-MAL-CLIENT-ID": client_id}

            return params

        @staticmethod
        def retrieve_anime(anime_id: str, log: bool = False) -> Dict[str, Any]:
            """
            Retrieve anime data from MyAnimeList API.

            Parameters
            ----------
            anime_id : str
                MyAnimeList anime ID
            log : bool, optional
                Whether to print log messages to console, by default False

            Returns
            -------
            Dict[str, Any]
                Anime data from MyAnimeList API

            Raises
            ------
            requests.HTTPError
                If the API request fails
            """
            if log:
                print(f"Fetching anime {anime_id} from MyAnimeList API...")

            r = requests.get(
                API.MAL.endpoint_v2 + API.MAL.anime.format(anime_id),
                headers=API.MAL.params_client_id(),
                timeout=10,
            )
            time.sleep(API.sleep_time)

            if r.status_code == 200:
                if log:
                    print(
                        f"Successfully fetched anime {anime_id} from MyAnimeList API"
                    )
                return r.json()
            else:
                if log:
                    print(
                        f"Failed to fetch anime {anime_id}: HTTP {r.status_code}"
                    )
                raise requests.HTTPError(f"HTTP {r.status_code}: {r.text}")

        @staticmethod
        def retrieve_animelist(
            username: str, log: bool = False
        ) -> Dict[str, str]:
            """
            Retrieve animelist from user's MyAnimeList.

            Parameters
            ----------
            username : str
                User's MyAnimeList username
            log : bool, optional
                Whether to print log messages to console, by default False

            Returns
            -------
            Dict[str, str]
                Animelist entries ("anime ID": "anime name")
            """
            if log:
                print(
                    f"Scraping anime list for {username} from MyAnimeList..."
                )

            # Initialize a headless Firefox browser.
            if log:
                print("Initializing headless Firefox browser...")

            options = webdriver.FirefoxOptions()
            options.add_argument("--headless")
            driver = webdriver.Firefox(options=options)

            # Load the MAL page
            if log:
                print(f"Loading MyAnimeList page for user: {username}")

            driver.get(API.MAL.animelist_url.format(username))

            # Scroll to the bottom of the page multiple times
            num_scrolls = 5
            if log:
                print(
                    f"Scrolling page {num_scrolls} times to load all content..."
                )

            for i in range(num_scrolls):
                # Scroll to the bottom of the page
                driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);"
                )
                # Wait for some time to let content load
                time.sleep(2)
                if log:
                    print(f"Scroll {i+1}/{num_scrolls} completed")

            # Extract anime titles
            if log:
                print("Extracting anime data from page source...")

            anime_list_raw = re.findall(
                r'<a href="/anime/(\d+)/[^"]+" class="link sort">([^<]+)</a>',
                driver.page_source,
            )

            # Terminate browser
            if log:
                print("Closing browser...")

            driver.quit()

            anime_list = {}

            for anime in anime_list_raw:
                anime_list[anime[0]] = anime[1]

            if log:
                print(
                    f"Successfully extracted {len(anime_list)} anime entries"
                )
                if anime_list:
                    sample_anime = list(anime_list.items())[
                        :3
                    ]  # Show first 3 as sample
                    print(f"Sample entries: {dict(sample_anime)}")

            return anime_list

    @dataclass(frozen=True)
    class AT:
        """
        AnimeThemes API client.

        Provides methods to interact with the AnimeThemes API.
        """

        enpoint_anime = "https://api.animethemes.moe/anime"

        @staticmethod
        def params_mal_anime_id(anime_id: str) -> Dict[str, str]:
            """
            Get query parameters for AnimeThemes API anime lookup.

            Parameters
            ----------
            anime_id : str
                MyAnimeList anime ID to search for

            Returns
            -------
            Dict[str, str]
                Query parameters for AnimeThemes API request
            """
            return {
                "filter[has]": "resources",
                "filter[site]": "MyAnimeList",
                "filter[external_id]": anime_id,
                "fields[anime]": "id,name,slug",
                "include": "animethemes,animethemes.animethemeentries,animethemes.animethemeentries.videos",
            }

        @staticmethod
        def retrieve_anime(anime_id: str, log: bool = False) -> Dict[str, Any]:
            """
            Retrieve anime data from AnimeThemes API.

            Parameters
            ----------
            anime_id : str
                MyAnimeList anime ID to search for
            log : bool, optional
                Whether to print log messages to console, by default False

            Returns
            -------
            Dict[str, Any]
                Anime data from AnimeThemes API

            Raises
            ------
            requests.HTTPError
                If the API request fails
            """
            if log:
                print(
                    f"Fetching animethemes for {anime_id} from AnimeThemes API..."
                )

            r = requests.get(
                API.AT.enpoint_anime,
                params=API.AT.params_mal_anime_id(anime_id),
                timeout=10,
            )
            time.sleep(API.sleep_time)

            if r.status_code == 200:
                anime_data = r.json()["anime"]
                if anime_data:
                    data = anime_data[0]
                    if log:
                        print(
                            f"Successfully fetched animethemes for {anime_id}: {len(data.get('animethemes', []))} themes found"
                        )
                    return data
            if log:
                print(
                    f"Failed to fetch animethemes for {anime_id}: HTTP {r.status_code}"
                )
            return {}

    class YT:
        search_query_url = "https://www.youtube.com/results?search_query={}"
        video_url = "https://www.youtube.com/watch?v={}"
        video_url_re = r"watch\?v=(\S{11})"

        @staticmethod
        def get_theme_url(title: str, artist: str, log: bool = False) -> str:
            """
            Get YouTube URL for a theme song.

            Searches YouTube for a theme song and returns the URL of the first result.

            Parameters
            ----------
            title : str
                Title of the theme song
            artist : str
                Artist name of the theme song
            log : bool, optional
                Whether to print log messages to console, by default False

            Returns
            -------
            str
                YouTube video URL for the theme song

            Raises
            ------
            IndexError
                If no video IDs are found for the search query
            requests.HTTPError
                If the YouTube search request fails
            """
            if log:
                print(f"Searching YouTube for: '{title}' by {artist}")

            video_ids = API.YT.get_theme_ids(
                title=title, artist=artist, log=log
            )

            if not video_ids:
                if log:
                    print(
                        f"No YouTube videos found for: '{title}' by {artist}"
                    )
                raise IndexError(
                    f"No YouTube videos found for: '{title}' by {artist}"
                )

            url = API.YT.video_url.format(video_ids[0])

            if log:
                print(f"Selected YouTube URL: {url}")

            return url

        @staticmethod
        def get_theme_ids(
            title: str, artist: str, log: bool = False
        ) -> List[str]:
            """
            Get YouTube video IDs for a theme song search.

            Searches YouTube and extracts video IDs from the search results.

            Parameters
            ----------
            title : str
                Title of the theme song
            artist : str
                Artist name of the theme song
            log : bool, optional
                Whether to print log messages to console, by default False

            Returns
            -------
            List[str]
                List of YouTube video IDs found in search results

            Raises
            ------
            requests.HTTPError
                If the YouTube search request fails
            """
            search_query = f"{title} by {artist}"
            encoded_query = quote(search_query)
            search_url = API.YT.search_query_url.format(encoded_query)

            if log:
                print(f"YouTube search query: '{search_query}'")
                print(f"Search URL: {search_url}")

            r = requests.get(search_url, timeout=10)
            time.sleep(API.sleep_time)

            if r.status_code == 200:
                video_ids = re.findall(API.YT.video_url_re, r.text)

                if log:
                    print(f"Found {len(video_ids)} YouTube video IDs")
                    if video_ids:
                        print(f"First video ID: {video_ids[0]}")

                return video_ids
            else:
                if log:
                    print(
                        f"YouTube search failed with status code: {r.status_code}"
                    )
                raise requests.HTTPError(
                    f"YouTube search failed: HTTP {r.status_code}"
                )

    class Spotify:
        keys = os.path.join("project", ".secret", "spotify_api.json")

        @staticmethod
        def get_theme_uri(title: str, artist: str) -> str:
            """NOT IMPLEMENTED"""
            _, _ = title, artist
            return ""


if __name__ == "__main__":
    # print(API.YT.get_theme_url("Ocean Eyes", "Billie Eilish", log=True))

    # un = "mik2003"

    # print(Cache.retrieve_animelist(un, log=True))

    mal_id = "512"

    # # Example usage with logging
    # print("=== Without logging ===")
    # anime_data = Cache.retrieve_anime(mal_id, log=True)
    # print(f"Retrieved anime: {anime_data.get('title', 'Unknown')}")

    print("\n=== With logging ===")
    animethemes_data = Cache.retrieve_animethemes(mal_id, log=True)
    print(f"Retrieved {len(animethemes_data.get('animethemes', []))} themes")
