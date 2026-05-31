#!/usr/bin/env python3
# =============================================================================
# VORTEX BOT v3.0 - FINAL ABSOLUTE WORKING
# Instagram Password Reset via Telegram
# By @xtxz7 | @kai_olds | @louis_olds
# =============================================================================

import os, sys, time, random, string, json, uuid, re, asyncio, threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# ─── AUTO INSTALL ──────────────────────────────────────────────────────────
try:
    import requests
    from telethon import TelegramClient, events, Button, utils
    from telethon.sessions import StringSession
except ImportError:
    os.system("pip install requests telethon --upgrade -q")
    import requests
    from telethon import TelegramClient, events, Button, utils
    from telethon.sessions import StringSession

# ═══════════════════════════════════════════════════════════════════════════
# PART 1 - CONFIG + INSTAGRAM ENGINE
# ═══════════════════════════════════════════════════════════════════════════

API_ID = 35964213
API_HASH = "49f6f929d59ba8c565c498015a48adb1"
BOT_TOKEN = "8740023572:AAGwxZga-zTOfsuOJXHgwMhaGUFodVTj9sA"
ADMIN_IDS = [7691071175]
CONFIG_FILE = "channelszss_config.json"
USERS_FILE = "userszsz.json"

# ─── DEFAULT CHANNELS ────────────────────────────────────────────────────
CHANNELS = {
    1: {
        "type": "public",
        "link": "https://t.me/vrtxportal",
        "username": "@vrtxportal",
        "invite_link": "https://t.me/vrtxportal"
    }
}

user_state = {}
user_tokens = {}
user_chat_ids = {}
executor = ThreadPoolExecutor(max_workers=20)

# ─── USERS (File-based) ───────────────────────────────────────────────────
registered_users = {}
last_update_id = 0  # For Bot API polling

P = '\033[35m'; G = '\033[92m'; Y = '\033[1;33m'; Z = '\033[1;31m'
B = '\033[94m'; N = '\033[1;37m'; J = '\033[2;36m'; E = '\033[38;5;208m'

def load_channels():
    global CHANNELS
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f:
                for k, v in json.load(f).items():
                    if "type" not in v: v["type"]="public"; v["invite_link"]=v.get("link","")
                    CHANNELS[int(k)] = v
        except: pass
    save_channels()

def save_channels():
    with open(CONFIG_FILE,"w") as f: json.dump({str(k):v for k,v in CHANNELS.items()},f,indent=2)

def load_users():
    global registered_users
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE) as f:
                data = json.load(f)
                for k, v in data.items():
                    registered_users[int(k)] = v
        except: pass

def save_users():
    with open(USERS_FILE,"w") as f:
        json.dump({str(k):v for k,v in registered_users.items()}, f, indent=2)

load_users()

def register_user(uid, username=None, first_name=None):
    global registered_users
    if uid not in registered_users:
        registered_users[uid] = {
            "username": username or "",
            "first_name": first_name or "",
            "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        save_users()
        print(f"{G}[+] User registered: {uid}{N}")

load_channels()

# ─── CHANNEL CHECK ─────────────────────────────────────────────────────────
def check_user_channels_sync(user_id):
    not_joined = []
    for idx, ch_data in CHANNELS.items():
        username = ch_data.get("username","").lstrip("@")
        if not username:
            not_joined.append(idx)
            continue
        try:
            r = requests.get(
                f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember",
                params={"chat_id": f"@{username}", "user_id": user_id},
                timeout=4
            )
            data = r.json()
            if data.get("ok"):
                status = data["result"]["status"]
                if status in ("member", "administrator", "creator", "restricted"):
                    continue
            not_joined.append(idx)
        except:
            not_joined.append(idx)
    return len(not_joined) == 0, not_joined

async def check_user_channels(user_id):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, check_user_channels_sync, user_id)

