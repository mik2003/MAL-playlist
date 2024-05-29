from project.animelist import AnimeList
from project.malapi import MALAPI
from project.youtube import yt_search


def html_encode(username: str) -> None:
    """
    Function to encode HTML file.

    Parameters
    ----------
    username : str
        User's MyAnimeList username.
    """
    anime_list = AnimeList(username)

    with open(f"anime_playlist_{username}.html", "w", encoding="utf-8") as f:
        f.write(
            f"""<!DOCTYPE html><html><head><title>Anime playlist {username}"""
            + """</title></head><body><h1>"""
            + f"""<a href="{MALAPI.url_animelist.format(username)}">"""
            + f"""Anime playlist {username}</a></h1><ol>"""
        )
        n = len(anime_list.anime)
        i = 0
        for anime in anime_list.anime:
            i += 1
            print(
                f"({i:0{len(str(n))}d}/{n}) "
                + f"[YT] Searching theme songs: {anime.title}"
            )
            f.write(
                f"""<li><a href="{MALAPI.url_anime.format(anime.id)}">"""
                + f"""{anime.title}</a></li>"""
                + """<ul><li>Opening Theme</li><ol>"""
            )
            for opening in anime.opening_themes:
                videos = yt_search(f"{opening.name} {opening.artist}")
                if videos:
                    f.write(
                        f"""<li><a href="{videos[0]}">{opening.name} """
                        + f"""by {opening.artist} {opening.episode}</a></li>"""
                    )
            f.write("""</ol><li>Ending Theme</a></li><ol>""")
            for ending in anime.ending_themes:
                videos = yt_search(f"{ending.name} {ending.artist}")
                if videos:
                    f.write(
                        f"""<li><a href="{videos[0]}">{ending.name} """
                        + f"""by {ending.artist} {ending.episode}</a></li>"""
                    )
            f.write("""</ol></ul>""")
        f.write("""</ol></body></html>""")
