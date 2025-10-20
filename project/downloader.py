#!/usr/bin/env python3
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

import requests
import yt_dlp
from requests.exceptions import HTTPError, RequestException, Timeout
from yt_dlp.utils import DownloadError, ExtractorError

from project.structs import Anime, AnimeList, ThemeSong


class DownloadCache:
    """
    Cache manager for tracking downloaded songs.
    """

    def __init__(self, cache_file: str = "download_cache.json"):
        self.cache_file = Path(cache_file)
        self._cache: Dict[str, Dict] = self._load_cache()

    def _load_cache(self) -> Dict:
        """Load the download cache from file."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def _save_cache(self):
        """Save the download cache to file."""
        try:
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(self._cache, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"⚠️  Warning: Could not save download cache: {e}")

    def is_downloaded(self, theme_id: str, output_dir: str) -> bool:
        """Check if a theme has already been downloaded."""
        cache_key = f"{theme_id}_{output_dir}"
        if cache_key in self._cache:
            cached_info = self._cache[cache_key]
            # Check if file still exists
            if os.path.exists(cached_info.get("filepath", "")):
                return True
            else:
                # File doesn't exist, remove from cache
                del self._cache[cache_key]
                self._save_cache()
        return False

    def mark_downloaded(
        self, theme_id: str, output_dir: str, filepath: str, metadata: Dict
    ):
        """Mark a theme as downloaded."""
        cache_key = f"{theme_id}_{output_dir}"
        self._cache[cache_key] = {
            "filepath": filepath,
            "theme_id": theme_id,
            "output_dir": output_dir,
            "timestamp": os.path.getmtime(filepath),
            "metadata": metadata,
        }
        self._save_cache()

    def get_downloaded_files(self, output_dir: str) -> List[Dict]:
        """Get all downloaded files for a specific output directory."""
        return [
            info
            for key, info in self._cache.items()
            if info.get("output_dir") == output_dir
            and os.path.exists(info.get("filepath", ""))
        ]


class AnimeAudioDownloader:
    def __init__(self, anime_list: AnimeList, cache: DownloadCache = None):
        self.anime_list = anime_list
        self.cache = cache or DownloadCache()

    def calculate_track_number(
        self, anime: Anime, track_type: str, theme_index: int
    ) -> int:
        """
        Calculate progressive track number based on position in anime list.

        For example: if anime has 3 OPs and we're downloading ED2, track number = 3 + 2 = 5

        Args:
            anime: The anime object
            track_type: "OPi" or "EDi"
            theme_index: The index within the track type (1-based)

        Returns:
            Progressive track number
        """
        if track_type.startswith("OP"):
            # For OPs, track number is just the OP index
            return theme_index
        elif track_type.startswith("ED"):
            # For EDs, track number is (number of OPs) + ED index
            num_openings = len(anime.opening_themes)
            return num_openings + theme_index
        else:
            return 1

    def find_theme_by_youtube_id(
        self, youtube_id: str
    ) -> Tuple[
        Optional[Anime], Optional[ThemeSong], Optional[str], Optional[int]
    ]:
        """Find theme information by YouTube ID."""
        for anime in self.anime_list.anime:
            for i, theme in enumerate(anime.opening_themes, 1):
                if theme.yt_url and youtube_id in theme.yt_url:
                    track_number = self.calculate_track_number(anime, "OP", i)
                    return anime, theme, f"OP{i}", track_number
            for i, theme in enumerate(anime.ending_themes, 1):
                if theme.yt_url and youtube_id in theme.yt_url:
                    track_number = self.calculate_track_number(anime, "ED", i)
                    return anime, theme, f"ED{i}", track_number
        return None, None, None, None

    def find_theme_by_id(
        self, theme_id: str
    ) -> Tuple[
        Optional[Anime], Optional[ThemeSong], Optional[str], Optional[int]
    ]:
        """Find theme information by theme ID."""
        for anime in self.anime_list.anime:
            for i, theme in enumerate(anime.opening_themes, 1):
                if str(theme.id) == theme_id:
                    track_number = self.calculate_track_number(anime, "OP", i)
                    return anime, theme, f"OP{i}", track_number
            for i, theme in enumerate(anime.ending_themes, 1):
                if str(theme.id) == theme_id:
                    track_number = self.calculate_track_number(anime, "ED", i)
                    return anime, theme, f"ED{i}", track_number
        return None, None, None, None

    def get_all_themes(self) -> List[Tuple[Anime, ThemeSong, str, int]]:
        """Get all themes from the anime list with calculated track numbers."""
        themes = []
        for anime in self.anime_list.anime:
            for i, theme in enumerate(anime.opening_themes, 1):
                track_number = self.calculate_track_number(anime, "OP", i)
                themes.append((anime, theme, f"OP{i}", track_number))
            for i, theme in enumerate(anime.ending_themes, 1):
                track_number = self.calculate_track_number(anime, "ED", i)
                themes.append((anime, theme, f"ED{i}", track_number))
        return themes

    def sanitize_filename(self, name: str) -> str:
        """Sanitize filename to remove invalid characters."""
        return re.sub(r'[<>:"/\\|?*]', "", name)

    def download_album_art(self, picture_url: str) -> Optional[str]:
        """Download album art to temporary file."""
        try:
            parsed_url = urlparse(picture_url)
            if not parsed_url.scheme or not parsed_url.netloc:
                raise ValueError(f"Invalid URL format: {picture_url}")

            response = requests.get(picture_url, timeout=10)
            response.raise_for_status()

            content_type = response.headers.get("content-type", "")
            if not content_type.startswith("image/"):
                raise ValueError(
                    f"URL does not point to an image: {content_type}"
                )

            temp_file = tempfile.NamedTemporaryFile(
                suffix=".jpg", delete=False
            )
            temp_file.write(response.content)
            temp_file.close()
            return temp_file.name

        except (RequestException, Timeout, HTTPError) as e:
            print(f"⚠️  Network error downloading album art: {e}")
            return None
        except (ValueError, OSError, IOError) as e:
            print(f"⚠️  Error processing album art: {e}")
            return None

    def extract_youtube_id(self, url: str) -> Optional[str]:
        """Extract YouTube ID from various URL formats."""
        patterns = [
            r"(?:youtube\.com/watch\?v=|youtu\.be/)([^&?/]+)",
            r"youtube\.com/embed/([^&?/]+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def download_theme(
        self, theme_identifier: str, output_dir: str = ".", force: bool = False
    ) -> bool:
        """
        Download a theme by YouTube ID or theme ID.

        Args:
            theme_identifier: YouTube ID, YouTube URL, or theme ID
            output_dir: Directory to save the file
            force: Force re-download even if cached

        Returns:
            bool: True if successful
        """
        # Determine if it's a YouTube ID/URL or theme ID
        youtube_id = None
        theme_id = None

        # Check if it's a YouTube URL
        if "youtube.com" in theme_identifier or "youtu.be" in theme_identifier:
            youtube_id = self.extract_youtube_id(theme_identifier)
        elif len(theme_identifier) == 11:  # Typical YouTube ID length
            youtube_id = theme_identifier
        else:
            # Assume it's a theme ID
            theme_id = theme_identifier

        # Find theme information
        if youtube_id:
            anime, theme, track_type, track_number = (
                self.find_theme_by_youtube_id(youtube_id)
            )
        else:
            anime, theme, track_type, track_number = self.find_theme_by_id(
                theme_id
            )

        if not anime or not theme:
            print(f"❌ No metadata found for: {theme_identifier}")
            return False

        # Check cache
        if not force and self.cache.is_downloaded(str(theme.id), output_dir):
            print(
                f"✅ Already downloaded: {anime.title} {track_type} - {theme.name}"
            )
            return True

        return self._download_theme_file(
            anime, theme, track_type, track_number, output_dir
        )

    def _download_theme_file(
        self,
        anime: Anime,
        theme: ThemeSong,
        track_type: str,
        track_number: int,
        output_dir: str,
    ) -> bool:
        """Download and process a single theme file."""
        # Create filename
        safe_anime = self.sanitize_filename(anime.title)
        safe_title = self.sanitize_filename(theme.name.strip('"'))
        filename_base = f"{safe_anime} - {track_type} - {safe_title}"
        filename = f"{filename_base}.%(ext)s"

        # YouTube URL
        youtube_url = theme.yt_url
        if not youtube_url:
            print(f"❌ No YouTube URL for: {anime.title} {track_type}")
            return False

        # Download options
        ydl_opts = {
            "format": "bestaudio[ext=m4a]/bestaudio/best",
            "outtmpl": f"{output_dir}/{filename}",
            "writethumbnail": False,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "m4a",
                    "preferredquality": "0",
                }
            ],
            "postprocessor_args": [],
        }

        try:
            print(f"🎵 {anime.title} {track_type} - {theme.name}")
            print(f"🎤 {theme.artist}")
            print(f"🔢 Track number: {track_number}")

            # Download audio file
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=True)
                original_filename = ydl.prepare_filename(info)
                m4a_filename = os.path.splitext(original_filename)[0] + ".m4a"

            # Add metadata and album art
            if os.path.exists(m4a_filename):
                success = self._add_metadata(
                    m4a_filename, anime, theme, track_type, track_number
                )
                if success:
                    # Add to cache
                    metadata = {
                        "anime_title": anime.title,
                        "theme_name": theme.name,
                        "artist": theme.artist,
                        "track_type": track_type,
                        "track_number": track_number,
                        "theme_id": theme.id,
                    }
                    self.cache.mark_downloaded(
                        str(theme.id), output_dir, m4a_filename, metadata
                    )
                    print("✅ Download completed!")
                    return True
                else:
                    # Clean up failed download
                    try:
                        os.remove(m4a_filename)
                    except OSError:
                        pass
                    return False

            return False

        except (DownloadError, ExtractorError) as e:
            print(f"❌ YouTube download error: {e}")
            return False
        except OSError as e:
            print(f"❌ File system error: {e}")
            return False
        except KeyboardInterrupt:
            print("❌ Download interrupted by user")
            return False

    def _add_metadata(
        self,
        m4a_file: str,
        anime: Anime,
        theme: ThemeSong,
        track_type: str,
        track_number: int,
    ) -> bool:
        """Add metadata and album art to the audio file."""
        temp_output = None
        try:
            temp_output = m4a_file + ".temp.m4a"

            comment = f"{anime.title} - {track_type} - {theme.name.strip('"')} - {theme.artist}"

            # Build FFmpeg command
            cmd = ["ffmpeg", "-i", m4a_file]

            # Add album art if available
            album_art_path = None
            if anime.picture:
                album_art_path = self.download_album_art(anime.picture)
                if album_art_path:
                    cmd.extend(["-i", album_art_path])
                    cmd.extend(
                        [
                            "-map",
                            "0:0",
                            "-map",
                            "1:0",
                            "-c",
                            "copy",
                            "-disposition:v",
                            "attached_pic",
                        ]
                    )
                    print("🖼️  Embedding album art")

            if not album_art_path:
                cmd.extend(["-map", "0:0", "-c", "copy"])

            # Add metadata
            metadata = {
                "title": theme.name.strip('"'),
                "artist": theme.artist,
                "album": anime.title,
                "genre": "Anime",
                "comment": comment,
                "track": str(track_number),
            }

            for key, value in metadata.items():
                if value:
                    cmd.extend(["-metadata", f"{key}={value}"])

            cmd.append(temp_output)

            # Run FFmpeg
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
                check=False,
            )

            if result.returncode == 0:
                os.replace(temp_output, m4a_file)
                temp_output = None
                print("📝 Metadata added successfully")

                # Clean up album art
                if album_art_path and os.path.exists(album_art_path):
                    try:
                        os.unlink(album_art_path)
                    except OSError:
                        pass

                return True
            else:
                print(f"⚠️  Failed to add metadata: {result.stderr}")
                return False

        except (subprocess.SubprocessError, OSError) as e:
            print(f"⚠️  Error during metadata addition: {e}")
            return False
        finally:
            if temp_output and os.path.exists(temp_output):
                try:
                    os.remove(temp_output)
                except OSError:
                    pass

    def download_all_themes(
        self, output_dir: str = ".", force: bool = False
    ) -> Dict[str, int]:
        """
        Download all themes from the anime list.

        Returns:
            Dict with success and failure counts
        """
        themes = self.get_all_themes()
        results = {"success": 0, "failed": 0, "skipped": 0}

        print(f"🎵 Processing {len(themes)} themes...")

        for i, (anime, theme, track_type, track_number) in enumerate(
            themes, 1
        ):
            print(f"\n--- [{i}/{len(themes)}] ---")

            # Check cache
            if not force and self.cache.is_downloaded(
                str(theme.id), output_dir
            ):
                print(
                    f"✅ Skipped (cached): {anime.title} {track_type} - {theme.name}"
                )
                results["skipped"] += 1
                continue

            if self._download_theme_file(
                anime, theme, track_type, track_number, output_dir
            ):
                results["success"] += 1
            else:
                results["failed"] += 1

        return results

    def download_multiple(
        self,
        identifiers: List[str],
        output_dir: str = ".",
        force: bool = False,
    ) -> Dict[str, int]:
        """Download multiple themes by their identifiers."""
        results = {"success": 0, "failed": 0, "skipped": 0}

        for identifier in identifiers:
            print(f"\n--- Processing: {identifier} ---")
            if self.download_theme(identifier, output_dir, force):
                results["success"] += 1
            else:
                results["failed"] += 1

        return results


def main():
    if len(sys.argv) < 3:
        print("Usage:")
        print(
            "  Download single: python downloader.py <IDENTIFIER> <ANIME_LIST_JSON> [output_dir] [--force]"
        )
        print(
            "  Download batch: python downloader.py --batch <ID1,ID2,...> <ANIME_LIST_JSON> [output_dir] [--force]"
        )
        print(
            "  Download all:   python downloader.py --all <ANIME_LIST_JSON> [output_dir] [--force]"
        )
        print("\nIDENTIFIER can be: YouTube ID, YouTube URL, or theme ID")
        sys.exit(1)

    try:
        # Parse arguments
        force = "--force" in sys.argv
        args = [arg for arg in sys.argv[1:] if arg != "--force"]

        if args[0] == "--all":
            json_file = args[1]
            output_dir = args[2] if len(args) > 2 else "."
            mode = "all"
        elif args[0] == "--batch":
            identifiers = args[1].split(",")
            json_file = args[2]
            output_dir = args[3] if len(args) > 3 else "."
            mode = "batch"
        else:
            identifier = args[0]
            json_file = args[1]
            output_dir = args[2] if len(args) > 2 else "."
            mode = "single"

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Load anime list
        with open(json_file, "r", encoding="utf-8") as f:
            anime_list_data = json.load(f)
            anime_list = AnimeList.json_decode(anime_list_data)

        # Initialize downloader with cache
        cache_file = os.path.join(output_dir, "download_cache.json")
        cache = DownloadCache(cache_file)
        downloader = AnimeAudioDownloader(anime_list, cache)

        # Execute based on mode
        if mode == "all":
            print("🚀 Downloading all themes...")
            results = downloader.download_all_themes(output_dir, force)
        elif mode == "batch":
            print(f"🚀 Downloading {len(identifiers)} themes...")
            results = downloader.download_multiple(
                identifiers, output_dir, force
            )
        else:  # single
            success = downloader.download_theme(identifier, output_dir, force)
            results = {
                "success": 1 if success else 0,
                "failed": 0 if success else 1,
                "skipped": 0,
            }

        # Print summary
        print(f"\n🎉 Download Summary:")
        print(f"   ✅ Successful: {results['success']}")
        print(f"   ❌ Failed: {results['failed']}")
        if "skipped" in results:
            print(f"   ⏭️  Skipped (cached): {results['skipped']}")

        if results["failed"] > 0:
            sys.exit(1)

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
