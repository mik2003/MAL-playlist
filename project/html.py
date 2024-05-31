from project.animelist import AnimeList
from project.malapi import MALAPI


def html_encode(username: str) -> None:
    """
    Function to encode HTML file.

    Parameters
    ----------
    username : str
        User's MyAnimeList username.
    """
    # Use this to load from the MAL API cache
    # anime_list = AnimeList(username)
    # Use this to scrape MyAnimeList directly
    anime_list = AnimeList.full(username)

    with open(f"anime_playlist_{username}.html", "w", encoding="utf-8") as f:
        f.write(
            f"<!DOCTYPE html><html><head><title>Anime playlist {username}"
            # Add styling with CSS, feel free to copy my file.
            + '</title><link rel="stylesheet" href="css/index.css"></head>'
            + f'<body><h1><a href="{MALAPI.url_animelist.format(username)}">'
            + f'Anime playlist {username}</a></h1><ol class="anime-list">'
        )
        for anime in anime_list.anime:
            f.write(
                '<li class="anime-item"><div class="anime-content"><img sr'
                + f'c="{anime.picture}" alt="{anime.title}" width="100">'
                + '<div class="anime-details"><a href'
                f'="{MALAPI.url_anime.format(anime.id)}", '
                + f'style="font-weight: bold;">{anime.title}</a>'
                + "<ul><li>Opening Theme</li><ol>"
            )
            for opening in anime.opening_themes:
                li_content = (
                    (
                        f'<a href="{opening.yt_url[0]}">'
                        if opening.yt_url
                        else ""
                    )
                    + f'"{opening.name}"'
                    + (f" by {opening.artist}" if opening.artist else "")
                    + (f" ({opening.episode})" if opening.episode else "")
                    + ("</a>" if opening.yt_url else "")
                )
                f.write(f"<li>{li_content}</li>")
            f.write("</ol><li>Ending Theme</li><ol>")
            for ending in anime.ending_themes:
                li_content = (
                    (f'<a href="{ending.yt_url[0]}">' if ending.yt_url else "")
                    + f'"{ending.name}"'
                    + (f" by {ending.artist}" if ending.artist else "")
                    + (f" ({ending.episode})" if ending.episode else "")
                    + ("</a>" if ending.yt_url else "")
                )
                f.write(f"<li>{li_content}</li>")
            f.write("</ol></li></ul></div></div></li>")
        f.write("</ol></body></html>")
