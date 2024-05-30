import re
import urllib.request
from dataclasses import dataclass
from urllib.parse import quote


@dataclass(frozen=True)
class YTConstants:
    url_result = "https://www.youtube.com/results?"
    url_search = "https://www.youtube.com/results?search_query="


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
    print(f"[YT] Searching theme song '{search_str}'...")

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
