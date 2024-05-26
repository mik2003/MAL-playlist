import re
import urllib.request
from typing import Any


def f7(seq: list[Any]) -> list[Any]:
    seen: set[Any] = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def yt_search(search_str: str, suffix: str = "") -> list[str]:
    search_keyword = search_str.replace(" ", "+")
    if suffix:
        search_keyword += f"+{suffix}"
    html = urllib.request.urlopen(
        "https://www.youtube.com/results?search_query=" + search_keyword
    )
    video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
    return [
        "https://www.youtube.com/watch?v=" + video_id for video_id in video_ids
    ]


def mal_search(username: str) -> list[str]:
    html = urllib.request.urlopen(
        f"https://myanimelist.net/animelist/{username}"
    )
    video_titles = re.findall(
        r"anime_title&quot;:&quot;(.*?)&quot;", html.read().decode()
    )
    return video_titles


def anime_dict(anime_list: list[str]) -> dict[str, list[str]]:
    out = {}
    for anime in anime_list:
        out[anime] = yt_search(anime)
    return out


def html_encode(filename: str, anime_list: list[str], n: int) -> None:
    out = """<!DOCTYPE html><html><head></head><body>"""
    for anime in anime_list:
        print(anime)
        out += f"""{anime}<ul>"""
        out += (
            """<li><a href="https://www.youtube.com/results?search_query="""
            f"""{anime.replace(" ", "+")}+OP">OP</a></li><ul>"""
        )
        videos = f7(yt_search(anime, suffix="OP"))
        for i in range(min(n, len(videos))):
            out += f"""<li><a href="{videos[i]}">{videos[i]}</a></li>"""
        out += """</ul>"""
        out += (
            """<li><a href="https://www.youtube.com/results?search_query="""
            f"""{anime.replace(" ", "+")}+ED">ED</a></li><ul>"""
        )
        videos = f7(yt_search(anime, suffix="ED"))
        for i in range(min(n, len(videos))):
            out += f"""<li><a href="{videos[i]}">{videos[i]}</a></li>"""
        out += """</ul></ul>"""
    out += """</body></html>"""

    with open(filename, "w", encoding="utf-8") as f:
        f.write(out)


if __name__ == "__main__":
    # print(
    #     yt_search(
    #         "Dungeon ni Deai wo Motomeru no wa Machigatteiru Darou ka III OP"
    #     )
    # )

    titles = mal_search("mik2003")
    html_encode("list.html", titles, 3)
