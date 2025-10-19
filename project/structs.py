import json
import re
from typing import Any, Optional

from project.utils import Cache


class ThemeSong:
    """
    Class to store anime theme song information.

    Handles parsing of theme song data from MAL API and retrieval of
    music URLs from either YouTube or Spotify based on configuration.

    Parameters
    ----------
    theme_song : Any
        JSON containing information about the theme song from MAL API

    Attributes
    ----------
    id : int
        MyAnimeList ID of the theme song
    anime_id : int
        MyAnimeList ID of the theme song anime
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
    at_url : str
        AnimeThemes.moe URL for the theme song
    yt_url : str
        YouTube URL for the theme song
    spotify_uri : str
        Spotify URI for the theme song
    """

    def __init__(
        self,
        theme_song: Any,
    ) -> None:
        self.id: int
        self.anime_id: int
        self.text: str
        self.index: Optional[str]
        self.name: str
        self.artist: str
        self.episode: Optional[str]
        self._at_url: str = ""
        self._yt_url: str = ""
        self._spotify_uri: str = ""

        if theme_song:
            self.id = theme_song["id"]
            self.anime_id = theme_song["anime_id"]
            self.text = theme_song["text"]
            self._parse_text()

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

    @property
    def at_url(self) -> str:
        # if not self._at_url:
        #     raise ValueError
        return self._at_url

    @at_url.setter
    def at_url(self, value: Any) -> None:
        if not isinstance(value, str):
            raise TypeError
        self._at_url = value

    @property
    def yt_url(self) -> str:
        if not self._yt_url:
            self._yt_url = Cache.retrieve_youtube(
                theme_id=str(self.id), title=self.name, artist=self.artist
            )
        return self._yt_url

    @yt_url.setter
    def yt_url(self, value: Any) -> None:
        if not isinstance(value, str):
            raise TypeError
        self._yt_url = value

    @property
    def spotify_uri(self) -> str:
        # if not self._spotify_uri:
        #     self._spotify_uri = Cache.retrieve_spotify(
        #         theme_id=str(self.id), title=self.name, artist=self.artist
        #     )
        return self._spotify_uri

    @spotify_uri.setter
    def spotify_uri(self, value: Any) -> None:
        if not isinstance(value, str):
            raise TypeError
        self._spotify_uri = value

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
        out["at_url"] = self.at_url
        out["yt_url"] = self.yt_url
        out["spotify_uri"] = self.spotify_uri

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
        out.at_url = theme_song["at_url"]
        out.yt_url = theme_song["yt_url"]
        out.spotify_uri = theme_song["spotify_uri"]

        return out

    def __repr__(self) -> str:
        """Return string representation of ThemeSong."""
        return (
            "ThemeSong("
            + f"ID: {self.id}, "
            + f"Anime_ID: {self.anime_id}, "
            + f"Name: {self.name}, "
            + f"Artist: {self.artist}"
            + ")"
        )


class Anime:
    """
    Class to store anime information.

    Parameters
    ----------
    anime_id : str, optional
        Anime ID from MAL API

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
    """

    def __init__(
        self,
        anime_id: Optional[str] = None,
    ) -> None:
        self.id: str = ""
        self.title: str = ""
        self.picture: str = ""
        self.opening_themes: list[ThemeSong] = []
        self.ending_themes: list[ThemeSong] = []

        if anime_id:
            anime_data = Cache.retrieve_anime(anime_id)
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
            i = 0
            animethemes_data_full = Cache.retrieve_animethemes(
                anime_id=anime_id, log=True
            )
            animethemes_bool = "animethemes" in animethemes_data_full
            if animethemes_bool:
                animethemes_data = animethemes_data_full["animethemes"]
                n = len(animethemes_data)
            else:
                n = 0
            if "opening_themes" in anime_data:
                for opening_theme in anime_data["opening_themes"]:
                    self.opening_themes.append(ThemeSong(opening_theme))
                    if animethemes_bool and i < n:
                        self.opening_themes[-1].at_url = animethemes_data[i][
                            "animethemeentries"
                        ][0]["videos"][0]["link"]
                    i += 1
            if "ending_themes" in anime_data:
                for ending_theme in anime_data["ending_themes"]:
                    self.ending_themes.append(ThemeSong(ending_theme))
                    if animethemes_bool and i < n:
                        self.ending_themes[-1].at_url = animethemes_data[i][
                            "animethemeentries"
                        ][0]["videos"][0]["link"]
                    i += 1

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
        anime_data = Cache.retrieve_anime(str(anime_id))
        if "title" in anime_data:
            return anime_data["title"]
        else:
            print(f"No title for anime with ID {anime_id}.")
            return ""

    def __repr__(self) -> str:
        """Return string representation of Anime."""
        return "Anime(" + f"ID: {self.id}, " + f"Title: {self.title}" + ")"


class AnimeList:
    """
    Class to store User's anime list information.

    Parameters
    ----------
    username : str, optional
        User's MyAnimeList username

    Attributes
    ----------
    username : str
        User's MyAnimeList username
    anime : list[Anime]
        List of anime in the user's list
    """

    def __init__(self, username: Optional[str] = None) -> None:
        self.username = username
        self.anime: list[Anime] = []
        if username:
            animelist_data = Cache.retrieve_animelist(username)
            n = len(animelist_data)
            for i, (anime_id, title) in enumerate(animelist_data.items()):
                print(
                    f"({i:0{len(str(n))}d}/{n}) Initializing "
                    + f"anime '{title}'"
                )
                self.anime.append(Anime(anime_id=anime_id))
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
        out.anime = [Anime.json_decode(anime) for anime in anime_list["anime"]]

        return out

    def __repr__(self) -> str:
        """Return string representation of AnimeList."""
        return (
            "AnimeList("
            + f"Username: {self.username}, "
            + f"Anime count: {len(self.anime)}"
            + ")"
        )


if __name__ == "__main__":
    al = AnimeList("mik2003")
    with open("test.json", "w", encoding="utf-8") as f:
        json.dump(al.json_encode(), f)
