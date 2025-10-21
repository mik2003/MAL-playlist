import json
import re
from typing import Any, List, Literal, Optional, TypedDict, Unpack, cast

from project.utils import Cache


class EncodeOptions(TypedDict, total=False):
    """
    Configuration options for JSON encoding of Anime and AnimeTheme objects.

    This TypedDict defines all available options for controlling which fields
    are included when serializing Anime and AnimeTheme instances to JSON.

    Options are organized by object type and allow for fine-grained control
    over serialization output through include/exclude patterns.

    Parameters
    ----------
    include_null : bool, default True
        Whether to include null fields

    anime_include : List[AnimeField], optional
        Whitelist of fields to include for Anime objects.
        If specified, only these fields will be present in the output.
        Available fields: "id", "title", "picture", "opening_themes", "ending_themes"

    anime_exclude : List[AnimeField], optional
        Blacklist of fields to exclude for Anime objects.
        Only used if `anime_include` is not provided.
        Available fields: "id", "title", "picture", "opening_themes", "ending_themes"

    themesong_include : List[ThemeSongField], optional
        Whitelist of fields to include for AnimeTheme objects.
        If specified, only these fields will be present in the output.
        Available fields: "id", "anime_id", "text", "index", "name", "artist",
        "episode", "yt_id", "yt_url", "yt_query", "at_url", "spotify_uri"

    themesong_exclude : List[ThemeSongField], optional
        Blacklist of fields to exclude for AnimeTheme objects.
        Only used if `themesong_include` is not provided.
        Available fields: "id", "anime_id", "text", "index", "name", "artist",
        "episode", "yt_id", "yt_url", "yt_query", "at_url", "spotify_uri"

    Behavior
    --------
    - If neither include nor exclude options are provided for an object type,
      all fields for that object type are included.
    - Include options take precedence over exclude options.
    """

    include_null: bool
    anime_include: List[
        Literal["id", "title", "picture", "opening_themes", "ending_themes"]
    ]
    anime_exclude: List[
        Literal["id", "title", "picture", "opening_themes", "ending_themes"]
    ]
    themesong_include: List[
        Literal[
            "id",
            "anime_id",
            "text",
            "index",
            "name",
            "artist",
            "episode",
            "yt_id",
            "yt_url",
            "yt_query",
            "at_url",
            "spotify_uri",
        ]
    ]
    themesong_exclude: List[
        Literal[
            "id",
            "anime_id",
            "text",
            "index",
            "name",
            "artist",
            "episode",
            "yt_id",
            "yt_url",
            "yt_query",
            "at_url",
            "spotify_uri",
        ]
    ]


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
    yt_id : str
        YouTube video ID for theme song
    yt_url : str
        YouTube URL for the theme song
    yt_query : str
        YouTube query URL for the theme song
    at_url : str
        AnimeThemes.moe URL for the theme song
    spotify_uri : str
        Spotify URI for the theme song
    """

    def __init__(self, theme_song: Any) -> None:
        self.id: int
        self.anime_id: int
        self.text: str
        self.index: Optional[str]
        self.name: str
        self.artist: str
        self.episode: Optional[str]
        self._yt_id: str = ""
        self._yt_url: str = ""
        self._yt_query: str = ""
        self._at_url: str = ""
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
    def yt_id(self) -> str:
        if not self._yt_id:
            self._yt_id = Cache.retrieve_youtube_id(
                theme_id=str(self.id), title=self.name, artist=self.artist
            )
        return self._yt_id

    @yt_id.setter
    def yt_id(self, value: Any) -> None:
        if not isinstance(value, str):
            raise TypeError
        self._yt_id = value

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
    def yt_query(self) -> str:
        if not self._yt_query:
            self._yt_query = Cache.retrieve_youtube_query(
                theme_id=str(self.id), title=self.name, artist=self.artist
            )
        return self._yt_query

    @yt_query.setter
    def yt_query(self, value: Any) -> None:
        if not isinstance(value, str):
            raise TypeError
        self._yt_query = value

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

    def json_encode(
        self, **encode_options: Unpack[EncodeOptions]
    ) -> dict[str, Any]:
        """
        Encode theme song data to JSON-serializable dictionary.

        Parameters
        ----------
        **encode_options : EncodeOptions
            Encoding optional keyword arguments
            (See EncodeOptions for more information)

        Returns
        -------
        dict[str, Any]
            Dictionary containing all theme song data
        """
        all_fields = {
            "id": self.id,
            "anime_id": self.anime_id,
            "text": self.text,
            "index": self.index,
            "name": self.name,
            "artist": self.artist,
            "episode": self.episode,
            "yt_id": self.yt_id,
            "yt_url": self.yt_url,
            "yt_query": self.yt_query,
            "at_url": self.at_url,
            "spotify_uri": self.spotify_uri,
        }

        include_null = cast(bool, encode_options.get("include_null", True))
        include = cast(
            List[str] | None, encode_options.get("themesong_include")
        )
        exclude = cast(List[str], encode_options.get("themesong_exclude", []))

        if include:
            # Include only specified fields
            return {
                field: all_fields[field]
                for field in include
                if field in all_fields
                and (include_null or all_fields[field] is not None)
            }
        else:
            # Include all fields except excluded ones
            return {
                field: value
                for field, value in all_fields.items()
                if field not in exclude and (include_null or value is not None)
            }

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
        # Create instance without calling _parse_text
        out = ThemeSong.__new__(ThemeSong)

        # Initialize all attributes to safe defaults
        out.id = 0
        out.anime_id = 0
        out.text = ""
        out.index = None
        out.name = ""
        out.artist = ""
        out.episode = None
        out.yt_id = ""
        out.yt_url = ""
        out.yt_query = ""
        out.at_url = ""
        out.spotify_uri = ""

        # Set values with safe dictionary access
        out.id = theme_song.get("id", 0)
        out.anime_id = theme_song.get("anime_id", 0)
        out.text = theme_song.get("text", "")
        out.index = theme_song.get("index")
        out.name = theme_song.get("name", "")
        out.artist = theme_song.get("artist", "")
        out.episode = theme_song.get("episode")
        out.yt_id = theme_song.get("yt_id", "")
        out.yt_url = theme_song.get("yt_url", "")
        out.yt_query = theme_song.get("yt_query", "")
        out.at_url = theme_song.get("at_url", "")
        out.spotify_uri = theme_song.get("spotify_uri", "")

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

    def json_encode(
        self, **encode_options: Unpack[EncodeOptions]
    ) -> dict[str, Any]:
        """
        Encode anime data to JSON-serializable dictionary.

        Parameters
        ----------
        **encode_options : EncodeOptions
            Encoding optional keyword arguments
            (See EncodeOptions for more information)

        Returns
        -------
        dict[str, Any]
            Dictionary containing all anime data
        """
        all_fields = {
            "id": self.id,
            "title": self.title,
            "picture": self.picture,
            "opening_themes": [{}],
            "ending_themes": [{}],
        }
        theme_types = ["opening_themes", "ending_themes"]

        include_null = cast(bool, encode_options.get("include_null", True))
        include = cast(List[str] | None, encode_options.get("anime_include"))
        exclude = cast(List[str], encode_options.get("anime_exclude", []))

        if include:
            # Include only specified fields
            for theme_type in theme_types:
                if theme_type in include:
                    all_fields[theme_type] = [
                        theme.json_encode(**encode_options)
                        for theme in cast(
                            List[ThemeSong], getattr(self, theme_type)
                        )
                    ]
            return {
                field: all_fields[field]
                for field in include
                if field in all_fields
                and (include_null or all_fields[field] is not None)
            }
        else:
            # Include all fields except excluded ones
            for theme_type in theme_types:
                if theme_type not in exclude:
                    all_fields[theme_type] = [
                        theme.json_encode(**encode_options)
                        for theme in cast(
                            List[ThemeSong], getattr(self, theme_type)
                        )
                    ]
            return {
                field: value
                for field, value in all_fields.items()
                if field not in exclude and (include_null or value is not None)
            }

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
        out = Anime.__new__(Anime)

        # Initialize with safe defaults
        out.id = anime.get("id", 0)
        out.title = anime.get("title", "")
        out.picture = anime.get("picture", "")

        # Use list comprehensions with fallback
        opening_data = anime.get("opening_themes", [])
        out.opening_themes = [
            ThemeSong.json_decode(theme) for theme in opening_data
        ]

        ending_data = anime.get("ending_themes", [])
        out.ending_themes = [
            ThemeSong.json_decode(theme) for theme in ending_data
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

    def json_encode(
        self, **encode_options: Unpack[EncodeOptions]
    ) -> dict[str, Any]:
        """
        Encode anime list data to JSON-serializable dictionary.

        Parameters
        ----------
        **encode_options : EncodeOptions
            Encoding optional keyword arguments
            (See EncodeOptions for more information)

        Returns
        -------
        dict[str, Any]
            Dictionary containing all anime list data
        """
        out: dict[str, Any] = {}
        out["username"] = self.username
        out["anime"] = [
            anime.json_encode(**encode_options) for anime in self.anime
        ]

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
        out = AnimeList.__new__(AnimeList)
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
    al_params = {
        "include_null": True,
        "themesong_exclude": ["yt_id", "yt_query", "spotify_uri"],
    }
    query_params = {
        "include_null": False,
        "anime_exclude": ["picture"],
        "themesong_include": [
            "id",
            "name",
            "artist",
            "yt_id",
            "yt_url",
            "yt_query",
        ],
    }
    with open("test.json", "w", encoding="utf-8") as f:
        json.dump(
            al.json_encode(**query_params),  # type: ignore
            f,
            indent=4,
        )
