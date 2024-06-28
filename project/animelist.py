"""
Module for anime theme songs retrieval from MyAnimeList.
"""

import json
import os
import re
import time
from typing import Any

from selenium import webdriver

from project.malapi import MALAPI, mal_api_retrieve_anime
from project.youtube import yt_search


class ThemeSong:
    """
    Class to store anime theme song information.

    Parameters
    ----------
    theme_song : Any
        JSON containing information about the theme song,
        as defined by the MAL API.

    Attributes
    ----------
    id : int
        ID of the theme song.
    anime_id : int
        ID of the theme song anime.
    text : str
        The full text of the theme song.
        Includes index, name, artist and episode.
    index : str
        Integer for index, useful if anime has multiple theme songs.
    name : str
        Name of the theme song.
    artist : str
        Artist of the theme song.
    episode : str
        Episodes for which the theme song is used.
    """

    def __init__(self, theme_song: Any) -> None:
        self.id: int
        self.anime_id: int
        self.text: str
        self.index: str
        self.name: str
        self.artist: str
        self.episode: str
        self.yt_url: list[str]
        if theme_song:
            self.id = theme_song["id"]
            self.anime_id = theme_song["anime_id"]
            self.text = theme_song["text"]
            self._parse_text()
            self._retrieve_yt_url()

    def _parse_text(self) -> None:
        # Regular expression (hope it's right...)
        pattern = (
            r"(?:#(?P<index>\d+):)?"
            + r"\s*\"(?P<name>[^\"]+)\""
            + r"\s*(?:by\s+(?P<artist>(?:(?!\s+\([^()]*ep[^()]+\)$).)+))?"
            + r"\s*(?:\((?P<episode>[^()]*ep[^()]+)\)$)?"
        )

        # Match regex
        match = re.search(pattern, self.text)
        if match:
            self.index = match.group("index")
            self.name = match.group("name")
            self.artist = match.group("artist")
            self.episode = match.group("episode")

    def _retrieve_yt_url(self) -> None:
        with open(MALAPI.yt, "r", encoding="utf-8") as youtube_json:
            youtube_data = json.load(youtube_json)
        if str(self.id) in youtube_data:
            self.yt_url = youtube_data[str(self.id)]
        else:
            self.yt_url = yt_search(f"{self.name} {self.artist}")
            youtube_data[str(self.id)] = self.yt_url
            with open(MALAPI.yt, "w", encoding="utf-8") as youtube_json:
                json.dump(youtube_data, youtube_json, indent=4)

    def json_encode(self) -> dict[str, Any]:
        out: dict[str, Any] = {}
        out["id"] = self.id
        out["anime_id"] = self.anime_id
        out["text"] = self.text
        out["index"] = self.index
        out["name"] = self.name
        out["artist"] = self.artist
        out["episode"] = self.episode
        out["yt_url"] = (self.yt_url[0] if self.yt_url else [])

        return out

    @staticmethod
    def json_decode(theme_song: dict[str, Any]) -> "ThemeSong":
        out = ThemeSong(None)
        out.id = theme_song["id"]
        out.anime_id = theme_song["anime_id"]
        out.text = theme_song["text"]
        out.index = theme_song["index"]
        out.name = theme_song["name"]
        out.artist = theme_song["artist"]
        out.episode = theme_song["episode"]
        yt_url = theme_song["yt_url"]
        out.yt_url = ([yt_url] if yt_url else [])

        return out

    def __repr__(self) -> str:
        return (
            "ThemeSong("
            + f"ID: {self.id}, "
            + f"Anime_ID: {self.anime_id}, "
            + f"Text: {self.text}"
            + ")"
        )


class Anime:
    """
    Class to store anime information.

    Parameters
    ----------
    anime_id : str
        Anime ID, as defined in the MAL API.

    Attributes
    ----------
    id : str
        Anime ID, as defined in the MAL API.+
    title : str
        Anime title.
    picture : str
        URL to the anime picture.
    opening_themes : list[ThemeSong]
        List of anime opening themes.
    ending_themes : list[ThemeSong]
        List of anime ending themes.
    """

    def __init__(self, anime_id: str | None) -> None:
        self.id: str = ""
        self.title: str = ""
        self.picture: str = ""
        self.opening_themes: list[ThemeSong] = []
        self.ending_themes: list[ThemeSong] = []

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
                                ThemeSong(opening_theme)
                            )
                    if "ending_themes" in anime_data:
                        for ending_theme in anime_data["ending_themes"]:
                            self.ending_themes.append(ThemeSong(ending_theme))
                else:
                    print(
                        f"Anime with id {anime_id} not found in cache. "
                        + "First retrieve the anime through the MAL API."
                    )
            except FileNotFoundError as file_err:
                print(file_err)

    def json_encode(self) -> dict[str, Any]:
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

        return out

    @staticmethod
    def json_decode(anime: dict[str, Any]) -> "Anime":
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

        return out

    def __repr__(self) -> str:
        return (
            "Anime("
            + f"ID: {self.id}, "
            + f"Title: {self.title}, "
            + f"Opening themes: {self.opening_themes}, "
            + f"Ending themes: {self.ending_themes}"
            + ")"
        )


