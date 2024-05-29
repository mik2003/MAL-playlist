"""
Module for anime theme songs retrieval from MyAnimeList.
"""

import re
import time
from dataclasses import dataclass
from urllib import request
from urllib.parse import quote

from bs4 import BeautifulSoup, Tag
from selenium import webdriver

# from project.util import click_buttons_if_present  # , random_human


@dataclass(frozen=True)
class MALConstants:
    """
    Dataclass containing constants related to MyAnimeList HTML tags.
    """

    # MAL anime page URL
    url = "https://myanimelist.net"
    url_list = "https://myanimelist.net/animelist/"
    url_list_arguments = "?order=-5&status=2"
    # Arguments for Tag.find
    theme_song_index = "span", {"class": "theme-song-index"}
    theme_song_artist = "span", {"class": "theme-song-artist"}
    theme_song_episode = "span", {"class": "theme-song-episode"}
    theme_songs_opening = (
        "div",
        {
            "class": "theme-songs js-theme-songs opnening"
        },  # Wrong spelling is intended :)
    )
    theme_songs_ending = "div", {"class": "theme-songs js-theme-songs ending"}
    theme_song = "td", {"width": "84%"}

    # Regular expression to match the anchor tags and extract href and title
    anime_re = r'<a href="(/anime/\d+/[^"]+)" class="link sort">([^<]+)</a>'


class ThemeSong:
    """
    Class to store anime theme song information.

    Attributes
    ----------
    theme_song : Tag
        The HTML tag corresponding to the theme song.
    index : str
        Integer for index, useful if anime has multiple theme songs.
    name : str
        Name of the theme song.
    artist : str
        Artist of the theme song.
    episode : str
        Episodes for which the theme song is used.
    """

    def __init__(self, theme_song: Tag) -> None:
        self.theme_song: Tag = theme_song
        self.index: str = "1"
        self.name: str = ""
        self.artist: str = ""
        self.episode: str = ""
        self._split()

    def _split(self) -> None:
        """
        Private method to retrieve ThemeSong attributes from HTML Tag.
        """
        index_tag = self.theme_song.find(*MALConstants.theme_song_index)
        if isinstance(index_tag, Tag):
            self.index = index_tag.text.strip()
            name_pos = 1
        else:
            name_pos = 0
        self.name = self.theme_song.contents[name_pos].text.strip('" ')
        artist_tag = self.theme_song.find(*MALConstants.theme_song_artist)
        if isinstance(artist_tag, Tag):
            self.artist = artist_tag.text.strip()[3:]
        episode_tag = self.theme_song.find(*MALConstants.theme_song_episode)
        if isinstance(episode_tag, Tag):
            self.episode = episode_tag.text.strip()

    def __repr__(self) -> str:
        return (
            "ThemeSong("
            + f"Index: {self.index}, "
            + f"Song: {self.name}, "
            + f"Artist: {self.artist}, "
            + f"Episodes: {self.episode}"
            + ")"
        )


