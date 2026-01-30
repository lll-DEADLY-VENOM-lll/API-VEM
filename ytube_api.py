# ---------------------------------------------------------------
# 🔸 Shashank YT-API Project
# 🔹 Developed & Maintained by: Shashank Shukla (https://github.com/itzshukla)
# 📅 Copyright © 2025 – All Rights Reserved
#
# 📖 License:
# This source code is open for educational and non-commercial use ONLY.
# You are required to retain this credit in all copies or substantial portions of this file.
# Commercial use, redistribution, or removal of this notice is strictly prohibited
# without prior written permission from the author.
#
# ❤️ Made with dedication and love by ItzShukla
# ---------------------------------------------------------------

import os
import yt_dlp
import aiohttp
import asyncio
from typing import Optional, List, Dict
from youtubesearchpython.__future__ import VideosSearch

COOKIE_FILE = "cookies1.txt"  # optional


class DownloadLink:
    def __init__(self, url: str):
        self.url = url


class Ytube:
    def __init__(self):
        self.download_dir = "downloads"
        os.makedirs(self.download_dir, exist_ok=True)

    async def search_videos(self, query: str) -> Optional[List[Dict]]:
        """Search YouTube and return top result info."""
        try:
            results = await VideosSearch(query, limit=1).next()
            if results.get("result"):
                v = results["result"][0]
                return [{
                    "id": v.get("id"),
                    "title": v.get("title"),
                    "duration": v.get("duration"),
                    "viewCount": v.get("viewCount", {}).get("short"),
                    "thumbnails": v.get("thumbnails"),
                    "channel": v.get("channel", {}).get("name"),
                    "link": v.get("link")
                }]
        except Exception as e:
            print(f"[search_videos warning] {e}")

        try:
            info = await self.get_video_info(query)
            if info:
                return [{
                    "id": info.get("id"),
                    "title": info.get("title"),
                    "duration": info.get("duration_string"),
                    "viewCount": info.get("view_count"),
                    "thumbnails": [{"url": info.get("thumbnail")}],
                    "channel": info.get("uploader"),
                    "link": f"https://www.youtube.com/watch?v={info.get('id')}"
                }]
        except Exception as e:
            print(f"[search_videos fallback error] {e}")

        return None

    async def get_video_info(self, url_or_id: str) -> Optional[Dict]:
        """Accurate metadata using yt-dlp."""
        if len(url_or_id) == 11 and "http" not in url_or_id:
            url_or_id = f"https://www.youtube.com/watch?v={url_or_id}"

        ydl_opts = {
            "quiet": True,
            "noplaylist": True,
            "skip_download": True,
        }
        if os.path.exists(COOKIE_FILE):
            ydl_opts["cookiefile"] = COOKIE_FILE

        try:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self._extract_info_sync, url_or_id, ydl_opts)
        except Exception as e:
            print(f"[get_video_info error] {e}")
            return None

    def _extract_info_sync(self, url: str, opts: Dict):
        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(url, download=False)

    def get_download_link(
        self,
        item: Dict,
        format: str = "mp3",
        quality: str = "320",
        use_cookies: bool = False
    ) -> Optional[DownloadLink]:
        """Return a direct media URL."""
        url = item.get("link") or f"https://www.youtube.com/watch?v={item.get('id')}"
        ydl_opts = {
            "quiet": True,
            "noplaylist": True,
            "skip_download": True,
            "extract_flat": False,
            "force_generic_extractor": False,
            "outtmpl": os.path.join(self.download_dir, "%(id)s.%(ext)s"),
        }
        if use_cookies and os.path.exists(COOKIE_FILE):
            ydl_opts["cookiefile"] = COOKIE_FILE

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                formats = info.get("formats", [])

                if format == "mp3":
                    audio_formats = [
                        f for f in formats
                        if f.get("acodec") != "none" and f.get("url")
                    ]
                    def audio_key(f):
                        ext_pref = 1 if f.get("ext") == "m4a" else 0
                        abr_val = f.get("abr") or 0  # Fix None bug
                        return (ext_pref, abr_val)
                    audio_formats.sort(key=audio_key, reverse=True)
                    if audio_formats:
                        return DownloadLink(audio_formats[0]["url"])

                elif format == "mp4":
                    prog = [
                        f for f in formats
                        if f.get("vcodec") != "none" and f.get("acodec") != "none"
                        and f.get("ext") == "mp4" and f.get("url")
                    ]
                    prog.sort(key=lambda x: x.get("height") or 0, reverse=True)
                    if prog:
                        return DownloadLink(prog[0]["url"])

                    mp4_video_only = [
                        f for f in formats
                        if f.get("vcodec") != "none" and f.get("ext") == "mp4" and f.get("url")
                    ]
                    mp4_video_only.sort(key=lambda x: x.get("height") or 0, reverse=True)
                    if mp4_video_only:
                        return DownloadLink(mp4_video_only[0]["url"])

        except Exception as e:
            print(f"[get_download_link error] {e}")

        return None