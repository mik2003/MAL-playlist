import datetime
import json
import os
import time
from dataclasses import dataclass
from typing import Any

import requests


@dataclass(frozen=True)
class MALAPI:
    keys = os.path.join("project", ".secret", "mal_api.json")

    v2 = "https://api.myanimelist.net/v2"
    animelist = (
        "/users/{}/animelist?offset={}"
        + "&status=completed&sort=list_updated_at&limit=100"
    )
    anime = "/anime/{}?fields=opening_themes,ending_themes"
    animelist_cache = os.path.join(
        "project", "cache", "animelist", "{}_{}.json"
    )
    anime_cache = os.path.join("project", "cache", "anime", "{}.json")
    log = os.path.join("project", "log", "{}.log")

    # Sleep time between API calls [s]
    sleep_time = 0.1


def get_keys(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    keys = get_keys(MALAPI.keys)
    client_id = keys["Client_ID"]
    headers = {"X-MAL-CLIENT-ID": client_id}

    user_name = "MysticReaction"
    offset = 300

    # Set log to None to print to the console instead
    log = open(
        MALAPI.log.format(
            datetime.datetime.now().strftime(f"{user_name}_%Y_%m_%d_%H_%M_%S")
        ),
        "w",
        encoding="utf-8",
    )

    t_0 = time.time()

    if os.path.exists(MALAPI.animelist_cache.format(user_name, offset)):
        print(
            f"Retrieving {user_name} anime list "
            + f"(offset={offset}) from cache...",
            file=log,
        )
        with open(
            MALAPI.animelist_cache.format(user_name, offset),
            "r",
            encoding="utf-8",
        ) as animelist_file:
            anime_list = json.load(animelist_file)
    else:
        print(
            f"Retrieving {user_name} anime list "
            + f"(offset={offset}) from MyAnimeList...",
            file=log,
        )
        r = requests.get(
            MALAPI.v2 + MALAPI.animelist.format(user_name, offset),
            headers={"X-MAL-CLIENT-ID": client_id},
            timeout=10,
        )
        time.sleep(MALAPI.sleep_time)
        if r.status_code == 200:
            print(
                f"Caching {user_name} anime list (offset={offset})...",
                file=log,
            )
            with open(
                MALAPI.animelist_cache.format(user_name, offset),
                "w",
                encoding="utf-8",
            ) as animelist_file:
                animelist_file.write(r.text)
            anime_list = r.json()
        else:
            print(
                f"Retrieval of {user_name} anime list "
                + f"(offset={offset}) failed: {r.status_code}",
                file=log,
            )

    for anime in anime_list["data"]:
        anime_node = anime["node"]
        anime_id = anime_node["id"]
        anime_title = anime_node["title"]

        if os.path.exists(MALAPI.anime_cache.format(anime_id)):
            print(
                f"Retrieving '{anime_title}' information from cache...",
                file=log,
            )
            with open(
                MALAPI.anime_cache.format(anime_id),
                "r",
                encoding="utf-8",
            ) as anime_file:
                anime_data = json.load(anime_file)
        else:
            print(
                f"Retrieving '{anime_title}' information from MyAnimeList...",
                file=log,
            )
            r = requests.get(
                MALAPI.v2 + MALAPI.anime.format(anime_id),
                headers={"X-MAL-CLIENT-ID": client_id},
                timeout=10,
            )
            time.sleep(MALAPI.sleep_time)
            if r.status_code == 200:
                print(f"Caching '{anime_title}' information...", file=log)
                with open(
                    MALAPI.anime_cache.format(anime_id),
                    "w",
                    encoding="utf-8",
                ) as anime_file:
                    anime_file.write(r.text)
                anime_data = r.json()
            else:
                print(
                    f"Retrieval of '{anime_title}' information failed: "
                    + f"{r.status_code}",
                    file=log,
                )

    print(f"Program finished in {time.time()-t_0:.3f} s.", file=log)

    if log:
        log.close()