# ─── INSTAGRAM RESET ENGINE ────────────────────────────────────────────────
def gen_dev(cp):
    aid = f"android-{''.join(random.choices(string.hexdigits.lower(),k=16))}"
    ua = f"Instagram 394.0.0.46.81 Android ({random.choice(['28/9','29/10','30/11','31/12'])}; {random.choice(['240dpi','320dpi','480dpi'])}; {random.choice(['720x1280','1080x1920','1440x2560'])}; {random.choice(['samsung','xiaomi','huawei','oneplus','google'])}; {random.choice(['SM-G975F','Mi-9T','P30-Pro','ONEPLUS-A6003','Pixel-4'])}; intel; en_US; {random.randint(100000000,999999999)})"
    wid = str(uuid.uuid4())
    pw = f'#PWD_INSTAGRAM:0:{int(datetime.now().timestamp())}:{cp}'
    return aid, ua, wid, pw

def mkh(mid="", ua=""):
    return {"Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
            "X-Bloks-Version-Id":"e061cacfa956f06869fc2b678270bef1583d2480bf51f508321e64cfb5cc12bd",
            "X-Mid":mid,"User-Agent":ua,"Content-Length":"9481"}

def id_user(uid):
    try:
        r = requests.get(f"https://i.instagram.com/api/v1/users/{uid}/info/",
            headers={"User-Agent":"Instagram 219.0.0.12.117 Android","Accept":"application/json","X-IG-App-ID":"936619743392459"},timeout=5)
        if "<!DOCTYPE" in r.text: return "Private/Deleted"
        return r.json()["user"]["username"]
    except: return "Unknown"

def reset_pass(link, pw):
    try:
        aid, ua, wid, PASSWORD = gen_dev(pw)
        uidb36 = link.split("uidb36=")[1].split("&token=")[0]
        token = link.split("&token=")[1].split(":")[0]
        
        r = requests.post("https://i.instagram.com/api/v1/accounts/password_reset/",
            headers=mkh(ua=ua),
            data={"source":"one_click_login_email","uidb36":uidb36,"device_id":aid,"token":token,"waterfall_id":wid},
            timeout=15)
        
        if "user_id" not in r.text:
            if "challenge_required" in r.text: return {"success":False,"error":"Account has 2FA/security challenge."}
            if "expired" in r.text.lower(): return {"success":False,"error":"Reset link expired."}
            return {"success":False,"error":"Invalid reset link"}
        
        mid = r.headers.get("Ig-Set-X-Mid","")
        j = r.json()
        uid, cni = j["user_id"], j["cni"]
        nn = j.get("nonce_code","")
        cc = j.get("challenge_context","")
        
        u2 = "https://i.instagram.com/api/v1/bloks/apps/com.instagram.challenge.navigation.take_challenge/"
        d2 = {"user_id":str(uid),"cni":str(cni),"nonce_code":str(nn),
              "bk_client_context":'{"bloks_version":"e061cacfa956f06869fc2b678270bef1583d2480bf51f508321e64cfb5cc12bd","styles_id":"instagram"}',
              "challenge_context":str(cc),
              "bloks_versioning_id":"e061cacfa956f06869fc2b678270bef1583d2480bf51f508321e64cfb5cc12bd","get_challenge":"true"}
        r2 = requests.post(u2, headers=mkh(mid,ua), data=d2, timeout=15).text.replace('\\','')
        
        try: ccf = r2.split(f'(bk.action.i64.Const, {cni}), "')[1].split('", (bk.action.bool.Const, false)))')[0]
        except: return {"success":False,"error":"Challenge extraction failed"}
        
        d3 = {"is_caa":"False","source":"","uidb36":uidb36,
              "error_state":json.dumps({"type_name":"str","index":0,"state_id":1048583541}),
              "afv":"","cni":str(cni),"token":token,"has_follow_up_screens":"0",
              "bk_client_context":json.dumps({"bloks_version":"e061cacfa956f06869fc2b678270bef1583d2480bf51f508321e64cfb5cc12bd","styles_id":"instagram"}),
              "challenge_context":ccf,
              "bloks_versioning_id":"e061cacfa956f06869fc2b678270bef1583d2480bf51f508321e64cfb5cc12bd",
              "enc_new_password1":PASSWORD,"enc_new_password2":PASSWORD}
        requests.post(u2, headers=mkh(mid,ua), data=d3, timeout=15)
        
        uname = id_user(uid)
        return {"success":True,"password":pw,"user_id":uid,"username":uname}
    except Exception as e:
        return {"success":False,"error":f"Connection error or rate limited: {str(e)}"}
        # ═══════════════════════════════════════════════════════════════════════════