class AnimeList:
    """
    Class to store User's anime list information.

    Parameters
    ----------
    username : str
        User's MyAnimeList username.

    Attributes
    ----------
    username : str
        User's MyAnimeList username.
    anime : list[Anime]
        List of anime.
    """

    def __init__(
        self,
        username: str | None,
    ) -> None:
        self.username = username
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
                                + f"anime '{anime["node"]["title"]}'"
                            )
                            self.anime.append(Anime(anime["node"]["id"]))
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
        out: dict[str, Any] = {}
        out["username"] = self.username
        out["anime"] = [anime.json_encode() for anime in self.anime]

        return out

    @staticmethod
    def json_decode(anime_list: dict[str, Any]) -> "AnimeList":
        out = AnimeList(None)
        out.username = anime_list["username"]
        out.anime = [Anime.json_decode(anime) for anime in anime_list["anime"]]

        return out

    def __repr__(self) -> str:
        return (
            "AnimeList("
            + f"Username: {self.username}, "
            + f"Anime: {self.anime}, "
            + ")"
        )

    @staticmethod
    def mal_scrape(username: str) -> "AnimeList":
        """
        Retrieve User's MyAnimeList.

        Parameters
        ----------
        username : str
            User's MyAnimeList username.

        Returns
        -------
        AnimeList
            Initialised AnimeList object.
        """
        anime_list_raw = AnimeList.raw(username, update_cache=True)

        n = len(anime_list_raw)

        print(f"Found list of {n} anime for {username}!")
        print("Initializing anime list...")

        anime_list = AnimeList(None)
        anime_list.username = username

        i = 0
        for anime in anime_list_raw:
            i += 1
            print(f"({i:0{len(str(n))}d}/{n}) {anime[1]}")
            mal_api_retrieve_anime(anime[0], anime[1])
            anime_list.anime.append(Anime(anime[0]))

        return anime_list

    @staticmethod
    def raw(username: str, update_cache: bool = False) -> list[list[str]]:
        """
        Retrieve User's raw MyAnimeList.

        Parameters
        ----------
        username : str
            User's MyAnimeList username.
        update_cache : bool = False
            Optional parameters, if true, anime list will be retrieved
            from the web regardless if there is a cache, and cache is updated.

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
                encoding="utf-8"
            ) as animelist_json:
                anime_list_raw = json.loads(animelist_json.read())
        else:
            print(f"Scraping anime list for {username} from MyAnimeList...")

            # Initialize a headless Firefox browser.
            options = webdriver.FirefoxOptions()
            options.add_argument("--headless")
            driver = webdriver.Firefox(options=options)

            # Load the MAL page
            driver.get(
                MALAPI.url_animelist.format(username)
            )

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
                driver.page_source
            )

            # Terminate browser
            driver.quit()
            with open(
                MALAPI.animelist_raw_cache.format(username),
                "w",
                encoding="utf-8"
            ) as animelist_json:
                animelist_json.write(json.dumps(anime_list_raw, indent=4))

        return anime_list_raw

    @staticmethod
    def full(username: str, update_cache: bool = False) -> "AnimeList":
        """
        Retrieve User's full MyAnimeList.

        Parameters
        ----------
        username : str
            User's MyAnimeList username.
        update_cache : bool = False
            Optional parameters, if true, anime list will be retrieved
            from the web regardless if there is a cache, and cache is updated.

        Returns
        -------
        AnimeList
            Initialised AnimeList object.
        """

        if not update_cache and os.path.exists(
            MALAPI.animelist_full_cache.format(username)
        ):
            print(f"Anime list for {username} already in cache.")

            with open(
                MALAPI.animelist_full_cache.format(username),
                "r",
                encoding="utf-8"
            ) as animelist_json:
                anime_list_full = AnimeList.json_decode(
                    json.loads(animelist_json.read())
                )
        else:
            anime_list_full = AnimeList.mal_scrape(username)

            with open(
                MALAPI.animelist_full_cache.format(username),
                "w",
                encoding="utf-8"
            ) as animelist_json:
                animelist_json.write(json.dumps(anime_list_full.json_encode()))

        return anime_list_full

    def json_encode_songs(self, filename: str) -> None:
        songs: dict[str, Any] = {}
        for anime in self.anime:
            for op in anime.opening_themes:
                songs[str(op.id)] = op.json_encode()
            for ed in anime.ending_themes:
                songs[str(ed.id)] = ed.json_encode()
        with open(filename, "w", encoding="utf-8") as songs_json:
            songs_json.write(json.dumps(songs))


if __name__ == "__main__":
    un = "mik2003"
    al = AnimeList.full(un, update_cache=True)
    al.json_encode_songs("songs.json")
