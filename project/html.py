from urllib.parse import quote

from project.myanimelist import AnimeList, MALConstants
from project.util import f7, init_firefox
from project.youtube import YTConstants, yt_search


def html_encode_raw(
    username: str, anime_list: list[tuple[str, str]], n: int
) -> None:
    """
    Function to encode HTML file.

    Parameters
    ----------
    username : str
        User's MyAnimeList username.
    anime_list : list[tuple[str, str]]
        Output of `mal_search`.
    n : int
        How many of the YouTube search results will be saved in the HTML file.
    """
    with open(f"anime_playlist_{username}.html", "w", encoding="utf-8") as f:
        f.write(
            f"""<!DOCTYPE html><html><head><title>Anime playlist {username}"""
            + f"""</title></head><body><h1><a href="{MALConstants.url_list}"""
            + f"""{username}{MALConstants.url_list_arguments}">"""
            + f"""Anime playlist {username}</a></h1><ol>"""
        )
        k = len(anime_list)
        j = 0
        for anime in anime_list:
            j += 1
            print(f"({j}/{k}) {anime[1]}")
            f.write(
                f"""<li><a href="{MALConstants.url}"""
                + f"""{anime[0]}">{anime[1]}</a></li>"""
                + f"""<ul><li><a href="{YTConstants.url_search}"""
                + f"""{quote(anime[1])}+OP">OP</a></li><ul>"""
            )
            videos = f7(yt_search(anime[1], suffix="OP"))
            for i in range(min(n, len(videos))):
                f.write(f"""<li><a href="{videos[i]}">{videos[i]}</a></li>""")
            f.write(
                f"""</ul><li><a href="{YTConstants.url_search}"""
                + f"""{quote(anime[1])}+ED">ED</a></li><ul>"""
            )
            videos = f7(yt_search(anime[1], suffix="ED"))
            for i in range(min(n, len(videos))):
                f.write(f"""<li><a href="{videos[i]}">{videos[i]}</a></li>""")
            f.write("""</ul></ul>""")
        f.write("""</ol></body></html>""")


def html_encode(username: str) -> None:
    """
    Function to encode HTML file.

    Parameters
    ----------
    username : str
        User's MyAnimeList username.
    """
    driver = init_firefox()
    anime_list = AnimeList(username, driver)

    with open(f"anime_playlist_{username}.html", "w", encoding="utf-8") as f:
        f.write(
            f"""<!DOCTYPE html><html><head><title>Anime playlist {username}"""
            + f"""</title></head><body><h1><a href="{MALConstants.url_list}"""
            + f"""{username}{MALConstants.url_list_arguments}">"""
            + f"""Anime playlist {username}</a></h1><ol>"""
        )
        k = len(anime_list.anime)
        j = 0
        for anime in anime_list.anime:
            j += 1
            print(
                f"({j:0{len(str(k))}d}/{k}) "
                + f"[YT] Searching theme songs: {anime.name}"
            )
            f.write(
                f"""<li><a href="{MALConstants.url}"""
                + f"""{anime.url}">{anime.name}</a></li>"""
                + """<ul><li>Opening Theme</li><ol>"""
            )
            for opening in anime.songs.openings:
                videos = f7(yt_search(f"{opening.name} {opening.artist}"))
                if videos:
                    f.write(
                        f"""<li><a href="{videos[0]}">{opening.name} """
                        + f"""by {opening.artist} {opening.episode}</a></li>"""
                    )
            f.write("""</ol><li>Ending Theme</a></li><ol>""")
            for ending in anime.songs.endings:
                videos = f7(yt_search(f"{ending.name} {ending.artist}"))
                if videos:
                    f.write(
                        f"""<li><a href="{videos[0]}">{ending.name} """
                        + f"""by {ending.artist} {ending.episode}</a></li>"""
                    )
            f.write("""</ol></ul>""")
        f.write("""</ol></body></html>""")

    # Close the browser
    driver.quit()