# PART 2 - TELEGRAM CLIENT + ALL EVENT HANDLERS
# ═══════════════════════════════════════════════════════════════════════════

client = TelegramClient(StringSession(), API_ID, API_HASH).start(bot_token=BOT_TOKEN)
print(f"{G}[+] VORTEX v3.0 - FINAL ABSOLUTE WORKING{N}")
print(f"{G}[+] Mode: GROUP + DM - ALAG HANDLERS{N}")

def mk_btns(nj):
    btns = []
    for idx in nj:
        cd = CHANNELS.get(idx,{})
        lbl = "🔒" if cd.get("type")=="private" else "📢"
        link = cd.get("invite_link") or cd.get("link","")
        btns.append([Button.url(f"{lbl} Channel {idx}", link)])
    if btns: btns.append([Button.inline("✅ Joined All", b"joined")])
    return btns

# ─── BOT API POLLING THREAD (Group messages ke liye) ──────────────────────
def bot_api_polling():
    """Bot API se directly group messages read karega"""
    global last_update_id
    
    print(f"{G}[+] Bot API polling thread started for GROUP messages{N}")
    
    while True:
        try:
            params = {"timeout": 30, "allowed_updates": ["message", "callback_query"]}
            if last_update_id:
                params["offset"] = last_update_id + 1
            
            r = requests.get(
                f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates",
                params=params,
                timeout=35
            )
            data = r.json()
            
            if data.get("ok") and data.get("result"):
                for update in data["result"]:
                    last_update_id = update["update_id"]
                    
                    # ─── CALLBACK QUERY HANDLE ───────────────────
                    if "callback_query" in update:
                        cb = update["callback_query"]
                        uid = cb["from"]["id"]
                        cb_data = cb["data"]
                        
                        # Async run in executor
                        future = asyncio.run_coroutine_threadsafe(
                            handle_bot_callback(uid, cb_data, cb),
                            client.loop
                        )
                        continue
                    
                    # ─── MESSAGE HANDLE ──────────────────────────
                    if "message" not in update:
                        continue
                    
                    msg = update["message"]
                    chat = msg.get("chat", {})
                    chat_type = chat.get("type", "")
                    uid = msg["from"]["id"]
                    text = msg.get("text", "")
                    
                    # Only handle group messages via Bot API
                    if chat_type not in ("group", "supergroup"):
                        continue
                    
                    chat_id = chat["id"]
                    message_id = msg["message_id"]
                    username = msg["from"].get("username", "")
                    first_name = msg["from"].get("first_name", "")
                    
                    print(f"{B}[BOT-API][GROUP] MSG from {uid} in {chat_id}: {(text or '(empty)')[:60]}{N}")
                    
                    # Register user
                    register_user(uid, username, first_name)
                    
                    # Handle command
                    if text.startswith("/"):
                        if text == "/start":
                            # Send start message
                            send_bot_message(chat_id, 
                                "**🔐 VORTEX PREMIUM v3.0**\n\n"
                                "✅ **ACCESS GRANTED**\n\n"
                                "📌 **STEPS:**\n"
                                "1️⃣ Send Instagram Reset Link\n"
                                "2️⃣ Send New Password\n"
                                "3️⃣ Done ✅\n\n"
                                "**📤 Send reset link:**",
                                message_id
                            )
                            user_state[uid] = {"step": "link"}
                        continue
                    
                    # ─── REPLY PROTECTION ────────────────────────
                    if "reply_to_message" in msg:
                        replied = msg["reply_to_message"]
                        original_id = replied["from"]["id"]
                        
                        if original_id != uid and uid not in ADMIN_IDS:
                            send_bot_message(chat_id,
                                "**⛔ This is not your message!**\n\n"
                                "❌ You can only interact with your own requests.",
                                message_id
                            )
                            continue
                    
                    # ─── CHANNEL VERIFICATION ──────────────────────
                    all_joined, nj = check_user_channels_sync(uid)
                    if not all_joined:
                        btn_msg = "⚠️ **VERIFICATION REQUIRED**\n\n"
                        for idx in nj:
                            cd = CHANNELS.get(idx,{})
                            btn_msg += f"❌ **Channel {idx}:** {cd.get('username','')}\n"
                        btn_msg += "\n**Join the channel and try again**"
                        send_bot_message(chat_id, btn_msg, message_id)
                        continue
                    
                    # ─── STATE MANAGEMENT ──────────────────────────
                    if uid not in user_state:
                        user_state[uid] = {"step": "link"}
                    
                    st = user_state[uid]
                    
                    # ─── STEP 1: LINK ──────────────────────────────
                    if st["step"] == "link":
                        if "uidb36=" not in text:
                            send_bot_message(chat_id, "**❌ Invalid!** Send Valid link with `uidb36=`", message_id)
                            continue
                        
                        user_state[uid] = {"step": "pass", "link": text}
                        send_bot_message(chat_id, "**✅ Link saved!**\n\n**🔑 Now send new password** (min 6 chars):", message_id)
                    
                    # ─── STEP 2: PASSWORD ───────────────────────────
                    elif st["step"] == "pass":
                        if len(text) < 6:
                            send_bot_message(chat_id, "**❌ Min 6 chars:**", message_id)
                            continue
                        
                        user_state[uid] = {"step": "busy"}
                        send_bot_message(chat_id, "**🔄 Resetting the password wait...**", message_id)
                        
                        try:
                            res = reset_pass(st["link"], text)
                            
                            if res.get("success"):
                                send_bot_message(chat_id,
                                    "━━━━━━━━━━━━━━━━━\n"
                                    "**✅ PASSWORD RESET SUCCESSFUL**\n"
                                    "━━━━━━━━━━━━━━━━━\n\n"
                                    f"**👤 Username:** `{res['username']}`\n"
                                    f"**🔑 New Password:** `{res['password']}`\n\n"
                                    "━━━━━━━━━━━━━━━━━\n"
                                    "**⚡ VORTEX PREMIUM v3.0**\n"
                                    "By @dochains \n\n"
                                    "Send Another Valid Reset Link"
                                )
                            else:
                                send_bot_message(chat_id,
                                    "━━━━━━━━━━━━━━━━━\n"
                                    "**❌ RESET FAILED**\n"
                                    "━━━━━━━━━━━━━━━━━\n\n"
                                    f"**Error:** `{res.get('error')}`\n\n"
                                    "Send `/start` to retry"
                                )
                        except Exception as ex:
                            send_bot_message(chat_id, f"**❌ Error:** `{str(ex)}`")
                        
                        user_state[uid] = {"step": "link"}
        
        except Exception as e:
            print(f"{Z}[!] Bot API polling error: {e}{N}")
            time.sleep(1)

