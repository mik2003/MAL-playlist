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
    anime_list = AnimeList.mal_scrape(username)

    with open(f"anime_playlist_{username}.html", "w", encoding="utf-8") as f:
        f.write(
            f"""<!DOCTYPE html><html><head><title>Anime playlist {username}"""
            + """</title></head><body><h1>"""
            + f"""<a href="{MALAPI.url_animelist.format(username)}">"""
            + f"""Anime playlist {username}</a></h1><ol>"""
        )
        for anime in anime_list.anime:
            f.write(
                f"""<li><a href="{MALAPI.url_anime.format(anime.id)}">"""
                + f"""{anime.title}</a></li>"""
                + """<ul><li>Opening Theme</li><ol>"""
            )
            for opening in anime.opening_themes:
                li_content = (
                    (f'<a href="{opening.url[0]}">' if opening.url else "")
                    + f'"{opening.name}"'
                    + (f" by {opening.artist}" if opening.artist else "")
                    + (f" ({opening.episode})" if opening.episode else "")
                    + ("</a>" if opening.url else "")
                )
                f.write(f"<li>{li_content}</li>")
            f.write("""</ol><li>Ending Theme</a></li><ol>""")
            for ending in anime.ending_themes:
                li_content = (
                    (f'<a href="{ending.url[0]}">' if ending.url else "")
                    + f'"{ending.name}"'
                    + (f" by {ending.artist}" if ending.artist else "")
                    + (f" ({ending.episode})" if ending.episode else "")
                    + ("</a>" if ending.url else "")
                )
                f.write(f"<li>{li_content}</li>")
            f.write("""</ol></ul>""")
        f.write("""</ol></body></html>""")
