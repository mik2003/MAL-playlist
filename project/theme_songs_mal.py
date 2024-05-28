"""
Module for anime theme songs retrieval from MyAnimeList.
"""

from dataclasses import dataclass
from urllib import request

from bs4 import BeautifulSoup, Tag


@dataclass(frozen=True)
class MALConstants:
    """
    Dataclass containing constants related to MyAnimeList HTML tags.
    """

    # MAL anime page URL
    url = "https://myanimelist.net/anime"
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
    def mal_songs(mal_url: str) -> "AnimeSongs":
        """
        Static method to instantiate AnimeSongs from MyAnimeList URL.

        Parameters
        ----------
        mal_url : str
            URL of the anime page on MyAnimeList.
            (!) IMPORTANT: only use the relative portion of the MAL URL,
            of the form '/1234/Anime_Name'.

        Returns
        -------
        AnimeSongs
            The instantiated AnimeSongs.
        """
        out = AnimeSongs()
        out.url += mal_url
        try:
            html = request.urlopen(out.url)
        except request.HTTPError as http_err:
            print(http_err)
        else:
            soup = BeautifulSoup(html, features="html.parser")
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


if __name__ == "__main__":
    url = "/49458/Kono_Subarashii_Sekai_ni_Shukufuku_wo_3"
    anime_songs = AnimeSongs.mal_songs(url)
    print(anime_songs)