def send_bot_message(chat_id, text, reply_to=None):
    """Bot API se message bhejne ke liye helper"""
    try:
        data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        if reply_to:
            data["reply_to_message_id"] = reply_to
        
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json=data,
            timeout=5
        )
    except:
        pass

async def handle_bot_callback(uid, cb_data, cb_data_full):
    """Bot API callback queries handle karega"""
    try:
        msg = cb_data_full.get("message", {})
        chat_id = msg.get("chat", {}).get("id", 0)
        message_id = msg.get("message_id", 0)
        
        if cb_data == "joined":
            all_joined, nj = check_user_channels_sync(uid)
            if all_joined:
                user_state[uid] = {"step": "link"}
                # Edit message via Bot API
                requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText",
                    json={
                        "chat_id": chat_id,
                        "message_id": message_id,
                        "text": "**✅ VERIFIED!**\n\n**📤 Send Instagram reset link:**",
                        "parse_mode": "Markdown"
                    },
                    timeout=5
                )
            else:
                msg_text = "❌ **NOT VERIFIED**\n\n"
                for idx in nj:
                    cd = CHANNELS.get(idx,{})
                    msg_text += f"❌ **Channel {idx}:** {cd.get('username','')}\n"
                msg_text += "\nJoin and try again"
                requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText",
                    json={
                        "chat_id": chat_id,
                        "message_id": message_id,
                        "text": msg_text,
                        "parse_mode": "Markdown"
                    },
                    timeout=5
                )
    except:
        pass

# ─── TELEGRAM CLIENT EVENTS (DM ke liye) ──────────────────────────────────

