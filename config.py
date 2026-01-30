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

API_VERSION = "1.0.0"
DEFAULT_ADMIN_KEY = "SHUKLA"
DEFAULT_API_KEY = "stranger"
DEFAULT_DEMO_KEY = "1a873582a7c83342f961cc0a177b2b26"

DEBUG = os.getenv("DEBUG", "False").lower() == "true"
SECRET_KEY = os.getenv("SECRET_KEY", "youtube_api_secure_key_change_in_production")
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8080))

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///youtube_api.db")
if DATABASE_URL.startswith("postgres://"):

    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

CACHE_TIMEOUT = int(os.getenv("CACHE_TIMEOUT", 60 * 60))  # 1 hour
DEFAULT_RATE_LIMIT = os.getenv("DEFAULT_RATE_LIMIT", "100 per minute")

STREAM_CHUNK_SIZE = int(os.getenv("STREAM_CHUNK_SIZE", 1024 * 1024))
DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "downloads")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 30))

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", 10))

PROXY_LIST = os.getenv("PROXY_LIST", "").split(",") if os.getenv("PROXY_LIST") else []
