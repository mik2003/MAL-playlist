"""
Module for anime theme songs retrieval from MyAnimeList.
"""

import json
import re
from typing import Any

from project.malapi import MALAPI
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
        self.id: int = theme_song["id"]
        self.anime_id: int = theme_song["anime_id"]
        self.text: str = theme_song["text"]
        self.index: str
        self.name: str
        self.artist: str
        self.episode: str
        self.yt_url: list[str]
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
            self.url = youtube_data[str(self.id)]
        else:
            self.url = yt_search(f"{self.name} {self.artist}")
            youtube_data[str(self.id)] = self.url
            with open(MALAPI.yt, "w", encoding="utf-8") as youtube_json:
                json.dump(youtube_data, youtube_json, indent=4)

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
    opening_themes : list[ThemeSong]
        List of anime opening themes.
    ending_themes : list[ThemeSong]
        List of anime ending themes.
    """

    def __init__(self, anime_id: str) -> None:
        self.id: str = ""
        self.title: str = ""
        self.opening_themes: list[ThemeSong] = []
        self.ending_themes: list[ThemeSong] = []
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
                if "opening_themes" in anime_data:
                    for opening_theme in anime_data["opening_themes"]:
                        self.opening_themes.append(ThemeSong(opening_theme))
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
        username: str,
    ) -> None:
        self.username = username
        self.anime: list[Anime] = []
        offset = 0
        while True:
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
                                + f"anime '{anime["node"]["title"]}'")
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

    def __repr__(self) -> str:
        return (
            "AnimeList("
            + f"Username: {self.username}, "
            + f"Anime: {self.anime}, "
            + ")"
        )
