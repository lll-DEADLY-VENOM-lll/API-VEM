import json
import os
import logging
from datetime import datetime, timedelta
from uuid import uuid4
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ================= CONFIGURATION =================
# Aapke provided credentials yahan hain
API_ID = 28795512  
API_HASH = "c17e4eb6d994c9892b8a8b6bfea4042a"  
BOT_TOKEN = "8574015536:AAGhHfZ_qu12YSjW9mbTEtCLpxnymhA556M"  

# Admin ID list (Integers)
ADMIN_IDS = [8302503314]  
API_KEYS_FILE = "api_keys.json"
# =================================================

# Logging Setup
logging.basicConfig(level=logging.INFO)

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
# USER COMMANDS
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
        reply_markup=get_main_buttons(),
        parse_mode=enums.ParseMode.HTML
    )

@app.on_message(filters.command("free"))
async def free_key_handler(client, message):
    user_id = message.from_user.id
    api_keys = load_api_keys()
    now = datetime.utcnow()

    # Check for existing key
    for k in api_keys:
        if k.get("user_id") == user_id:
            expiry = datetime.fromisoformat(k["valid_until"])
            if expiry > now:
                return await message.reply_text(
                    f"<b>⚠️ ʏᴏᴜ ᴀʟʀᴇᴀᴅʏ ʜᴀᴠᴇ ᴀ ᴋᴇʏ!</b>\n"
                    f"{LINE}\n"
                    f"<b>🔑 ᴋᴇʏ:</b> <code>{k['key']}</code>\n"
                    f"<b>⏳ ᴇxᴘɪʀʏ:</b> {expiry.strftime('%d %b, %Y')}\n"
                    f"<b>📊 ʟɪᴍɪᴛ:</b> 1100 ʀᴇǫᴜᴇsᴛs\n"
                    f"{LINE}",
                    parse_mode=enums.ParseMode.HTML
                )

    # Generate New Key
    new_key = f"STRANGER-{uuid4().hex[:8].upper()}"
    valid_until = (now + timedelta(days=7)).isoformat()

    api_keys.append({
        "user_id": user_id,
        "key": new_key,
        "valid_until": valid_until,
        "daily_limit": 1100,
        "type": "Free"
    })
    save_api_keys(api_keys)

    success_text = (
        f"<b>✅ ᴀᴘɪ ᴋᴇʏ ɢᴇɴᴇʀᴀᴛᴇᴅ!</b>\n"
        f"{LINE}\n"
        f"<b>🎫 ᴛɪᴇʀ:</b> ꜰʀᴇᴇ\n"
        f"<b>🔑 ᴋᴇʏ:</b> <code>{new_key}</code>\n"
        f"<b>📅 ᴠᴀʟɪᴅ ᴜɴᴛɪʟ:</b> {(now + timedelta(days=7)).strftime('%d %b, %Y')}\n\n"
        f"<i>ɴᴏᴛᴇ: ᴅᴏ ɴᴏᴛ sʜᴀʀᴇ ʏᴏᴜʀ ᴋᴇʏ ᴡɪᴛʜ ᴀɴʏᴏɴᴇ.</i>\n"
        f"{LINE}"
    )
    await message.reply_text(success_text, parse_mode=enums.ParseMode.HTML, reply_markup=get_main_buttons())

# -------------------------------------------------
# ADMIN COMMANDS
# -------------------------------------------------

@app.on_message(filters.command("stats") & filters.user(ADMIN_IDS))
async def admin_stats(client, message):
    keys = load_api_keys()
    now = datetime.utcnow()
    active = sum(1 for k in keys if datetime.fromisoformat(k["valid_until"]) > now)
    
    await message.reply_text(
        f"<b>📊 ꜱʏꜱᴛᴇᴍ ꜱᴛᴀᴛɪꜱᴛɪᴄꜱ</b>\n"
        f"{LINE}\n"
        f"<b>👥 ᴛᴏᴛᴀʟ ᴜsᴇʀs:</b> <code>{len(keys)}</code>\n"
        f"<b>🟢 ᴀᴄᴛɪᴠᴇ ᴋᴇʏs:</b> <code>{active}</code>\n"
        f"<b>🔴 ᴇxᴘɪʀᴇᴅ ᴋᴇʏs:</b> <code>{len(keys) - active}</code>\n"
        f"{LINE}",
        parse_mode=enums.ParseMode.HTML
    )

@app.on_message(filters.command("allkey") & filters.user(ADMIN_IDS))
async def all_keys_admin(client, message):
    keys = load_api_keys()
    if not keys:
        return await message.reply_text("<b>❌ No keys found in database.</b>")

    text = "<b>🔑 ʟɪsᴛ ᴏғ ᴀᴘɪ ᴋᴇʏs (ʟᴀᴛᴇsᴛ 𝟷𝟻)</b>\n" + LINE + "\n"
    for k in keys[-15:]:
        status = "🟢" if datetime.fromisoformat(k["valid_until"]) > datetime.utcnow() else "🔴"
        text += f"{status} <code>{k['key']}</code> | ID: <code>{k['user_id']}</code>\n"
    
    await message.reply_text(text, parse_mode=enums.ParseMode.HTML)

@app.on_message(filters.command("delkey") & filters.user(ADMIN_IDS))
async def delete_key_admin(client, message):
    if len(message.command) < 2:
        return await message.reply_text("<b>❌ Usage:</b> /delkey [API_KEY]")
    
    target = message.command[1]
    keys = load_api_keys()
    new_keys = [k for k in keys if k["key"] != target]
    
    if len(keys) == len(new_keys):
        await message.reply_text("<b>❌ ᴋᴇʏ ɴᴏᴛ ғᴏᴜɴᴅ ɪɴ ᴅᴀᴛᴀʙᴀsᴇ!</b>")
    else:
        save_api_keys(new_keys)
        await message.reply_text(f"<b>✅ sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ:</b>\n<code>{target}</code>")

@app.on_message(filters.command("delallexpired") & filters.user(ADMIN_IDS))
async def clean_expired_admin(client, message):
    now = datetime.utcnow()
    keys = load_api_keys()
    filtered = [k for k in keys if datetime.fromisoformat(k["valid_until"]) > now]
    
    deleted_count = len(keys) - len(filtered)
    save_api_keys(filtered)
    
    await message.reply_text(
        f"<b>🧹 ᴄʟᴇᴀɴᴜᴘ ᴄᴏᴍᴘʟᴇᴛᴇᴅ!</b>\n"
        f"{LINE}\n"
        f"<b>🗑️ ʀᴇᴍᴏᴠᴇᴅ:</b> <code>{deleted_count}</code> ᴇxᴘɪʀᴇᴅ ᴋᴇʏs.\n"
        f"<b>🟢 ʀᴇᴍᴀɪɴɪɴɢ:</b> <code>{len(filtered)}</code> ᴀᴄᴛɪᴠᴇ ᴋᴇʏs."
    )

# -------------------------------------------------
# BOT EXECUTION
# -------------------------------------------------
if __name__ == "__main__":
    print("---------------------------------------")
    print("  STRANGER API BOT STARTED SUCCESSFULLY")
    print("  ADMIN ID: 8302503314")
    print("---------------------------------------")
    app.run()
