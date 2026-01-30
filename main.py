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

import json
import os
import logging
import requests
import asyncio
import aiohttp
from fastapi import FastAPI, Query, Request, HTTPException, Body
from fastapi.responses import StreamingResponse, HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from ytube_api import Ytube
from mongocache import get_cached_file, save_cached_file
from mongocache import get_all_files, delete_cached_file
from pyrogram import Client, filters
from pyrogram.types import Message
import httpx
from datetime import datetime, timedelta
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor
from bots.externalapi import *
from bots.eternalapi2 import *
from bots.externalapi import download_song as ext_download_song
from bots.eternalapi2 import download_video as ext_download_video
import shutil
import subprocess

API_KEY = "stranger"
ADMIN_KEY = "SHUKLA"
LOG_FILE = "api_requests.log"
LOGS_FILE = "logs.json"
LAST_RESET_FILE = "last_reset.json"
API_ID = 20138139
API_HASH = "ff813495ed17a07723000a9751f4c3ee"
BOT_TOKEN = "7902208475:AAF4zXIU5wxAoR4T1yLoLpa0tMEidEKUvrc"
TOKEN = "7902208475:AAF4zXIU5wxAoR4T1yLoLpa0tMEidEKUvrc"
CACHE_CHANNEL = -1002715601269
WEB_PORT = 8000

