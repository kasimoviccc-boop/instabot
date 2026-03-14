import os
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
from threading import Thread
from instagrapi import Client

# --- SOZLAMALAR ---
API_TOKEN = '8618465943:AAEM6BI2wM0TVanFN2Wc_85x1yLJ_JKqjfo'
ADMIN_ID = '6052580480' 

# --- FOYDALANUVCHI BAZASI ---
USER_FILE = "users_list.txt"

def add_to_db(user_id):
    if not os.path.exists(USER_FILE):
        with open(USER_FILE, "w") as f: f.write("")
    with open(USER_FILE, "r") as f:
        users = f.read().splitlines()
    if str(user_id) not in users:
        with open(USER_FILE, "a") as f:
            with open(USER_FILE, "a") as f: f.write(str(user_id) + "\n")

def get_total_users():
    if not os.path.exists(USER_FILE): return 0
    with open(USER_FILE, "r") as f:
        return len(f.read().splitlines())

# --- INSTAGRAM CLIENT ---
cl = Client()

# --- WEB SERVER (Render uchun) ---
server = Flask(__name__)
@server.route('/')
def index(): return "Bot is running!"

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server.run(host='0.0.0.0', port=port)

# --- BOT LOGIKASI ---
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

def main_keyboard(user_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("📝 PROMPT"))
    if str(user_id) == str(ADMIN_ID):
        markup.add(KeyboardButton("📊 Statistika"))
    return markup

def gemini_inline():
    markup = InlineKeyboardMarkup()
    btn = InlineKeyboardButton(text="PROMPT ISHLATISH", url="https://gemini.google.com/")
    markup.add(btn)
    return markup

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    add_to_db(message.from_user.id)
    await message.answer(
        "Xush kelibsiz! Instagram Reels yoki Video linkini yuboring, men hashtagni olib beraman.",
        reply_markup=main_keyboard(message.from_user.id)
    )

@dp.message_handler(lambda message: message.text == "📝 PROMPT")
async def prompt_handler(message: types.Message):
    # Matnni "Code" formatiga olamiz (Nusxalash uchun)
    prompt_text = (
        "Men @INSTAGRAM_KASIMOV kanali administratoriman. Sening vazifang menga Reels va videolarim uchun global (ingliz tili) auditoriyaga moslangan professional marketing materiallari tayyorlab berish. Men senga video mavzusini yoki linkini yuborganimda, sen quyidagilarni taqdim etishing kerak:\n"
        "Hook & Caption: Odamni birinchi soniyada to'xtatadigan savol yoki fakt bilan boshlanuvchi, hissiyotga boy inglizcha matn.\n"
        "CTA: Videodan so'ng foydalanuvchini harakatga chorlovchi (obuna bo'lish yoki izoh qoldirish) yakuniy qism.\n"
        "5 Ta Hashtag: Mavzuga oid eng ko'p qidiriladigan va viral bo'lishga yordam beradigan hashtaglar.\n"
        "SEO & Strategy: Agar video murakkab bo'lsa, uni qanday sarlavha bilan chiqarish bo'yicha qisqa maslahat.\n"
        "Hozir men senga yangi video yuboraman, tayyormisan?"
    )
    # MarkdownV2 nusxalash uchun eng yaxshisi
    safe_text = prompt_text.replace(".", "\\.").replace("-", "\\-").replace("(", "\\(").replace(")", "\\)")
    await message.answer(f"```\n{safe_text}\n```", parse_mode="MarkdownV2", reply_markup=gemini_inline())

@dp.message_handler(lambda message: message.text == "📊 Statistika")
async def stats_handler(message: types.Message):
    if str(message.from_user.id) == str(ADMIN_ID):
        count = get_total_users()
        await message.answer(f"📊 Jami foydalanuvchilar: {count} ta")

@dp.message_handler()
async def handle_insta_link(message: types.Message):
    if "instagram.com" in message.text:
        wait_msg = await message.answer("🔎 Yuklanmoqda...")
        try:
            # Media ID olish
            media_pk = cl.media_pk_from_url(message.text)
            # Media ma'lumotlarini olish
            media_info = cl.media_info(media_pk)
            caption = media_info.caption_text
            
            if caption:
                await wait_msg.edit_text(f"✅ **Video Captioni:**\n\n`{caption}`", parse_mode="Markdown")
            else:
                await wait_msg.edit_text("❌ Ushbu videoda caption topilmadi.")
        except Exception as e:
            await wait_msg.edit_text(f"❌ Xatolik yuz berdi. Link ochiq ekanligini tekshiring.")
    else:
        await message.answer("Iltimos, Instagram linkini yuboring.")

if __name__ == "__main__":
    Thread(target=run_server).start()
    executor.start_polling(dp, skip_updates=True)
