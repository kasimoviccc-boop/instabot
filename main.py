import os
import logging
import asyncio
import time
from aiogram import Bot, Dispatcher, executor, types
from flask import Flask
from threading import Thread
from instagrapi import Client
from instagrapi.exceptions import ChallengeRequired, LoginRequired, RateLimitError

# --- SOZLAMALAR ---
API_TOKEN = '8618465943:AAEyXXvV8nBsfsgS09XE7ehT8cpydO9WutU'
ADMIN_ID = '6052580480'
INSTA_USER = 'bottuchun'
INSTA_PASS = 'ZEARZEAR2'
SESSION_FILE = "insta_session.json"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    """Sessiyani yuklash yoki yangidan login qilish"""
    try:
        if os.path.exists(SESSION_FILE):
            cl.load_settings(SESSION_FILE)
            logger.info("Tayyor sessiya yuklandi.")
        
        try:
            # Sessiya hali ham tirikligini tekshirish
            cl.get_timeline_feed()
        except (LoginRequired, Exception):
            logger.info("Sessiya eskirgan yoki yo'q, yangidan login qilinmoqda...")
            cl.login(INSTA_USER, INSTA_PASS)
            cl.dump_settings(SESSION_FILE)
            logger.info("Instagramga muvaffaqiyatli kirildi!")
            
    except ChallengeRequired:
        logger.error("Instagram 'Challenge' talab qildi. Akkauntga telefondan kirib tasdiqlang!")
    except Exception as e:
        logger.error(f"Instagram login xatosi: {e}")

# Bot ishga tushishidan oldin login
login_instagram()

# --- WEB SERVER (Render uchun) ---
server = Flask(__name__)
@server.route('/')
def index(): return "Bot Active"

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server.run(host='0.0.0.0', port=port)

# --- BOT OBYEKTLARI ---
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# --- HANDLERS ---
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True).add("📝 PROMPT")
    await message.answer("Xush kelibsiz! Instagram Reels linkini yuboring.", reply_markup=markup)

@dp.message_handler(lambda m: m.text == "📝 PROMPT")
async def send_prompt(message: types.Message):
    # Siz yozgan asl PROMPT matni
    prompt_text = (
        "Men @INSTAGRAM_KASIMOV kanali administratoriman. Sening vazifang menga Reels videolarim uchun "
        "ingliz tilida marketing materiallari tayyorlash. Menga video mavzusini yuborganimda, FAQAT quyidagi "
        "formatdagi bitta yaxlit matnni yubor, hech qanday tushuntirish yoki bo'lim nomlarini yozma:\n\n"
        "[Hook, caption va CTA matni]\n"
        "#hashtag1 #hashtag2 #hashtag3 #hashtag4 #hashtag5\n\n"
        "DIQQAT: Matndan tashqari birorta ortiqcha gap qo'shma. Faqat nusxa olishga tayyor blok bo'lsin."
    )
    await message.answer(f"<code>{prompt_text}</code>", parse_mode="HTML")

@dp.message_handler()
async def insta_handler(message: types.Message):
    if "instagram.com" in message.text:
        wait = await message.answer("🔎 Yuklanmoqda...")
        try:
            # So'rovlar orasida 2 soniya kutish (Blokdan qochish uchun)
            await asyncio.sleep(2)
            
            media_pk = cl.media_pk_from_url(message.text)
            info = cl.media_info(media_pk)
            
            if info.caption_text:
                await wait.edit_text(f"✅ **Original Caption:**\n\n<code>{info.caption_text}</code>", parse_mode="HTML")
            else:
                await wait.edit_text("❌ Ushbu postda matn (caption) topilmadi.")
                
        except RateLimitError:
            await wait.edit_text("⚠️ Instagram so'rovlarni chekladi. Birozdan so'ng urinib ko'ring.")
        except Exception as e:
            logger.error(f"Xatolik: {e}")
            # Sessiya o'lgan bo'lsa qayta tiklashga urinish
            login_instagram()
            await wait.edit_text("❌ Xatolik! Instagram akkauntingizga telefondan kirib 'Bu men edim' tugmasini bosing.")

async def on_startup(dp):
    # Conflict (Terminated by other request) xatosini 100% tuzatadi
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Bot Telegram bilan aloqaga chiqdi!")

if __name__ == "__main__":
    Thread(target=run_server, daemon=True).start()
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
    
