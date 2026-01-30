import json
import os
from datetime import datetime, timedelta
from uuid import uuid4
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

API_KEYS_FILE = "api_keys.json"
LOGS_FILE = "logs.json"

ADMIN_IDS = [6868182331]  # Replace with your Telegram admin IDs

# ---------------------------
# Helper functions
# ---------------------------
def load_api_keys():
    if os.path.exists(API_KEYS_FILE):
        try:
            with open(API_KEYS_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def save_api_keys(keys):
    with open(API_KEYS_FILE, "w") as f:
        json.dump(keys, f, indent=2)

def load_logs():
    if os.path.exists(LOGS_FILE):
        try:
            with open(LOGS_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []

# Simulated IP fetch function
def get_user_ip(user_id):
    """
    Replace this with your actual logic to get user's IP.
    For now, we're simulating an IP based on user_id.
    """
    return f"192.168.0.{user_id % 255}"

# ---------------------------
# Buttons
# ---------------------------
MAIN_BUTTONS = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("📢 sᴜᴘᴘᴏʀᴛ", url="https://t.me/StrangerYTApi"),
        InlineKeyboardButton("📡 ᴜᴘᴅᴀᴛᴇs", url="https://t.me/StrangerApi")
    ],
    [
        InlineKeyboardButton("👨‍💻 ᴅᴇᴠᴇʟᴏᴘᴇʀ", url="https://t.me/AmShashank")
    ]
])

PREMIUM_BUTTONS = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("💎 ɢᴇᴛ ᴘʀᴇᴍɪᴜᴍ", url="https://t.me/AmShashank")
    ]
])

# ---------------------------
# Commands
# ---------------------------
@Client.on_message(filters.command("start"))
async def start_message(client, message):
    caption = (
        "🔥 **ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ sᴛʀᴀɴɢᴇʀ ᴀᴘɪ ʙᴏᴛ** 🔥\n\n"
        "**🚀 ᴛʜᴇ ᴇᴀsɪᴇsᴛ ᴡᴀʏ ᴛᴏ ɢᴇᴛ** **ғʀᴇᴇ ᴀᴘɪ ᴋᴇʏs** **ғᴏʀ ʏᴏᴜʀ ᴘʀᴏᴊᴇᴄᴛs!**\n\n"
        "**📌 FEATURES :**\n"
        "• 7 ᴅᴀʏs ғʀᴇᴇ ᴋᴇʏ ᴠᴀʟɪᴅɪᴛʏ ⏳\n"
        "• 1100 ʀᴇǫᴜᴇsᴛs ʟɪᴍɪᴛ 📊\n"
        "• ɪɴsᴛᴀɴᴛ ᴋᴇʏ ɢᴇɴᴇʀᴀᴛɪᴏɴ ⚡\n\n"
        "**ℹ️ ABOUT :**\n"
        "sᴛʀᴀɴɢᴇʀ ᴀᴘɪ ᴘʀᴏᴠɪᴅᴇs ғᴀsᴛ ᴀɴᴅ ʀᴇʟɪᴀʙʟᴇ ᴀᴘɪs ғᴏʀ ᴅᴇᴠᴇʟᴏᴘᴇʀs, "
        "sᴛᴜᴅᴇɴᴛs, ᴀɴᴅ ʜᴏʙʙʏ ᴘʀᴏᴊᴇᴄᴛs. ᴡʜᴇᴛʜᴇʀ ʏᴏᴜ'ʀᴇ ᴛᴇsᴛɪɴɢ ᴏʀ ʙᴜɪʟᴅɪɴɢ, "
        "ᴡᴇ'ᴠᴇ ɢᴏᴛ ʏᴏᴜ ᴄᴏᴠᴇʀᴇᴅ.\n\n"
        "💡 ᴜsᴇ `/free` ᴛᴏ ɢᴇᴛ ʏᴏᴜʀ ғʀᴇᴇ ᴀᴘɪ ᴋᴇʏ ɴᴏᴡ!"
    )

    await message.reply_photo(
        photo="https://files.catbox.moe/yoazrb.jpg",
        caption=caption,
        reply_markup=MAIN_BUTTONS
    )

@Client.on_message(filters.command("free"))
async def free_key_command(client, message):
    user_id = message.from_user.id
    user_ip = get_user_ip(user_id)  # Replace with actual IP fetching method
    api_keys = load_api_keys()
    now = datetime.utcnow()

    # Check if user already has an active key
    for k in api_keys:
        if (k.get("user_id") == user_id or k.get("ip_address") == user_ip) and datetime.fromisoformat(k["valid_until"]) > now:
            await message.reply_text(
                f"✅ You already have an active key:\n`{k['key']}`\n"
                f"📅 Valid until: **{k['valid_until']}**\n"
                f"🌐 IP: `{k['ip_address']}`",
                reply_markup=PREMIUM_BUTTONS
            )
            return

    # Generate new key
    prefix = "StrangerFreeApi"
    key = prefix + str(uuid4()).replace("-", "")[:6]
    valid_until = (now + timedelta(days=7)).isoformat()

    new_key = {
        "id": str(uuid4()),
        "key": key,
        "name": f"FreeKey_{user_id}",
        "user_id": user_id,
        "ip_address": user_ip,
        "created_at": now.isoformat(),
        "valid_until": valid_until,
        "daily_limit": 1100,
        "is_admin": False,
        "count": 0
    }

    api_keys.append(new_key)
    save_api_keys(api_keys)

    await message.reply_text(
        f"🎉 **Free API Key Generated!**\n\n"
        f"🔑 Key: `{key}`\n"
        f"📅 Valid Until: **{valid_until}**\n"
        f"📌 Limit: 1100 requests total\n"
        f"🌐 IP: `{user_ip}`\n\n"
        "Use this key in your API requests with `x-api-key` header.\n\n"
        "⚡ Upgrade to **Premium** for unlimited access!",
        reply_markup=PREMIUM_BUTTONS
    )

