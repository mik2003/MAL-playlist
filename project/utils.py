import json
import os
import time
from dataclasses import dataclass
from typing import Any, Dict

import requests


def json_read(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@dataclass(frozen=True)
class Cache:
    anime = os.path.join("project", "cache", "anime", "{}.json")
    animethemes = os.path.join("project", "cache", "animethemes", "{}.json")

    @staticmethod
    def retrieve_anime(anime_id: str) -> Dict[str, Any]:
        filepath = Cache.anime.format(anime_id)
        if not os.path.exists(filepath):
            Cache.update_anime(anime_id)
        return json_read(filepath)

    @staticmethod
    def retrieve_animethemes(anime_id: str) -> Dict[str, Any]:
        filepath = Cache.animethemes.format(anime_id)
        if not os.path.exists(filepath):
            Cache.update_animethemes(anime_id)
        return json_read(filepath)

    @staticmethod
    def update_anime(
        anime_id: str,
    ) -> None:
        with open(Cache.anime.format(anime_id), "w", encoding="utf-8") as f:
            json.dump(API.MAL.retrieve_anime(anime_id), f)

    @staticmethod
    def update_animethemes(
        anime_id: str,
    ) -> None:
        with open(
            Cache.animethemes.format(anime_id), "w", encoding="utf-8"
        ) as f:
            json.dump(API.AT.retrieve_anime(anime_id), f)


@dataclass(frozen=True)
class API:
    # Sleep time between API calls [s]
    sleep_time = 0.1

    @dataclass(frozen=True)
    class MAL:
        endpoint_v2 = "https://api.myanimelist.net/v2"
        keys = os.path.join("project", ".secret", "mal_api.json")
        anime = "/anime/{}?fields=opening_themes,ending_themes"

        @staticmethod
        def params_client_id() -> dict[str, str]:
            keys = json_read(API.MAL.keys)
            client_id = keys["Client_ID"]
            params = {"X-MAL-CLIENT-ID": client_id}

            return params

        @staticmethod
        def retrieve_anime(anime_id: str) -> Dict[str, Any]:
            r = requests.get(
                API.MAL.endpoint_v2 + API.MAL.anime.format(anime_id),
                headers=API.MAL.params_client_id(),
                timeout=10,
            )
            time.sleep(API.sleep_time)
            if r.status_code == 200:
                return r.json()
            else:
                raise requests.HTTPError(r.status_code)

    @dataclass(frozen=True)
    class AT:
        enpoint_anime = "https://api.animethemes.moe/anime"

        @staticmethod
        def params_mal_anime_id(anime_id: str) -> Dict[str, str]:
            return {
                "filter[has]": "resources",
                "filter[site]": "MyAnimeList",
                "filter[external_id]": anime_id,
                "fields[anime]": "id,name",
                "include": "animethemes,animethemes.animethemeentries,animethemes.animethemeentries.videos",
            }

        @staticmethod
        def retrieve_anime(anime_id: str) -> Dict[str, Any]:
            r = requests.get(
                API.AT.enpoint_anime,
                params=API.AT.params_mal_anime_id(anime_id),
                timeout=2000,
            )
            time.sleep(API.sleep_time)
            if r.status_code == 200:
                return r.json()["anime"][0]
            else:
                raise requests.HTTPError(r.status_code)


if __name__ == "__main__":
    mal_id = "37450"
    print(Cache.retrieve_anime(mal_id))
