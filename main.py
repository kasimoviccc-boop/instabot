import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
from threading import Thread
from instagrapi import Client
from instagrapi.exceptions import ChallengeRequired, LoginRequired

# --- SOZLAMALAR ---
# Tokenni BotFather'dan yangilagan bo'lsangiz, shu yerga yangisini yozing
API_TOKEN = '8618465943:AAEyXXvV8nBsfsgS09XE7ehT8cpydO9WutU'
ADMIN_ID = '6052580480'

# Instagram login ma'lumotlari
INSTA_USER = 'bottuchun'
INSTA_PASS = 'ZEARZEAR2'
SESSION_FILE = "insta_session.json"
USER_FILE = "users_list.txt"

# --- LOGGING ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- FOYDALANUVCHI BAZASI ---
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

# Instagramga O'zbekistondagi telefondan kirayotgandek ko'rinish berish
cl.set_device_settings({
    "app_version": "269.1.0.18.127",
    "android_version": 26,
    "android_release": "8.0.0",
    "model": "SM-G955F",
    "manufacturer": "samsung",
    "chipset": "samsungexynos8895",
    "cpu": "universal8895",
    "version_code": "443213196"
})

def login_instagram():
    try:
        if os.path.exists(SESSION_FILE):
            cl.load_settings(SESSION_FILE)
            logger.info("Tayyor sessiya yuklandi.")
        
        try:
            cl.get_timeline_feed() # Sessiya ishlayotganini tekshirish
        except Exception:
            logger.info("Sessiya yangilanmoqda...")
            cl.login(INSTA_USER, INSTA_PASS)
            cl.dump_settings(SESSION_FILE)
            logger.info("Instagramga muvaffaqiyatli kirildi!")
            
    except ChallengeRequired:
        logger.error("Instagram Challenge so'radi! Telefondan kirib tasdiqlang.")
    except Exception as e:
        logger.error(f"Instagram Login xatosi: {e}")

# Ishga tushishdan oldin login
login_instagram()

# --- WEB SERVER ---
server = Flask(__name__)
@server.route('/')
def index(): return "Bot is active and running!"

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server.run(host='0.0.0.0', port=port)

# --- BOT OBYEKTLARI ---
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# --- KLAVIATURALAR ---
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

# --- HANDLERS ---
@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    add_to_db(message.from_user.id)
    await message.answer(
        "Xush kelibsiz! Instagram video linkini yuboring yoki PROMPT tugmasini bosing.",
        reply_markup=main_keyboard(message.from_user.id)
    )

@dp.message_handler(lambda message: message.text == "📝 PROMPT")
async def prompt_handler(message: types.Message):
    # Siz xohlagan ASL VA TO'LIQ PROMPT MATNI
    prompt_text = (
        "Men @INSTAGRAM_KASIMOV kanali administratoriman. Sening vazifang menga Reels videolarim uchun "
        "ingliz tilida marketing materiallari tayyorlash. Menga video mavzusini yuborganimda, FAQAT quyidagi "
        "formatdagi bitta yaxlit matnni yubor, hech qanday tushuntirish yoki bo'lim nomlarini yozma:\n\n"
        "[Hook, caption va CTA matni]\n"
        "#hashtag1 #hashtag2 #hashtag3 #hashtag4 #hashtag5\n\n"
        "DIQQAT: Matndan tashqari birorta ortiqcha gap qo'shma. Faqat nusxa olishga tayyor blok bo'lsin."
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
            logger.error(f"Instagram xatosi: {e}")
            await wait.edit_text("❌ Xatolik! Akkauntga telefondan kirib 'Bu men edim' tugmasini bosing.")

# --- ISHGA TUSHIRISH ---
async def on_startup(dp):
    # Conflict (Terminated by other getUpdates) xatosini 100% tuzatadi
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Bot ishga tushdi!")

if __name__ == "__main__":
    Thread(target=run_server, daemon=True).start()
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
                    