@Client.on_message(filters.command("stats") & filters.user(ADMIN_IDS))
async def stats_command(client, message):
    logs = load_logs()
    api_keys = load_api_keys()
    now = datetime.utcnow()
    today_str = now.strftime("%Y-%m-%d")

    total_requests = len(logs)
    today_requests = sum(1 for l in logs if l.get("timestamp", "").startswith(today_str))
    active_keys = sum(1 for k in api_keys if datetime.fromisoformat(k["valid_until"]) > now)

    await message.reply_text(
        f"📊 **API Stats**\n\n"
        f"🔹 Total Requests: **{total_requests}**\n"
        f"🔹 Today's Requests: **{today_requests}**\n"
        f"🔹 Active Keys: **{active_keys}**"
    )


KEYS_PER_PAGE = 10

def paginate_keys(keys, page=0):
    """Split keys into pages."""
    start = page * KEYS_PER_PAGE
    end = start + KEYS_PER_PAGE
    return keys[start:end]

def get_keys_text(api_keys, page=0):
    now = datetime.utcnow()
    keys_on_page = paginate_keys(api_keys, page)

    keys_list = "\n\n".join(
        [
            f"{'✅ Active' if datetime.fromisoformat(k['valid_until']) > now else '❌ Expired'}\n"
            f"**Name:** {k['name']}\n"
            f"`{k['key']}`\n"
            f"📅 Expiry: {k['valid_until']}"
            for k in keys_on_page
        ]
    )

    return keys_list if keys_list else "❌ No keys on this page."

def get_pagination_markup(total_keys, page):
    total_pages = (len(total_keys) - 1) // KEYS_PER_PAGE
    buttons = []

    if page > 0:
        buttons.append(InlineKeyboardButton("⬅ Prev", callback_data=f"keys_page_{page-1}"))
    if page < total_pages:
        buttons.append(InlineKeyboardButton("➡ Next", callback_data=f"keys_page_{page+1}"))

    return InlineKeyboardMarkup([buttons]) if buttons else None


@Client.on_message(filters.command("allkey") & filters.user(ADMIN_IDS))
async def all_keys_command(client, message):
    api_keys = load_api_keys()
    if not api_keys:
        await message.reply_text("❌ No keys have been generated yet.")
        return

    page = 0
    keys_text = get_keys_text(api_keys, page)
    markup = get_pagination_markup(api_keys, page)

    await message.reply_text(
        f"🔑 **All Generated Keys (Page {page+1})**\n\n{keys_text}",
        reply_markup=markup,
        disable_web_page_preview=True
    )


@Client.on_callback_query(filters.regex(r"keys_page_\d+"))
async def keys_page_callback(client, callback_query: CallbackQuery):
    if callback_query.from_user.id not in ADMIN_IDS:
        await callback_query.answer("⛔ You are not authorized!", show_alert=True)
        return

    page = int(callback_query.data.split("_")[-1])
    api_keys = load_api_keys()
    keys_text = get_keys_text(api_keys, page)
    markup = get_pagination_markup(api_keys, page)

    await callback_query.message.edit_text(
        f"🔑 **All Generated Keys (Page {page+1})**\n\n{keys_text}",
        reply_markup=markup,
        disable_web_page_preview=True
    )



@Client.on_message(filters.command("delkey") & filters.user(ADMIN_IDS))
async def delete_key_command(client, message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.reply_text("❌ Usage: `/delkey <api_key>`", quote=True)
        return

    key_to_delete = parts[1].strip()
    api_keys = load_api_keys()

    updated_keys = [k for k in api_keys if k["key"] != key_to_delete]

    if len(updated_keys) == len(api_keys):
        await message.reply_text(f"❌ Key `{key_to_delete}` not found.")
        return

    save_api_keys(updated_keys)
    await message.reply_text(f"✅ Key `{key_to_delete}` has been deleted successfully.")

# ---------------------------
# Show expired keys
# ---------------------------
@Client.on_message(filters.command("expiredkey") & filters.user(ADMIN_IDS))
async def expired_keys_command(client, message):
    now = datetime.utcnow()
    api_keys = load_api_keys()
    expired = [k for k in api_keys if datetime.fromisoformat(k["valid_until"]) < now]

    if not expired:
        await message.reply_text("✅ No expired keys found.")
        return

    keys_list = "\n\n".join(
        [
            f"**Name:** {k['name']}\n`{k['key']}`\n📅 Expired On: {k['valid_until']}"
            for k in expired
        ]
    )

    await message.reply_text(
        f"🗑 **Expired Keys:**\n\n{keys_list}",
        disable_web_page_preview=True
    )

# ---------------------------
# Delete all expired keys
# ---------------------------
@Client.on_message(filters.command("delallexpired") & filters.user(ADMIN_IDS))
async def delete_all_expired_command(client, message):
    now = datetime.utcnow()
    api_keys = load_api_keys()
    expired = [k for k in api_keys if datetime.fromisoformat(k["valid_until"]) < now]

    if not expired:
        await message.reply_text("✅ No expired keys to delete.")
        return

    updated_keys = [k for k in api_keys if datetime.fromisoformat(k["valid_until"]) >= now]
    save_api_keys(updated_keys)

    await message.reply_text(f"🗑 Deleted **{len(expired)}** expired keys successfully.")
