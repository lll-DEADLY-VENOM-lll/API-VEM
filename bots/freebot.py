import json
import os
import logging
import asyncio
from datetime import datetime, timedelta
from uuid import uuid4
from pyrogram import Client, filters, enums, idle # idle import kiya gaya hai
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ================= CONFIGURATION =================
API_ID = 28795512  
API_HASH = "c17e4eb6d994c9892b8a8b6bfea4042a"  
BOT_TOKEN = "8574015536:AAGhHfZ_qu12YSjW9mbTEtCLpxnymhA556M"  

ADMIN_IDS = [8302503314]  # Admin ID as Integer
API_KEYS_FILE = "api_keys.json"
# =================================================

# Logging Setup
logging.basicConfig(level=logging.INFO)

# Client Initialization
app = Client(
    "StrangerApiBot", 
    api_id=API_ID, 
    api_hash=API_HASH, 
    bot_token=BOT_TOKEN
)

# -------------------------------------------------
# DATABASE FUNCTIONS
# -------------------------------------------------
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
        json.dump(keys, f, indent=4)

# -------------------------------------------------
# UI STYLING & BUTTONS
# -------------------------------------------------
HEADER_PIC = "https://files.catbox.moe/yoazrb.jpg"
LINE = "<b>━━━━━━━━━━━━━━━━━━━━━━━━━━</b>"

def get_main_buttons():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📢 sᴜᴘᴘᴏʀᴛ", url="https://t.me/NOBITA_SUPPORT"),
            InlineKeyboardButton("📡 ᴜᴘᴅᴀᴛᴇs", url="https://t.me/ll_DEADLY_VENOM_ll")
        ],
        [InlineKeyboardButton("👨‍💻 ᴅᴇᴠᴇʟᴏᴘᴇʀ", url="https://t.me/ll_DEADLY_VENOM_ll")],
        [InlineKeyboardButton("💎 ᴜᴘɢʀᴀᴅᴇ ᴛᴏ ᴘʀᴇᴍɪᴜᴍ", url="https://t.me/ll_DEADLY_VENOM_ll")]
    ])

# -------------------------------------------------
# USER HANDLERS
# -------------------------------------------------

@app.on_message(filters.command("start"))
async def start_handler(client, message):
    user = message.from_user
    welcome_text = (
        f"<b>🚀 ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ sᴛʀᴀɴɢᴇʀ ᴀᴘɪ</b>\n"
        f"{LINE}\n"
        f"ʜᴇʟʟᴏ {user.mention} 👋\n\n"
        f"ᴛʜɪs ʙᴏᴛ ᴘʀᴏᴠɪᴅᴇs ʜɪɢʜ-sᴘᴇᴇᴅ ᴀᴘɪ ᴋᴇʏs ғᴏʀ ʏᴏᴜʀ ᴘʀᴏᴊᴇᴄᴛs.\n\n"
        f"<b>✨ ꜰᴇᴀᴛᴜʀᴇꜱ:</b>\n"
        f"├ ⚡ ꜰᴀsᴛ ʀᴇsᴘᴏɴsᴇ ᴛɪᴍᴇ\n"
        f"├ 🛡️ sᴇᴄᴜʀᴇ ᴇɴᴅᴘᴏɪɴᴛs\n"
        f"└ 📊 ᴅᴀɪʟʏ ᴜsᴀɢᴇ ᴛʀᴀᴄᴋᴇʀ\n\n"
        f"<b>🎁 ꜰʀᴇᴇ ᴀᴄᴄᴇꜱꜱ:</b>\n"
        f"ᴜsᴇ /free ᴛᴏ ɢᴇɴᴇʀᴀᴛᴇ ʏᴏᴜʀ ᴋᴇʏ.\n"
        f"{LINE}\n"
        f"<i>ᴘᴏᴡᴇʀᴇᴅ ʙʏ @StrangerApi</i>"
    )
    await message.reply_photo(
        photo=HEADER_PIC,
        caption=welcome_text,
        reply_markup=get_main_buttons()
    )