# ─── /START ────────────────────────────────────────────────────────────────
@client.on(events.NewMessage(pattern="/start"))
async def start_cmd(event):
    s = await event.get_sender()
    uid = s.id
    
    # Sirf DM
    if event.is_group or event.is_channel:
        return
    
    register_user(uid, s.username, s.first_name)
    print(f"{G}[Telethon][DM] /start from {uid}{N}")
    
    all_joined, nj = await check_user_channels(uid)
    
    if all_joined:
        user_state[uid] = {"step":"link"}
        await event.respond(
            "**🔐 VORTEX PREMIUM v3.0**\n\n"
            "✅ **ACCESS GRANTED**\n\n"
            "📌 **STEPS:**\n"
            "1️⃣ Send Instagram Reset Link\n"
            "2️⃣ Send New Password\n"
            "3️⃣ Done ✅\n\n"
            "**📤 Send reset link:**"
        )
    else:
        msg = "⚠️ **VERIFICATION REQUIRED**\n\n"
        for idx in nj:
            cd = CHANNELS.get(idx,{})
            typ = cd.get("type","public")
            if typ == "private":
                msg += f"🔒 **Channel {idx}:** {cd.get('username','')} (Request to Join)\n"
            else:
                msg += f"❌ **Channel {idx}:** {cd.get('username','')}\n"
        if any(CHANNELS.get(i,{}).get("type")=="private" for i in nj):
            msg += "\n🔒 **Private Channel:** Click link → Tap 'Request to Join' → Wait for approval"
        msg += "\n\nThen tap **✅ Joined All**"
        await event.respond(msg, buttons=mk_btns(nj))

# ─── CALLBACK ──────────────────────────────────────────────────────────────
@client.on(events.CallbackQuery(data=b"joined"))
async def joined_cb(event):
    s = await event.get_sender()
    uid = s.id
    all_joined, nj = await check_user_channels(uid)
    
    if all_joined:
        user_state[uid] = {"step":"link"}
        await event.edit("**✅ VERIFIED!**\n\n**📤 Send Instagram reset link:**")
    else:
        msg = "❌ **NOT VERIFIED**\n\n"
        for idx in nj:
            cd = CHANNELS.get(idx,{})
            msg += f"❌ **Channel {idx}:** {cd.get('username','')}\n"
        msg += "\nJoin and tap button again"
        await event.edit(msg, buttons=mk_btns(nj))

# ─── DM MESSAGE HANDLER ────────────────────────────────────────────────────
@client.on(events.NewMessage)
async def dm_msg_handler(event):
    """Sirf DM messages"""
    if not event.is_private:
        return
    
    s = await event.get_sender()
    uid = s.id
    
    if event.message.text and event.message.text.startswith("/"):
        return
    
    txt = event.message.text.strip()
    if not txt:
        return
    
    print(f"{G}[Telethon][DM] MSG from {uid}: {txt[:50]}{N}")
    register_user(uid, s.username, s.first_name)
    
    all_joined, nj = await check_user_channels(uid)
    if not all_joined:
        msg = "⚠️ **VERIFICATION REQUIRED**\n\n"
        for idx in nj:
            cd = CHANNELS.get(idx,{})
            typ = cd.get("type","public")
            if typ == "private":
                msg += f"🔒 **Channel {idx}:** {cd.get('username','')} (Request to Join)\n"
            else:
                msg += f"❌ **Channel {idx}:** {cd.get('username','')}\n"
        msg += "\nTap **✅ Joined All** when done"
        return await event.respond(msg, buttons=mk_btns(nj))
    
    if uid not in user_state: user_state[uid] = {"step":"link"}
    st = user_state[uid]
    
    if st["step"] == "link":
        if "uidb36=" not in txt:
            return await event.respond("**❌ Invalid!** Send Valid link with `uidb36=`")
        user_state[uid] = {"step":"pass", "link": txt}
        await event.respond("**✅ Link saved!**\n\n**🔑 Now send new password** (min 6 chars):")
    elif st["step"] == "pass":
        if len(txt) < 6:
            return await event.respond("**❌ Min 6 chars:**")
        user_state[uid] = {"step":"busy"}
        msg = await event.respond("**🔄 Resetting the password wait...**")
        try:
            loop = asyncio.get_event_loop()
            res = await loop.run_in_executor(executor, reset_pass, st["link"], txt)
            if res.get("success"):
                await msg.edit("━━━━━━━━━━━━━━━━━\n**✅ PASSWORD RESET SUCCESSFUL**\n━━━━━━━━━━━━━━━━━\n\n" + f"**👤 Username:** `{res['username']}`\n**🔑 New Password:** `{res['password']}`\n\n" + "━━━━━━━━━━━━━━━━━\n**⚡ VORTEX PREMIUM v3.0**\nBy @dochains \n\nSend Another Valid Reset Link")
            else:
                await msg.edit("━━━━━━━━━━━━━━━━━\n**❌ RESET FAILED**\n━━━━━━━━━━━━━━━━━\n\n" + f"**Error:** `{res.get('error')}`\n\nSend `/start` to retry")
        except Exception as ex:
            await msg.edit(f"**❌ Error:** `{str(ex)}`\n\nSend `/start`")
        user_state[uid] = {"step":"link"}

