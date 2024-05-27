import re
import time
import urllib.request
from typing import Any
from urllib.parse import quote

from selenium import webdriver


def f7(seq: list[Any]) -> list[Any]:
    """
    Function to remove duplicates in list while maintaining order.

    Parameters
    ----------
    seq : list[Any]

    Returns
    -------
    list[Any]

    See Also
    --------
    Source of the code: https://www.peterbe.com/plog/uniqifiers-benchmark
    """
    seen: set[Any] = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def yt_search(search_str: str, suffix: str = "") -> list[str]:
    """
    Perform YouTube search.

    Parameters
    ----------
    search_str : str
        Search query, can contain spaces and other unicode chars.
    suffix : str
        Suffix appended to search query.

    Returns
    -------
    list[str]
        List of search results URLs by order of search result.
    """
    # Encode str to URL
    search_keyword = quote(search_str)
    if suffix:
        search_keyword += f"+{suffix}"
    # Perform Youtube search
    try:
        html = urllib.request.urlopen(
            "https://www.youtube.com/results?search_query=" + search_keyword
        )
        video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
        return [
            "https://www.youtube.com/watch?v=" + video_id
            for video_id in video_ids
        ]
    # YouTube search failed
    except urllib.request.HTTPError:
        return []


def mal_search(username: str) -> list[tuple[str, str]]:
    """
    Retrieve User's MyAnimeList.

    Parameters
    ----------
    username : str
        User's MyAnimeList username.

    Returns
    -------
    list[tuple[str, str]]
        List of entries in anime list. Each entry contains the
        MyAnimeList anime page URL and the anime title.
    """
    # Initialize a headless Firefox browser
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)

    # Load the MAL page
    driver.get(
        f"https://myanimelist.net/animelist/{username}?order=-5&status=2"
    )

    # Scroll to the bottom of the page multiple times
    num_scrolls = 10
    for _ in range(num_scrolls):
        # Scroll to the bottom of the page
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);"
        )
        # Wait for some time to let content load
        time.sleep(2)

    # Regular expression to match the anchor tags and extract href and title
    pattern = r'<a href="(/anime/\d+/[^"]+)" class="link sort">([^<]+)</a>'

    # Extract anime titles
    anime_list = re.findall(pattern, driver.page_source)

    # Close the browser
    driver.quit()

    return anime_list


def html_encode(
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
            """<!DOCTYPE html><html><head><title>"""
            + f"""Anime playlist {username}</title></head><body>"""
            + f"""<h1><a href="https://myanimelist.net/animelist/{username}?"""
            + f"""order=-5&status=2">Anime playlist {username}</a></h1><ol>"""
        )
        k = len(anime_list)
        j = 0
        for anime in anime_list:
            j += 1
            print(f"({j}/{k}) {anime[1]}")
            f.write(
                """<li><a href="https://myanimelist.net"""
                + f"""{anime[0]}">{anime[1]}</a></li>"""
                + """<ul><li><a href="https://www.youtube.com/results?"""
                + f"""search_query={quote(anime[1])}+OP">OP</a></li><ul>"""
            )
            videos = f7(yt_search(anime[1], suffix="OP"))
            for i in range(min(n, len(videos))):
                f.write(f"""<li><a href="{videos[i]}">{videos[i]}</a></li>""")
            f.write(
                """</ul><li><a href="https://www.youtube.com/results?"""
                + f"""search_query={quote(anime[1])}+ED">ED</a></li><ul>"""
            )
            videos = f7(yt_search(anime[1], suffix="ED"))
            for i in range(min(n, len(videos))):
                f.write(f"""<li><a href="{videos[i]}">{videos[i]}</a></li>""")
            f.write("""</ul></ul>""")
        f.write("""</ol></body></html>""")


if __name__ == "__main__":
    name = "mik2003"
    titles = mal_search(name)
    html_encode(name, titles, 3)
