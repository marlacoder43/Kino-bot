from pyrogram import Client, filters
from pyrogram.enums import ParseMode, ChatMemberStatus
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
import json

# ✅ Bot API credentials
API_ID = 22225255
API_HASH = "6cb04f39cc07170b75d1ce675eeb65b8"
BOT_TOKEN = "7618049070:AAGvuAektEiRIPJQcIHQt8lbtTyKb-ziCaM"

# ✅ Admin ID va kanallar
ADMIN_ID = 5732326881
STORAGE_CHANNEL = -1002625959955  

MOVIE_CHANNEL = "Archive_channel1"

FORCE_SUB_FILE = "force_subs.json"
EDIT_MODE_FILE = "edit_mode.txt"

bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ✅ JSON mavjudligini tekshirish
if not os.path.exists(FORCE_SUB_FILE):
    with open(FORCE_SUB_FILE, "w") as f:
        json.dump([], f)

# ✅ Fayllar
START_MESSAGE_FILE = "start_message.json"
EDIT_MODE_FILE = "edit_mode.txt"

# ✅ Majburiy obuna kanallarini yuklash va saqlash
def load_forced_subs():
    if os.path.exists(FORCE_SUB_FILE):
        with open(FORCE_SUB_FILE, "r") as f:
            return json.load(f)
    return []

def save_forced_subs(channels):
    with open(FORCE_SUB_FILE, "w") as f:
        json.dump(channels, f, indent=4)