# ─── ADMIN COMMANDS (DM me) ────────────────────────────────────────────────
@client.on(events.NewMessage(pattern="/addchannel"))
async def add_ch(event):
    s = await event.get_sender()
    if s.id not in ADMIN_IDS: return await event.respond("**⛔ UNAUTHORIZED**")
    if not event.is_private: return
    parts = event.message.text.strip().split(maxsplit=3)
    if len(parts) < 3: return await event.respond("Usage: `/addchannel <invite_link> <@username>`\nor `/addchannel <invite_link> <@username> private`")
    link = parts[1]; uname = "@" + parts[2].lstrip("@")
    typ = "private" if (len(parts) > 3 and parts[3].lower() == "private") else "public"
    nxt = max(CHANNELS.keys()) + 1 if CHANNELS else 1
    CHANNELS[nxt] = {"type": typ, "link": link, "username": uname, "invite_link": link}
    save_channels()
    await event.respond(f"**✅ Channel {nxt} Added** ({typ})\n{uname}")

@client.on(events.NewMessage(pattern="/rmchannel"))
async def rm_ch(event):
    s = await event.get_sender()
    if s.id not in ADMIN_IDS: return await event.respond("**⛔ UNAUTHORIZED**")
    if not event.is_private: return
    parts = event.message.text.strip().split()
    if len(parts) < 2:
        cl = "\n".join([f"  {k}: {v['username']}" for k,v in CHANNELS.items()])
        return await event.respond(f"Usage: `/rmchannel <n>`\n\nCurrent:\n{cl}")
    try: idx = int(parts[1]); rem = CHANNELS.pop(idx); save_channels(); await event.respond(f"**✅ Removed Ch {idx}:** {rem['username']}")
    except: await event.respond("**❌ Invalid number**")

@client.on(events.NewMessage(pattern="/channels"))
async def list_ch(event):
    s = await event.get_sender()
    if s.id not in ADMIN_IDS: return await event.respond("**⛔ UNAUTHORIZED**")
    if not event.is_private: return
    if not CHANNELS: return await event.respond("No channels.")
    msg = "**📢 CHANNELS**\n\n"
    for idx,cd in sorted(CHANNELS.items()):
        ic = "🔒" if cd.get("type")=="private" else "📢"
        msg += f"{ic} **{idx}:** {cd['username']} ({cd.get('type','public')})\n   {cd['link']}\n\n"
    await event.respond(msg)