@app.on_message(filters.command("free"))
async def free_key_handler(client, message):
    user_id = message.from_user.id
    api_keys = load_api_keys()
    now = datetime.utcnow()

    for k in api_keys:
        if k.get("user_id") == user_id:
            expiry = datetime.fromisoformat(k["valid_until"])
            if expiry > now:
                return await message.reply_text(
                    f"<b>⚠️ ᴀᴄᴛɪᴠᴇ ᴋᴇʏ ꜰᴏᴜɴᴅ!</b>\n"
                    f"{LINE}\n"
                    f"<b>🔑 ᴋᴇʏ:</b> <code>{k['key']}</code>\n"
                    f"<b>⏳ ᴇxᴘɪʀʏ:</b> {expiry.strftime('%d %b, %Y')}\n"
                    f"{LINE}"
                )

    new_key = f"STRANGER-{uuid4().hex[:8].upper()}"
    valid_until = (now + timedelta(days=7)).isoformat()

    api_keys.append({
        "user_id": user_id,
        "key": new_key,
        "valid_until": valid_until,
        "daily_limit": 1100
    })
    save_api_keys(api_keys)

    await message.reply_text(
        f"<b>✅ ᴀᴘɪ ᴋᴇʏ ɢᴇɴᴇʀᴀᴛᴇᴅ!</b>\n"
        f"{LINE}\n"
        f"<b>🔑 ᴋᴇʏ:</b> <code>{new_key}</code>\n"
        f"<b>📅 ᴠᴀʟɪᴅ ᴜɴᴛɪʟ:</b> {(now + timedelta(days=7)).strftime('%d %b, %Y')}\n"
        f"{LINE}"
    )

# -------------------------------------------------
# ADMIN HANDLERS
# -------------------------------------------------

@app.on_message(filters.command("stats") & filters.user(ADMIN_IDS))
async def admin_stats(client, message):
    keys = load_api_keys()
    now = datetime.utcnow()
    active = sum(1 for k in keys if datetime.fromisoformat(k["valid_until"]) > now)
    
    await message.reply_text(
        f"<b>📊 sʏsᴛᴇᴍ sᴛᴀᴛɪsᴛɪᴄs</b>\n"
        f"{LINE}\n"
        f"<b>👥 ᴛᴏᴛᴀʟ ᴜsᴇʀs:</b> {len(keys)}\n"
        f"<b>🟢 ᴀᴄᴛɪᴠᴇ ᴋᴇʏs:</b> {active}\n"
        f"{LINE}"
    )

@app.on_message(filters.command("allkey") & filters.user(ADMIN_IDS))
async def all_keys_admin(client, message):
    keys = load_api_keys()
    if not keys: return await message.reply_text("❌ No keys found.")

    text = "<b>🔑 ʟɪsᴛ ᴏғ ᴀᴘɪ ᴋᴇʏs</b>\n" + LINE + "\n"
    for k in keys[-15:]:
        status = "🟢" if datetime.fromisoformat(k["valid_until"]) > datetime.utcnow() else "🔴"
        text += f"{status} <code>{k['key']}</code> | ID: <code>{k['user_id']}</code>\n"
    await message.reply_text(text)

@app.on_message(filters.command("delkey") & filters.user(ADMIN_IDS))
async def delete_key_admin(client, message):
    if len(message.command) < 2: return await message.reply_text("Usage: /delkey [KEY]")
    target = message.command[1]
    keys = load_api_keys()
    new_keys = [k for k in keys if k["key"] != target]
    if len(keys) == len(new_keys):
        await message.reply_text("❌ Key not found.")
    else:
        save_api_keys(new_keys)
        await message.reply_text(f"✅ Deleted: <code>{target}</code>")

# -------------------------------------------------
# BOT EXECUTION (Fixed idle Error)
# -------------------------------------------------

async def start_bot():
    await app.start()
    print("---------------------------------------")
    print("  STRANGER API BOT STARTED SUCCESSFULLY")
    print("---------------------------------------")
    await idle() # Fixed: use idle() from pyrogram, not app.idle()
    await app.stop()

if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(start_bot())
    except KeyboardInterrupt:
        pass
