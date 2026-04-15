import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, executor, types
from flask import Flask
from threading import Thread
from instagrapi import Client

# --- SOZLAMALAR ---
API_TOKEN = '8618465943:AAEyXXvV8nBsfsgS09XE7ehT8cpydO9WutU'
INSTA_USER = 'HOUSELUXAI'
INSTA_PASS = 'ZEARZEAR1'
SESSION_FILE = "insta_session.json"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

cl = Client()

def setup_instagram():
    try:
        cl.set_device({
            "app_version": "269.1.0.18.127",
            "android_version": 26,
            "android_release": "8.0.0",
            "model": "SM-G955F",
            "manufacturer": "samsung",
            "chipset": "samsungexynos8895",
            "cpu": "universal8895",
            "version_code": "443213196"
        })
        
        if os.path.exists(SESSION_FILE):
            try:
                cl.load_settings(SESSION_FILE)
                logger.info("Sessiya yuklandi.")
            except Exception:
                logger.info("Eski sessiya yaroqsiz.")
        
        # Agar sessiya orqali login o'tmasa, qaytadan login qilamiz
        if not cl.user_id:
            cl.login(INSTA_USER, INSTA_PASS)
            cl.dump_settings(SESSION_FILE)
            logger.info("Instagramga yangidan kirildi!")
    except Exception as e:
        logger.error(f"Login xatosi: {e}")

setup_instagram()

server = Flask(__name__)
@server.route('/')
def index(): return "Bot Active"

def run_server():
    # Rasmda chiqqan port xatosini oldini olish uchun xavfsiz usul
    try:
        port = int(os.environ.get("PORT", 10000))
    except (TypeError, ValueError):
        port = 10000
    server.run(host='0.0.0.0', port=port)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# --- SIZNING TUGMALARINGIZ VA MATNLARINGIZ (O'ZGARMADI) ---

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True).add("📝 PROMPT")
    await message.answer("Xush kelibsiz! Reels linkini yuboring.", reply_markup=markup)

@dp.message_handler(lambda m: m.text == "📝 PROMPT")
async def send_prompt(message: types.Message):
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
            # Asinxron loop ichida ishlash botni qotib qolishidan asraydi
            loop = asyncio.get_event_loop()
            media_pk = await loop.run_in_executor(None, cl.media_pk_from_url, message.text)
            info = await loop.run_in_executor(None, cl.media_info, media_pk)
            
            caption = info.caption_text if info.caption_text else "Caption topilmadi"
            await wait.edit_text(f"✅ **Original Caption:**\n\n<code>{caption}</code>", parse_mode="HTML")
        except Exception as e:
            logger.error(f"Xatolik yuz berdi: {e}")
            await wait.edit_text("❌ Xatolik! Telefondan Instagramga kirib 'Bu men edim' tugmasini bosing.")

async def on_startup(dp):
    await bot.delete_webhook(drop_pending_updates=True)

if __name__ == "__main__":
    Thread(target=run_server, daemon=True).start()
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
            
