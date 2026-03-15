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

# Instagram login ma'lumotlari
INSTA_USER = 'HOUSELUXAI'
INSTA_PASS = 'ZEARZEAR1'
SESSION_FILE = "insta_session.json"

# --- FOYDALANUVCHI BAZASI ---
USER_FILE = "users_list.txt"

def add_to_db(user_id):
    if not os.path.exists(USER_FILE):
        with open(USER_FILE, "w") as f: f.write("")
    with open(USER_FILE, "r") as f:
        users = f.read().splitlines()
    if str(user_id) not in users:
        with open(USER_FILE, "a") as f:
            f.write(str(user_id) + "\n")

def get_total_users():
    if not os.path.exists(USER_FILE): return 0
    with open(USER_FILE, "r") as f:
        return len(f.read().splitlines())

# --- INSTAGRAM CLIENT ---
cl = Client()
def login_instagram():
    try:
        if os.path.exists(SESSION_FILE):
            cl.load_settings(SESSION_FILE)
        cl.login(INSTA_USER, INSTA_PASS)
        cl.dump_settings(SESSION_FILE)
        logging.info("Instagramga muvaffaqiyatli kirildi!")
    except Exception as e:
        logging.error(f"Login xatosi: {e}")

login_instagram()

# --- WEB SERVER (Render uchun) ---
server = Flask(__name__)
@server.route('/')
def index(): return "Bot is running!"

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server.run(host='0.0.0.0', port=port)

# --- BOT ---
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
    btn = InlineKeyboardButton(text="PROMPTNI ISHLATISH (GEMINI)", url="https://gemini.google.com/")
    markup.add(btn)
    return markup

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    add_to_db(message.from_user.id)
    await message.answer(
        "Xush kelibsiz! Instagram video linkini yuboring yoki PROMPT tugmasini bosing.",
        reply_markup=main_keyboard(message.from_user.id)
    )

@dp.message_handler(lambda message: message.text == "📝 PROMPT")
async def prompt_handler(message: types.Message):
    # Siz so'ragan maxsus prompt matni
    prompt_text = (
        "Men @INSTAGRAM_KASIMOV kanali administratoriman. Sening vazifang menga Reels videolarim uchun "
        "ingliz tilida marketing materiallari tayyorlash. Menga video mavzusini yuborganimda, FAQAT quyidagi "
        "formatdagi bitta yaxlit matnni yubor, hech qanday tushuntirish yoki bo'lim nomlarini (Hook, CTA, Hashtag kabi) yozma:\n\n"
        "[Bu yerda sening hook, caption va CTA matning bo'lsin]\n"
        "#hashtag1 #hashtag2 #hashtag3 #hashtag4 #hashtag5\n\n"
        "DIQQAT: Matndan tashqari birorta ortiqcha gap qo'shma. Faqat nusxa olishga tayyor blok bo'lsin. Tayyormisan?"
    )
    
    await message.answer(
        f"Matn nusxa olish uchun tayyor:\n\n<code>{prompt_text}</code>", 
        parse_mode="HTML", 
        reply_markup=gemini_inline()
    )

@dp.message_handler(lambda message: message.text == "📊 Statistika")
async def stats_handler(message: types.Message):
    if str(message.from_user.id) == str(ADMIN_ID):
        count = get_total_users()
        await message.answer(f"📊 Jami foydalanuvchilar: {count} ta")

@dp.message_handler()
async def handle_insta(message: types.Message):
    if "instagram.com" in message.text:
        wait = await message.answer("🔎 Yuklanmoqda...")
        try:
            media_pk = cl.media_pk_from_url(message.text)
            media_info = cl.media_info(media_pk)
            caption = media_info.caption_text
            if caption:
                await wait.edit_text(f"✅ **Original Caption:**\n\n<code>{caption}</code>", parse_mode="HTML")
            else:
                await wait.edit_text("❌ Ushbu postda matn (caption) topilmadi.")
        except Exception as e:
            logging.error(f"Xatolik yuz berdi: {e}")
            await wait.edit_text("❌ Xatolik! Link noto'g'ri yoki Instagram botni vaqtincha chekladi.")

if __name__ == "__main__":
    Thread(target=run_server, daemon=True).start()
    executor.start_polling(dp, skip_updates=True)
    