# ✅ Obuna tekshirish
def is_subscribed(user_id):
    channels = load_forced_subs()
    for channel in channels:
        try:
            chat_member = bot.get_chat_member(channel, user_id)
            if chat_member.status not in [ChatMemberStatus.MEMBER, ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
                return False
        except Exception:
            return False
    return True

# ✅ MAJBURIY OBUNA XABARINI YUBORISH
def send_force_sub_message(user_id):
    channels = load_forced_subs()
    buttons = [[InlineKeyboardButton(f"📢 {channel}", url=f"https://t.me/{channel[1:]}")] for channel in channels]
    buttons.append([InlineKeyboardButton("🔄 Tekshirish", callback_data="check_sub")])

    bot.send_message(
        chat_id=user_id,
        text="❌ <b>Botdan foydalanish uchun quyidagi kanallarga obuna bo‘ling:</b>",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# ✅ START XABARINI YUKLASH
def load_start_message():
    if os.path.exists(START_MESSAGE_FILE):
        with open(START_MESSAGE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"text": "<b>👋 Assalomu alaykum {first_name}!</b>\n\n🔎 Kino kodini kiriting va biz sizga yuboramiz.", "photo": None}

# ✅ Start xabarini saqlash
def save_start_message(text=None, photo=None):
    data = load_start_message()
    if text:
        data["text"] = text
    if photo:
        data["photo"] = photo
    with open(START_MESSAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ✅ Placeholderlarni almashtirish
def format_start_message(text, user):
    return text.format(
        username=f"@{user.username}" if user.username else user.first_name,
        user_id=user.id,
        first_name=user.first_name
    )

# ✅ /start buyrug‘i - Foydalanuvchilar va adminlar uchun
@bot.on_message(filters.command("start"))
def start(client, message):
    user_id = message.chat.id
    start_data = load_start_message()
    formatted_text = format_start_message(start_data["text"], message.from_user)

    # ✅ Agar rasm bo‘lsa, rasm bilan yuborish
    if start_data["photo"]:
        bot.send_photo(
            chat_id=user_id,
            photo=start_data["photo"],
            caption=formatted_text,
            parse_mode=ParseMode.HTML
        )
    else:
        bot.send_message(
            chat_id=user_id,
            text=formatted_text,
            parse_mode=ParseMode.HTML
        )

    # ✅ Adminlar uchun qo‘shimcha tugmalar
    if user_id == ADMIN_ID:
        bot.send_message(
            chat_id=user_id,
            text="⚙️ <b>Admin panel:</b>\n\nStart xabarini yoki rasmini o‘zgartirish uchun quyidagi tugmalardan foydalaning.",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✏️ Start xabarini o‘zgartirish", callback_data="edit_start_text")],
                [InlineKeyboardButton("🖼 Start rasmini o‘zgartirish", callback_data="edit_start_photo")]
            ])
        )

# ✅ Start xabarini o‘zgartirish tugmasi
@bot.on_callback_query(filters.regex("edit_start_text"))
def edit_start_text(client, callback_query):
    if callback_query.from_user.id != ADMIN_ID:
        return

    bot.send_message(
        chat_id=ADMIN_ID,
        text="✍️ <b>Yangi start xabarini yuboring.</b>\n\n✅ Quyidagi placeholderlarni ishlatishingiz mumkin:\n"
             "`{username}` - Username yoki ism\n"
             "`{user_id}` - Foydalanuvchi ID\n"
             "`{first_name}` - Ism\n\n❌ Bekor qilish uchun /cancel buyrug‘idan foydalaning.",
        parse_mode=ParseMode.HTML
    )

    with open(EDIT_MODE_FILE, "w") as f:
        f.write("edit_text")

# ✅ Start rasmini o‘zgartirish tugmasi
@bot.on_callback_query(filters.regex("edit_start_photo"))
def edit_start_photo(client, callback_query):
    if callback_query.from_user.id != ADMIN_ID:
        return

    bot.send_message(
        chat_id=ADMIN_ID,
        text="📸 <b>Yangi start rasmini yuboring.</b>\n\n❌ Bekor qilish uchun /cancel buyrug‘idan foydalaning.",
        parse_mode=ParseMode.HTML
    )

    with open(EDIT_MODE_FILE, "w") as f:
        f.write("edit_photo")

# ✅ Start xabarini qabul qilish (faqat adminlar)
@bot.on_message(filters.text & filters.user(ADMIN_ID))
def receive_new_start_text(client, message):
    if not os.path.exists(EDIT_MODE_FILE):
        return  # ❌ Agar admin "startni o‘zgartirish" bosmagan bo‘lsa, hech narsa qilinmaydi

    with open(EDIT_MODE_FILE, "r") as f:
        mode = f.read().strip()

    if mode == "edit_text":
        save_start_message(text=message.text)
        os.remove(EDIT_MODE_FILE)
        message.reply_text("✅ Start xabari muvaffaqiyatli o‘zgartirildi!")

# ✅ Start rasmini qabul qilish (faqat adminlar)
@bot.on_message(filters.photo & filters.user(ADMIN_ID))
def receive_new_start_photo(client, message):
    if not os.path.exists(EDIT_MODE_FILE):
        return  # ❌ Agar admin "startni o‘zgartirish" bosmagan bo‘lsa, hech narsa qilinmaydi

    with open(EDIT_MODE_FILE, "r") as f:
        mode = f.read().strip()

    if mode == "edit_photo":
        file_id = message.photo.file_id
        save_start_message(photo=file_id)
        os.remove(EDIT_MODE_FILE)
        message.reply_text("✅ Start rasmi muvaffaqiyatli o‘zgartirildi!")

# ✅ /cancel - O‘zgartirishni bekor qilish (faqat adminlar)
@bot.on_message(filters.command("cancel") & filters.user(ADMIN_ID))
def cancel_edit(client, message):
    if os.path.exists(EDIT_MODE_FILE):
        os.remove(EDIT_MODE_FILE)
        message.reply_text("❌ O‘zgartirish bekor qilindi!")
    else:
        message.reply_text("⚠️ Hozir hech qanday o‘zgartirish jarayoni yo‘q.")



# ✅ /kanal - Admin uchun kanal boshqarish
@bot.on_message(filters.command("kanal") & filters.user(ADMIN_ID))
def manage_channels(client, message):
    channels = load_forced_subs()
    buttons = [[InlineKeyboardButton(f"🚫 O‘chirish - {channel}", callback_data=f"del_{channel}")] for channel in channels]

    if len(channels) < 6:  # Maksimal 6 ta kanal qo‘shish mumkin
        buttons.append([InlineKeyboardButton("+ Kanal qo‘shish", callback_data="add_channel")])

    bot.send_message(
        chat_id=ADMIN_ID,
        text="📢 <b>Majburiy obuna kanallarini boshqarish</b>\n\n"
             "Yangi kanal qo‘shish yoki mavjudini o‘chirish uchun tugmalarni bosing.",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# ✅ Yangi kanal qo‘shish tugmasi bosilganda
@bot.on_callback_query(filters.regex("add_channel"))
def request_channel_id(client, callback_query):
    bot.send_message(
        chat_id=ADMIN_ID,
        text="🔹 <b>Yangi kanal qo‘shish:</b>\n\n"
             "1️⃣ Iltimos, kanalga botni admin qilib qo‘ying.\n"
             "2️⃣ Kanal username (`@kanal_nomi`) yoki ID (`-100XXXXXXXXXX`) ni yuboring.",
        parse_mode=ParseMode.HTML
    )

    with open(EDIT_MODE_FILE, "w") as f:
        f.write("add_channel")

# ✅ Faqat kanal qo‘shish rejimida bo‘lsa, username yoki ID qabul qilish
@bot.on_message(filters.text & filters.user(ADMIN_ID))
def add_channel(client, message):
    if not os.path.exists(EDIT_MODE_FILE):
        return  # ❌ Agar admin kanal qo‘shish tugmasini bosmagan bo‘lsa, hech narsa qilmaydi

    with open(EDIT_MODE_FILE, "r") as f:
        mode = f.read().strip()

    if mode == "add_channel":
        channel = message.text.strip()
        channels = load_forced_subs()

        if channel.startswith("@") or channel.startswith("-100"):
            if channel not in channels:
                channels.append(channel)
                save_forced_subs(channels)
                message.reply_text(f"✅ {channel} kanal qo‘shildi!")
            else:
                message.reply_text("⚠️ Bu kanal allaqachon mavjud!")
        else:
            message.reply_text("⚠️ Noto‘g‘ri format! Iltimos, kanal ID yoki @username shaklida yuboring.")

        os.remove(EDIT_MODE_FILE)  # ✅ Jarayon tugadi, faylni o‘chiramiz

# ✅ Kanalni olib tashlash
@bot.on_callback_query(filters.regex(r"del_(.+)"))
def remove_channel(client, callback_query):
    channel = callback_query.data.split("_", 1)[1]
    channels = load_forced_subs()

    if channel in channels:
        channels.remove(channel)
        save_forced_subs(channels)
        callback_query.message.edit_text(f"✅ <b>{channel}</b> majburiy obunadan olib tashlandi.", parse_mode=ParseMode.HTML)
    else:
        callback_query.answer("⚠️ Kanal topilmadi!")



# ✅ /stats - Bot statistikasi (faqat admin uchun)
@bot.on_message(filters.command("stats") & filters.user(ADMIN_ID))
def bot_stats(client, message):
    bot.send_message(ADMIN_ID, "📊 Bot statistikasi hozircha mavjud emas.")

# ✅ /broadcast - Hammaga xabar yuborish
@bot.on_message(filters.command("broadcast") & filters.user(ADMIN_ID))
def broadcast_message(client, message):
    bot.send_message(ADMIN_ID, "📨 Yangi xabarni yozing va botga yuboring.")


# ✅ Obuna tekshirish (bu funksiya avvaldan mavjud deb hisoblaymiz)
def is_subscribed(user_id):
    return True  # Bu yerni oldingi kodingiz bilan almashtiring

# ✅ Kino izlash va yuborish
@bot.on_message(filters.text & filters.private & ~filters.user(ADMIN_ID))
def send_movie(client, message):
    user_id = message.chat.id
    movie_code = message.text.strip()

    if not movie_code.isdigit():  
        return  # Agar matn son bo‘lmasa, hech qanday javob qaytarmaydi

    if not is_subscribed(user_id):
        send_force_sub_message(user_id)
        return

    try:
        bot.copy_message(
            chat_id=user_id,
            from_chat_id=MOVIE_CHANNEL,
            message_id=int(movie_code),
            caption="<b>🎬 Siz so‘ragan kino topildi!</b>\n\n<i>Ko‘proq kinolar uchun: @Archive_channel1</i>",
            parse_mode=ParseMode.HTML
        )
    except Exception:
        message.reply_text("❌ Kino topilmadi yoki noto‘g‘ri kod kiritildi!")

# ✅ Admin video yuborganda uni saqlash
@bot.on_message(filters.video & filters.user(ADMIN_ID))
def upload_movie(client, message):
    try:
        # ✅ Channel ID ni tekshirish va yuklash
        chat = bot.get_chat(STORAGE_CHANNEL)

        # ✅ Forward video to storage channel
        forwarded_messages = bot.forward_messages(
            chat_id=chat.id,  
            from_chat_id=message.chat.id,
            message_ids=message.id
        )

        forwarded_message_id = forwarded_messages.id if hasattr(forwarded_messages, "id") else forwarded_messages[0].id

        message.reply_text(f"🚀 Yangi kino yuklandi!\n\n#️⃣ Kino kodi: {forwarded_message_id}")

    except Exception as e:
        message.reply_text(f"❌ Xatolik: {str(e)}")


# 🔹 BLOCK NON-ADMINS FROM SENDING VIDEOS
@bot.on_message(filters.video & ~filters.user(ADMIN_ID))
def restrict_videos(client, message):
    message.reply_text(
        "❌ <b>Siz botga to‘g‘ridan-to‘g‘ri video yubora olmaysiz!</b>\n\n"
        "📩 Agar sizda film bor bo‘lsa, admin bilan bog‘laning.",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📩 Admin bilan bog‘lanish", url="https://t.me/killerfurqat")]
        ])
    )
# ✅ Botni ishga tushirish
bot.run()