@client.on(events.NewMessage(pattern="/broadcast"))
async def broadcast_cmd(event):
    s = await event.get_sender()
    if s.id not in ADMIN_IDS: return await event.respond("**⛔ UNAUTHORIZED**")
    if not event.is_private: return
    parts = event.message.text.strip().split(maxsplit=1)
    if len(parts) < 2: return await event.respond(f"Usage: `/broadcast <message>`\n\nTotal users: {len(registered_users)}")
    msg_text = parts[1]; total = len(registered_users)
    if total == 0: return await event.respond("❌ No users.")
    await event.respond(f"**📤 Broadcasting to {total} users...**")
    sent = 0; failed = 0; failed_list = []
    status_msg = await event.respond(f"**📤 Progress:** 0/{total}")
    for uid, user_data in list(registered_users.items()):
        try:
            await client.send_message(int(uid), "━━━━━━━━━━━━━━━━━\n**📢 ADMIN BROADCAST**\n━━━━━━━━━━━━━━━━━\n\n" + f"{msg_text}\n\n━━━━━━━━━━━━━━━━━\n**⚡ VORTEX PREMIUM v3.0**")
            sent += 1
        except: failed += 1; failed_list.append(str(uid))
        if (sent + failed) % 5 == 0:
            try: await status_msg.edit(f"**📤 Progress:** {sent}/{total} | ❌ {failed}")
            except: pass
        await asyncio.sleep(0.05)
    result = "━━━━━━━━━━━━━━━━━\n**📢 BROADCAST COMPLETE**\n━━━━━━━━━━━━━━━━━\n\n" + f"✅ **Sent:** `{sent}`\n❌ **Failed:** `{failed}`\n👥 **Total:** `{total}`"
    if failed_list: result += f"\nFailed: `{', '.join(failed_list[:5])}`" + (f" +{len(failed_list)-5} more" if len(failed_list) > 5 else "")
    await status_msg.edit(result)

@client.on(events.NewMessage(pattern="/users"))
async def users_cmd(event):
    s = await event.get_sender()
    if s.id not in ADMIN_IDS: return await event.respond("**⛔ UNAUTHORIZED**")
    if not event.is_private: return
    total = len(registered_users)
    msg = f"**👥 USERS:** `{total}`\n\n"
    if registered_users:
        sorted_users = sorted(registered_users.items(), key=lambda x: x[1].get("registered_at",""), reverse=True)
        for uid, data in sorted_users[:15]:
            uname = data.get("username","") or data.get("first_name","Unknown")
            reg = data.get("registered_at","")
            msg += f"• `{uid}` - @{uname}\n"
    await event.respond(msg)

@client.on(events.NewMessage(pattern="/set"))
async def set_ch(event):
    s = await event.get_sender()
    if s.id not in ADMIN_IDS: return await event.respond("**⛔ UNAUTHORIZED**")
    if not event.is_private: return
    cmd = event.message.text.strip().split()[0].lower()
    mp = {"/set":1,"/set2":2,"/set3":3}; idx = mp.get(cmd,0)
    if not idx: return
    parts = event.message.text.strip().split(maxsplit=2)
    if len(parts) < 3: return await event.respond(f"Usage: `{cmd} <link> <@username>`")
    CHANNELS[idx] = {"type":"public","link":parts[1],"username":"@"+parts[2].lstrip("@"),"invite_link":parts[1]}
    save_channels()
    await event.respond(f"**✅ Channel {idx} Updated**")
    # ═══════════════════════════════════════════════════════════════════════════
# PART 3 - MAIN
# ═══════════════════════════════════════════════════════════════════════════

# ─── START BOT API POLLING THREAD ─────────────────────────────────────────
polling_thread = threading.Thread(target=bot_api_polling, daemon=True)
polling_thread.start()

# ─── MAIN ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"{G}{'='*60}{N}")
    print(f"{G}[+] VORTEX PREMIUM v3.0 - FINAL ABSOLUTE WORKING{N}")
    print(f"{G}[+] GROUP mode: Bot API Polling (direct){N}")
    print(f"{G}[+] DM mode: Telethon events{N}")
    print(f"{G}[+] Both work independently!{N}")
    print(f"{G}[+] Channels: {len(CHANNELS)}{N}")
    for idx,cd in sorted(CHANNELS.items()):
        print(f"    Ch {idx}: {cd['username']}")
    print(f"{G}[+] Registered users: {len(registered_users)}{N}")
    print(f"{G}[+] Broadcast: ALL users from USERS_FILE{N}")
    print(f"{G}[+] Reply protection: ACTIVE (group me){N}")
    print(f"{G}[+] Bot API Polling thread: STARTED{N}")
    print(f"{G}{'='*60}{N}")
    
    try:
        client.run_until_disconnected()
    except KeyboardInterrupt:
        print(f"\n{Z}[-] Stopped{N}")
    except Exception as e:
        print(f"\n{Z}[-] Error: {e}{N}")