class AnimeSongs:
    """
    Class to store information about an anime's theme songs.

    Attributes
    ----------
    url : str
        URL of the anime page on MyAnimeList.
    openings : list[ThemeSong]
        List of anime opening theme songs.
    endings : list[ThemeSong]
        List of anime ending theme songs.

    Methods
    -------
    mal_songs()
        Static method to instantiate AnimeSongs from MyAnimeList URL.
    """

    def __init__(self) -> None:
        self.url = MALConstants.url
        self.openings: list[ThemeSong] = []
        self.endings: list[ThemeSong] = []

    @staticmethod
    def mal_songs(
        mal_url: str, driver: webdriver.firefox.webdriver.WebDriver
    ) -> "AnimeSongs":
        """
        Static method to instantiate AnimeSongs from MyAnimeList URL.

        Parameters
        ----------
        mal_url : str
            URL of the anime page on MyAnimeList.
            (!) IMPORTANT: only use the relative portion of the MAL URL,
            of the form '/anime/123/Anime_Name'.

        Returns
        -------
        AnimeSongs
            The instantiated AnimeSongs.
        """
        out = AnimeSongs()
        out.url += quote(mal_url)
        try:
            # html = request.urlopen(out.url)
            driver.get(out.url)
            # random_human(driver)
            time.sleep(5)
        except request.HTTPError as http_err:
            print(http_err)
        else:
            soup = BeautifulSoup(driver.page_source, features="html.parser")
            openings = soup.find(*MALConstants.theme_songs_opening)
            endings = soup.find(*MALConstants.theme_songs_ending)
            if isinstance(openings, Tag):
                for opening in openings.find_all(*MALConstants.theme_song):
                    out.openings.append(ThemeSong(opening))
            if isinstance(endings, Tag):
                for ending in endings.find_all(*MALConstants.theme_song):
                    out.endings.append(ThemeSong(ending))
        return out

    def __repr__(self) -> str:
        return f"AnimeSongs(Openings: {self.openings}, Endings:{self.endings})"


class Anime:
    """
    Class to store anime information.

    Attributes
    ----------
    url : str
        URL of the anime page on MyAnimeList.
    name : str
        Name of the anime.
    songs : AnimeSongs
        Theme songs of the anime.
    """

    def __init__(
        self,
        mal_url: str,
        name: str,
        driver: webdriver.firefox.webdriver.WebDriver,
    ) -> None:
        self.url: str = mal_url
        self.name: str = name
        self.songs: AnimeSongs = AnimeSongs.mal_songs(mal_url, driver)

    def __repr__(self) -> str:
        return (
            "Anime("
            + f"Name: {self.name}, "
            + f"URL: {self.url}, "
            + f"Songs: {self.songs}"
            + ")"
        )


class AnimeList:
    """
    Class to store User's anime list information.

    Attributes
    ----------
    username : str
        User's MyAnimeList username.
    anime : list[Anime]
        List of anime.
    anime_raw : list[tuple[str, str]]
        Raw list of anime, output of mal_search.

    Methods
    -------
    mal_search(username)
        Staticmethod to retrieve user's anime list.
    """

    def __init__(
        self, username: str, driver: webdriver.firefox.webdriver.WebDriver
    ) -> None:
        self.username = username
        self.anime: list[Anime] = []
        self.anime_raw: list[tuple[str, str]] = AnimeList.mal_search(
            self.username, driver
        )
        n = len(self.anime_raw)
        i = 0
        for anime in self.anime_raw:
            i += 1
            print(
                f"({i:0{len(str(n))}d}/{n}) "
                + f"[MAL] Finding theme songs: {anime[1]}"
            )
            self.anime.append(Anime(*anime, driver))

    def __repr__(self) -> str:
        return (
            "AnimeList("
            + f"Username: {self.username}, "
            + f"Anime: {self.anime}, "
            + ")"
        )

    @staticmethod
    def mal_search(
        username: str, driver: webdriver.firefox.webdriver.WebDriver
    ) -> list[tuple[str, str]]:
        """
        Retrieve User's MyAnimeList.

        Parameters
        ----------
        username : str
            User's MyAnimeList username.
        driver : webdriver.firefox.webdriver.WebDriver
            Firefox webdriver, initiated from `project.util.init_firefox`.

        Returns
        -------
        list[tuple[str, str]]
            List of entries in anime list. Each entry contains the
            MyAnimeList anime page URL and the anime title.
        """
        print(f"Finding anime list for {username}...")

        # Load the MAL page
        driver.get(
            MALConstants.url_list + username + MALConstants.url_list_arguments
        )

        # click_buttons_if_present(driver)

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
        anime_list = re.findall(MALConstants.anime_re, driver.page_source)

        print(f"Found list of {len(anime_list)} anime for {username}!")

        return anime_list
