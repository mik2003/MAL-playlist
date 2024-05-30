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
            + """</title><style>
                /* Light mode */
                @media (prefers-color-scheme: light) {
                    :root {
                        --body-bg: #FFFFFF;
                        --body-color: #000000;
                    }
                }

                /* Dark mode */
                @media (prefers-color-scheme: dark) {
                    :root {
                        --body-bg: #000000;
                        --body-color: #FFFFFF;
                    }
                }

                body {
                    background: var(--body-bg);
                    color: var(--body-color);
                }
                ol.anime-list {
                    counter-reset: anime-counter;
                    margin-left: -30px;
                }
                li.anime-item {
                    display: flex;
                    align-items: flex-start;
                    margin-bottom: 20px;
                    counter-increment: anime-counter;
                }
                .anime-content {
                    display: flex;
                    align-items: flex-start;
                }
                .anime-content img {
                    margin-right: 15px;
                    float: left;
                    display: block;
                    overflow: hidden;
                }
                .anime-details {
                    flex: 1;
                }
                .anime-details::before {
                    content: "[" counter(anime-counter) "]";
                    font-weight: bold;
                    margin-right: 10px;
                }
                .anime-details ul {
                    margin: 0;
                    padding-left: 20px;
                }
                </style></head><body><h1>"""
            + f"""<a href="{MALAPI.url_animelist.format(username)}">"""
            + f"""Anime playlist {username}</a></h1><ol class="anime-list">"""
        )
        for anime in anime_list.anime:
            f.write(
                """<li class="anime-item"><div class="anime-content"><img sr"""
                + f"""c="{anime.picture}" alt="{anime.title}" width="100">"""
                + """<div class="anime-details"><a href"""
                f"""="{MALAPI.url_anime.format(anime.id)}", """
                + f"""style="font-weight: bold;">{anime.title}</a>"""
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
            f.write("""</ol><li>Ending Theme</li><ol>""")
            for ending in anime.ending_themes:
                li_content = (
                    (f'<a href="{ending.url[0]}">' if ending.url else "")
                    + f'"{ending.name}"'
                    + (f" by {ending.artist}" if ending.artist else "")
                    + (f" ({ending.episode})" if ending.episode else "")
                    + ("</a>" if ending.url else "")
                )
                f.write(f"<li>{li_content}</li>")
            f.write("""</ol></li></ul></div></div></li>""")
        f.write("""</ol></body></html>""")