os.makedirs("downloads", exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("yt_api")

executor = asyncio.get_event_loop()

app = FastAPI()
yt = Ytube()
templates = Jinja2Templates(directory="templates")

if os.path.isdir("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

pyro_api = Client("api-helper", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
bot_app = Client("music-bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
free_app = Client("free-api", api_id=API_ID, api_hash=API_HASH, bot_token=TOKEN, plugins=dict(root="bots"))

executor = ThreadPoolExecutor(max_workers=3)

def load_logs():
    if os.path.exists(LOGS_FILE):
        try:
            with open(LOGS_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def save_logs():
    try:
        with open(LOGS_FILE, "w") as f:
            json.dump(logs_db, f, indent=2)
    except Exception as e:
        print(f"[ERROR] Failed to save logs: {e}")

def load_last_reset():
    if os.path.exists(LAST_RESET_FILE):
        try:
            with open(LAST_RESET_FILE, "r") as f:
                return json.load(f).get("date")
        except:
            return None
    return None

def save_last_reset(date_str):
    with open(LAST_RESET_FILE, "w") as f:
        json.dump({"date": date_str}, f)

def reset_today_if_needed():
    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    last_reset = load_last_reset()

    if last_reset != today_str:
        global logs_db # FIX: Needed to reassign the global logs_db variable.
        logs_db = [log for log in logs_db if not log["timestamp"].startswith(today_str)]
        save_logs()
        save_last_reset(today_str)
        print("🔄 Today requests reset")

def ensure_file_exists(path):
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        raise HTTPException(status_code=500, detail="Generated file missing or empty")

def safe_stream(file_path, chunk_size=4096):
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk

def has_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False

async def url_stream(url, chunk_size=8192):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                raise HTTPException(status_code=404, detail="Failed to fetch stream")
            while True:
                chunk = await resp.content.read(chunk_size)
                if not chunk:
                    break
                yield chunk

async def remux_if_needed(src_path, dst_path, is_video):
    if not is_video or not has_ffmpeg():
        return src_path

    tmp_out = dst_path + ".part"

    if os.path.exists(tmp_out):
        try:
            os.remove(tmp_out)
        except:
            pass

    try:
        cmd = [
            "ffmpeg",
            "-y",
            "-i", src_path,
            "-c", "copy",
            "-movflags", "+faststart",
            tmp_out,
        ]

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            executor,
            lambda: subprocess.check_call(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        )

        if os.path.exists(tmp_out):
            shutil.move(tmp_out, dst_path)
            return dst_path

        return src_path

    except Exception as e:
        print(f"[remux_if_needed] {e} -> using original")

        if os.path.exists(tmp_out):
            try:
                os.remove(tmp_out)
            except:
                pass

        return src_path

async def download_file_threaded(url, dest_path):

    loop = asyncio.get_event_loop()

    def _download():
        tmp_path = dest_path + ".part"

        os.makedirs(os.path.dirname(dest_path), exist_ok=True)

        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except:
                pass

        resp = requests.get(url, stream=True, timeout=15)
        if resp.status_code != 200:
            raise Exception(f"Download failed with status {resp.status_code}")

        with open(tmp_path, "wb") as f:
            for chunk in resp.iter_content(4096):
                if chunk:
                    f.write(chunk)

        shutil.move(tmp_path, dest_path)

    await loop.run_in_executor(executor, _download)

API_KEYS_FILE = "api_keys.json"

def load_api_keys():
    if os.path.exists(API_KEYS_FILE):
        try:
            with open(API_KEYS_FILE, "r") as f:
                content = f.read().strip()
                if content:
                    return json.loads(content)
        except Exception as e:
            print(f"[ERROR] Failed to load API keys: {e}")

    return [{
        "id": "1",
        "key": API_KEY,
        "name": "Default",
        "created_at": datetime.utcnow().isoformat(),
        "valid_until": (datetime.utcnow() + timedelta(days=9999)).isoformat(),
        "daily_limit": 10000,
        "is_admin": True,
        "count": 0
    }]

def save_api_keys():
    with open(API_KEYS_FILE, "w") as f:
        json.dump(api_keys_db, f, indent=2)

api_keys_db = load_api_keys()
logs_db = load_logs()

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("static/favicon.ico")

def make_caption(video_id, ext):
    return f"yt_{video_id}_{ext}"

async def ensure_pyrogram_running():
    if not pyro_api.is_connected:
        await pyro_api.start()
        await asyncio.sleep(2)

async def ensure_channel_known(client, channel_id):
    try:
        await client.get_chat(channel_id)
    except Exception:
        try:
            await client.send_message(channel_id, "Initializing channel cache")
        except Exception as e:
            print(f"Failed to initialize channel {channel_id}: {e}")
            raise

cache_locks = {}

async def get_cache_lock(video_id, ext):
    key = f"{video_id}_{ext}"
    if key not in cache_locks:
        cache_locks[key] = asyncio.Lock()
    return cache_locks[key]

async def search_cache(video_id, ext):
    try:
        result = get_cached_file(video_id, ext)
        if not result:
            print(f"[search_cache] Not found DB for {video_id}.{ext}")
            return None

        if "message_id" in result:
            try:
                msg = await pyro_api.get_messages(CACHE_CHANNEL, result["message_id"])
                if ext == "mp3" and not getattr(msg, "audio", None):
                    print("[search_cache] Type mismatch: expected audio")
                    return None
                if ext == "mp4" and not getattr(msg, "video", None):
                    print("[search_cache] Type mismatch: expected video")
                    return None
                print(f"[search_cache] Valid cache for {video_id}.{ext}")
                return result
            except Exception as e:
                print(f"[search_cache] TG fetch failed: {e}")
                return None
        return None
    except Exception as e:
        print(f"[search_cache error] {e}")
        return None

async def cache_file_send(file_path, video_id, ext):
    lock = await get_cache_lock(video_id, ext)
    async with lock:
        await ensure_pyrogram_running()
        await ensure_channel_known(pyro_api, CACHE_CHANNEL)
        caption = make_caption(video_id, ext)

        try:
            try:
                old = get_cached_file(video_id, ext)
                if old and "message_id" in old:
                    await pyro_api.delete_messages(CACHE_CHANNEL, old["message_id"])
                    print(f"[cache_file_send] Old cache deleted for {video_id}.{ext}")
            except Exception as e:
                print(f"[cache_file_send] Old cache delete failed (non-fatal): {e}")

            if ext == "mp3":
                sent = await pyro_api.send_audio(CACHE_CHANNEL, file_path, caption=caption)
                file_id = sent.audio.file_id
            else:
                sent = await pyro_api.send_video(CACHE_CHANNEL, file_path, caption=caption)
                file_id = sent.video.file_id

            save_cached_file(video_id, ext, sent.id, file_id)
            print(f"[cache_file_send] Cached {video_id}.{ext} message_id {sent.id}")
            return sent

        except Exception as e:
            print(f"[cache_file_send error] Failed to cache {video_id}.{ext}: {e}")
            raise

        finally:
        
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"[cache_file_send] Temp file deleted: {file_path}")
            except Exception as e:
                print(f"[cache_file_send] Temp delete failed: {e}")

async def background_cache(video_id: str, temp_path: str, ext: str):
    try:
        print(f"[background_cache] Caching {video_id}.{ext}")
        await cache_file_send(temp_path, video_id, ext)
    except Exception as e:
        print(f"[background_cache ERROR] {e}")

async def get_video_metadata(video_id_or_url: str):
    is_youtube_url = (
        "youtu" in video_id_or_url
        or len(video_id_or_url) == 11
    )

    if is_youtube_url:
        url = video_id_or_url

        try:
            if "v=" in url:
                vid = url.split("v=")[-1].split("&")[0]
            else:
                vid = url.rstrip("/").split("/")[-1]
        except Exception:
            vid = video_id_or_url
    else:
        query = f"ytsearch:{video_id_or_url}"
        try:
            results = await yt.search_videos(query)

            if results and len(results) > 0:
                it = results[0]
                vid = it.get("id")

                return {
                    "id": vid,
                    "title": it.get("title", vid),
                    "thumbnail": (
                        ((it.get("thumbnails") or [{}])[0]) or {}
                    ).get("url"),
                    "url": f"https://www.youtube.com/watch?v={vid}"
                }

        except Exception as e:
            print(f"[get_video_metadata] search query failed: {e}")
            return {
                "id": video_id_or_url,
                "title": video_id_or_url,
                "thumbnail": None,
                "url": None
            }

        return {
            "id": video_id_or_url,
            "title": video_id_or_url,
            "thumbnail": None,
            "url": None
        }

    try:
        if hasattr(yt, "get_video_info"):
            info = await yt.get_video_info(vid)

            if info:
                return {
                    "id": vid,
                    "title": info.get("title", vid),
                    "thumbnail": info.get("thumbnail"),
                    "url": f"https://www.youtube.com/watch?v={vid}"
                }

    except Exception as e:
        print(f"[get_video_metadata] get_video_info failed: {e}")

    return {
        "id": vid,
        "title": vid,
        "thumbnail": None,
        "url": f"https://www.youtube.com/watch?v={vid}"
    }

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
COOKIES_FILE = "cookies1.txt"

def download_youtube_video(video_id: str):
    """
    Download YouTube video in MP4 format using yt-dlp.
    Returns: (file_path, video_title)
    """

    final_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.mp4")

    ydl_opts = {
        "format": "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best",
        "merge_output_format": "mp4",
        "outtmpl": final_path,
        "quiet": True,
        "ignoreerrors": True,
        "cookiefile": COOKIES_FILE if os.path.exists(COOKIES_FILE) else None,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(
            f"https://www.youtube.com/watch?v={video_id}",
            download=True
        )

    if not os.path.exists(final_path):
        raise FileNotFoundError("Video not found after download!")

    return final_path, info.get("title", video_id)

def check_api_key(request: Request):
    if request.url.path in ["/", "/status", "/admin"]:
        return

    key = request.headers.get("x-api-key") or request.query_params.get("api_key")
    if not key:
        raise HTTPException(status_code=401, detail="Missing API Key")

    matched_key = next((k for k in api_keys_db if k["key"] == key), None)
    if not matched_key:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    now = datetime.utcnow()
    if datetime.fromisoformat(matched_key["valid_until"]) < now:
        raise HTTPException(status_code=403, detail="API Key expired")

    matched_key["count"] += 1

    logs_db.append({
        "timestamp": now.isoformat(),
        "api_key": key,
        "endpoint": request.url.path,
        "status": 200
    })
    save_logs()

    return key

def check_admin_key(request: Request):
    key = request.query_params.get("admin_key")
    if key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Forbidden: Invalid admin key.")
    return key

async def run_bot():
    await bot_app.start()
    print("✅ Bot started!")
    await bot_app.idle()

async def free_run_bot():
    await free_app.start()
    print("✅ Free bot started!")
    await free_app.idle()

@app.on_event("startup")
async def startup_event():
    reset_today_if_needed()
    try:
        await pyro_api.start()
        print("✅ pyro_api started")
    except Exception as e:
        print(f"❌ Failed to start pyro_api: {e}")
    await asyncio.sleep(2)
    asyncio.create_task(run_bot())
    await asyncio.sleep(3)
    asyncio.create_task(free_run_bot())

@app.on_event("shutdown")
async def shutdown_event():
    await pyro_api.stop()
    await bot_app.stop()
    await free_app.stop()

@app.get("/status")
async def status():
    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    total_requests = len(logs_db)
    today_requests = len([log for log in logs_db if log["timestamp"].startswith(today_str)])
    return {
        "total_requests": total_requests,
        "today_requests": today_requests,
        "active_api_keys": len(api_keys_db)
    }

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(request: Request):
    try:
        check_admin_key(request)
        return templates.TemplateResponse("admin.html", {"request": request})
    except HTTPException:
        return RedirectResponse(url="/")

@app.get("/admin/metrics")
async def admin_metrics(request: Request):
    check_admin_key(request)
    now = datetime.utcnow()
    today = now.date()
    total_requests = len(logs_db)
    today_requests = sum(1 for l in logs_db if datetime.fromisoformat(l['timestamp']).date() == today)
    active_keys = sum(1 for k in api_keys_db if datetime.fromisoformat(k['valid_until']) > now)
    error_rate = 0
    if total_requests:
        error_rate = 100 * sum(1 for l in logs_db if l['status'] >= 400) // total_requests
    daily_requests = {}
    for i in range(7):
        d = (now - timedelta(days=6-i)).date()
        daily_requests[d.strftime("%a")] = sum(1 for l in logs_db if datetime.fromisoformat(l['timestamp']).date() == d)
    key_distribution = {}
    for k in api_keys_db:
        key_distribution[k['name']] = sum(1 for l in logs_db if l['api_key'] == k['key'])
    return {
        "total_requests": total_requests,
        "today_requests": today_requests,
        "active_keys": active_keys,
        "error_rate": error_rate,
        "daily_requests": daily_requests,
        "key_distribution": key_distribution,
    }

@app.get("/admin/list_api_keys")
async def admin_list_api_keys(request: Request):
    check_admin_key(request)
    now = datetime.utcnow()
    for k in api_keys_db:
        k['count'] = sum(1 for l in logs_db if l['api_key'] == k['key'] and datetime.fromisoformat(l['timestamp']).date() == now.date())
    return api_keys_db

@app.get("/admin/recent_logs")
async def admin_recent_logs(request: Request):
    check_admin_key(request)
    return logs_db[-6:]

@app.post("/admin/create_api_key")
async def admin_create_api_key(request: Request, data: dict = Body(...)):
    check_admin_key(request)

    prefix = "StrangerApi"
    total_length = 18
    remaining_length = total_length - len(prefix)
    random_part = str(uuid4()).replace('-', '')[:remaining_length]
    key = prefix + random_part

    now = datetime.utcnow()
    api_key = {
        "id": str(uuid4()),
        "key": key,
        "name": data.get("name", "unnamed"),
        "created_at": now.isoformat(),
        "valid_until": (now + timedelta(days=data.get("days_valid", 30))).isoformat(),
        "daily_limit": data.get("daily_limit", 100),
        "is_admin": data.get("is_admin", False),
        "count": 0
    }
    api_keys_db.append(api_key)
    save_api_keys()
    return {"api_key": key}

@app.post("/admin/revoke_api_key")
async def admin_revoke_api_key(request: Request, data: dict = Body(...)):
    check_admin_key(request)
    api_keys_db[:] = [k for k in api_keys_db if k["id"] != data["id"]]
    save_api_keys()
    return {"status": "ok"}

@app.get("/admin/cache_list")
async def admin_cache_list(request: Request):
    check_admin_key(request)
    try:
        files = get_all_files()
        return {"total": len(files), "files": files[-25:]}  # last 25 only
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch cache list: {e}")

@app.post("/admin/repair_cache")
async def admin_repair_cache(request: Request):
    check_admin_key(request)
    await ensure_pyrogram_running()
    await ensure_channel_known(pyro_api, CACHE_CHANNEL)

    fixed = 0
    deleted = 0
    total = 0
    errors = []

    try:
        records = get_all_files()
        total = len(records)
        for r in records:
            vid = r.get("video_id")
            ext = r.get("ext")
            mid = r.get("message_id")

            if not vid or not mid:
                continue
            try:
                msg = await pyro_api.get_messages(CACHE_CHANNEL, mid)
                if ext == "mp3" and not getattr(msg, "audio", None):
                    delete_cached_file(vid, ext)
                    deleted += 1
                    continue
                if ext == "mp4" and not getattr(msg, "video", None):
                    delete_cached_file(vid, ext)
                    deleted += 1
                    continue

                file_id = msg.audio.file_id if ext == "mp3" else msg.video.file_id
                if file_id != r.get("file_id"):
                    save_cached_file(vid, ext, mid, file_id)
                    fixed += 1

            except Exception as e:
                errors.append(f"{vid}.{ext}: {e}")
                delete_cached_file(vid, ext)
                deleted += 1

        return {
            "total_checked": total,
            "fixed": fixed,
            "deleted": deleted,
            "errors": errors[:10]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Repair failed: {e}")

@app.get("/search")
async def search(request: Request, q: str = Query(...)):
    _ = check_api_key(request)

    meta = await get_video_metadata(q)
    video_id = meta["id"]
    title = meta["title"]
    base = str(request.base_url).rstrip("/")

    return {
        "id": video_id,
        "title": title,
        "thumbnail": meta.get("thumbnail"),
        "url": meta["url"],
        "audio_stream": f"{base}/download/audio?video_id={video_id}&api_key=API_KEY",
        "video_stream": f"{base}/download/video?video_id={video_id}&api_key=API_KEY",
    }

@app.get("/download")
async def unified_download(request: Request, url: str = Query(...), type: str = Query("audio")):
    check_api_key(request)

    if "youtube.com" in url or "youtu.be" in url:
        if "v=" in url:
            video_id = url.split("v=")[-1].split("&")[0]
        else:
            video_id = url.rstrip("/").split("/")[-1]
    else:
        video_id = url 
        
    meta = await get_video_metadata(video_id)
    video_id = meta["id"]

    if type == "audio":
        return await process_cached_download(video_id, "mp3")
    elif type == "video":
        return await process_cached_download(video_id, "mp4")
    else:
        raise HTTPException(status_code=400, detail="Invalid type parameter")

async def process_cached_download(video_id: str, ext: str):
    await ensure_pyrogram_running()

    cached = await search_cache(video_id, ext)

    if cached and "message_id" in cached:
        tg_url = f"https://t.me/YtApisong/{cached['message_id']}"
        print(f"[CACHE HIT] {video_id}.{ext} -> {tg_url}")
        return {"status": "cached", "video_id": video_id, "telegram_url": tg_url}

    print(f"[CACHE MISS] Downloading {video_id}.{ext}")
    temp_path = None

    try:
        if ext == "mp3":
            temp_path = await ext_download_song(f"https://www.youtube.com/watch?v={video_id}")
        else:
            temp_path = await ext_download_video(f"https://www.youtube.com/watch?v={video_id}")
    except Exception as e:
        print(f"[External API Error] {e}")
        temp_path = None

    if not temp_path or not os.path.exists(temp_path):
        os.makedirs("downloads", exist_ok=True)

        temp_path = f"downloads/{video_id}_yt.{ext}"
        ydl_format = "best" if ext == "mp4" else "bestaudio"

        cmd = [
            "yt-dlp",
            "-f", ydl_format,
            "-o", temp_path,
            "--no-warnings",
            "--quiet",
            "--cookies", "cookies1.txt",
            f"https://www.youtube.com/watch?v={video_id}"
        ]

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(executor, lambda: subprocess.run(cmd))

    if not os.path.exists(temp_path) or os.path.getsize(temp_path) == 0:
        raise HTTPException(status_code=500, detail=f"Failed to download {video_id}.{ext}")

    sent = await cache_file_send(temp_path, video_id, ext)
    tg_url = f"https://t.me/YtApisong/{sent.id}"
    print(f"[CACHED] Uploaded {video_id}.{ext} -> {tg_url}")

    try:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
            print(f"[CLEANUP] Deleted temp file {temp_path}")
    except Exception as e:
        print(f"[CLEANUP ERROR] {e}")

    try:
        if os.path.exists("downloads"):
            for f in os.listdir("downloads"):
                if f.startswith(video_id) and f.endswith(".part"):
                    fp = os.path.join("downloads", f)
                    os.remove(fp)
                    print(f"[CLEANUP] Deleted leftover {fp}")
    except Exception as e:
        print(f"[CLEANUP .PART ERROR] {e}")

    return {
        "status": "uploaded",
        "video_id": video_id,
        "telegram_url": tg_url
    }


async def process_cached_video(video_id: str):
    await ensure_pyrogram_running()

    # 1️⃣ Check Cache
    cached = await search_cache(video_id, "mp4")
    if cached and "message_id" in cached:
        tg_url = f"https://t.me/YtApisong/{cached['message_id']}"
        print(f"[CACHE HIT] {video_id}.mp4 -> {tg_url}")
        return {"status": "cached", "video_id": video_id, "telegram_url": tg_url}

    print(f"[CACHE MISS] Downloading video for {video_id}.mp4")

    temp_path = None

    # ----------------------------------------------------
    # 2️⃣ (NEW LAYER 1) → External API Based Downloader
    # ----------------------------------------------------
    print("[LAYER 1] Trying external API video downloader first...")

    try:
        temp_path = await ext_download_video(f"https://www.youtube.com/watch?v={video_id}")
        if temp_path and os.path.exists(temp_path):
            print("[SUCCESS] External API video downloader worked.")
    except Exception as e:
        print("[External API Downloader ERROR]", e)
        temp_path = None

    # ----------------------------------------------------
    # 3️⃣ (NEW LAYER 2) → Try internal download_youtube_video()
    # ----------------------------------------------------
    if not temp_path or not os.path.exists(temp_path):
        print("[LAYER 2] Trying internal download_youtube_video()...")

        try:
            temp_path, _ = download_youtube_video(video_id)
            if temp_path and os.path.exists(temp_path):
                print("[SUCCESS] download_youtube_video worked.")
        except Exception as e:
            print(f"[Fallback 2: download_youtube_video ERROR] {e}")
            temp_path = None

    # ----------------------------------------------------
    # 4️⃣ SAFE FALLBACK → Patched yt-dlp (Guaranteed Working)
    # ----------------------------------------------------
    if not temp_path or not os.path.exists(temp_path):

        print("[LAYER 3] Using safe yt-dlp fallback...")

        os.makedirs("downloads", exist_ok=True)
        temp_path = f"downloads/{video_id}_yt.mp4"

        safe_opts = {
            "format": "bv*[ext=mp4][height<=720]+ba[ext=m4a]/best",
            "merge_output_format": "mp4",
            "outtmpl": temp_path,
            "quiet": True,
            "ignoreerrors": True,
            "allow_unplayable_formats": True,
            "cookiefile": "cookies1.txt" if os.path.exists("cookies1.txt") else None,
            "extractor_args": {
                "youtube": {
                    "player_client": ["web", "android"],
                    "no_check_formats": ["dash"]
                }
            }
        }

        try:
            import yt_dlp
            with yt_dlp.YoutubeDL(safe_opts) as ydl:
                ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=True)
        except Exception as e:
            print("[SAFE FALLBACK ERROR]", e)

    # ----------------------------------------------------
    # 5️⃣ FINAL VALIDATION
    # ----------------------------------------------------
    if not temp_path or not os.path.exists(temp_path) or os.path.getsize(temp_path) == 0:
        raise HTTPException(status_code=500, detail=f"Failed to download video")

    # ----------------------------------------------------
    # 6️⃣ UPLOAD TO TELEGRAM CACHE
    # ----------------------------------------------------
    sent = await cache_file_send(temp_path, video_id, "mp4")

    tg_url = f"https://t.me/YtApisong/{sent.id}"
    print(f"[CACHED] Uploaded {video_id}.mp4 -> {tg_url}")

    # ----------------------------------------------------
    # 7️⃣ CLEANUP TEMP FILES
    # ----------------------------------------------------
    try:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
            print(f"[CLEANUP] Deleted temp file {temp_path}")
    except Exception as e:
        print(f"[CLEANUP ERROR]", e)

    try:
        if os.path.exists("downloads"):
            for f in os.listdir("downloads"):
                if f.startswith(video_id) and f.endswith(".part"):
                    fp = os.path.join("downloads", f)
                    os.remove(fp)
                    print(f"[CLEANUP] Deleted leftover {fp}")
    except Exception as e:
        print(f"[CLEANUP .PART ERROR]", e)

    # ----------------------------------------------------
    # 8️⃣ RETURN RESPONSE
    # ----------------------------------------------------
    return {
        "status": "uploaded",
        "video_id": video_id,
        "telegram_url": tg_url
    }

@app.get("/download/audio")
async def download_audio(request: Request, video_id: str = Query(...)):
    check_api_key(request)
    return await process_cached_download(video_id, "mp3")

@app.get("/download/video")
async def download_video(request: Request, video_id: str = Query(...)):
    check_api_key(request)
    return await process_cached_video(video_id)

OWNER_ID = 7497210291

@bot_app.on_message(filters.private & filters.command("restart"))
async def restart_cmd(client, message: Message):
    if message.from_user.id != OWNER_ID:
        return await message.reply("You're not authorized to restart ❌")

    await message.reply("♻️ Restarting API... Please wait!")

    # Kill current python process
    os.system("kill -9 " + str(os.getpid()))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=WEB_PORT)