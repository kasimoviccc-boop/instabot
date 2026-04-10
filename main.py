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
        # Qurilma identifikatsiyasi (Sizning telefoningizdek ko'rinish uchun)
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
            cl.load_settings(SESSION_FILE)
            logger.info("Sessiya yuklandi.")
        
        cl.login(INSTA_USER, INSTA_PASS)
        cl.dump_settings(SESSION_FILE)
        logger.info("Instagramga qurilma orqali muvaffaqiyatli kirildi!")
    except Exception as e:
        logger.error(f"Login xatosi: {e}")

setup_instagram()

server = Flask(__name__)
@server.route('/')
def index(): return "Bot Active"

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server.run(host='0.0.0.0', port=port)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

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
            await asyncio.sleep(2)
            media_pk = cl.media_pk_from_url(message.text)
            info = cl.media_info(media_pk)
            await wait.edit_text(f"✅ **Original Caption:**\n\n<code>{info.caption_text}</code>", parse_mode="HTML")
        except Exception:
            await wait.edit_text("❌ Xatolik! Telefondan Instagramga kirib 'Bu men edim' tugmasini bosing.")

async def on_startup(dp):
    await bot.delete_webhook(drop_pending_updates=True)

if __name__ == "__main__":
    Thread(target=run_server, daemon=True).start()
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
        
