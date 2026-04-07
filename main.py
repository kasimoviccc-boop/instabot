import os
import logging
from aiogram import Bot, Dispatcher, executor, types
from flask import Flask
from threading import Thread
from instagrapi import Client

# --- SOZLAMALAR ---
API_TOKEN = '8618465943:AAGTxyROizsOOjHOymOytcO4GigmhdiGHC4'
ADMIN_ID = '6052580480'
INSTA_USER = 'bottuchun'
INSTA_PASS = 'ZEARZEAR2'
SESSION_FILE = "insta_session.json"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

cl = Client()
cl.set_device_settings({"app_version": "269.1.0.18.127", "android_version": 26, "model": "SM-G955F"})

def login_instagram():
    try:
        if os.path.exists(SESSION_FILE):
            cl.load_settings(SESSION_FILE)
            logger.info("Sessiya yuklandi.")
        cl.login(INSTA_USER, INSTA_PASS)
        cl.dump_settings(SESSION_FILE)
        logger.info("Instagramga kirildi!")
    except Exception as e:
        logger.error(f"Login xatosi: {e}")

login_instagram()

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
    await message.answer("Xush kelibsiz! Link yuboring.", reply_markup=markup)

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
        wait = await message.answer("🔎...")
        try:
            media_pk = cl.media_pk_from_url(message.text)
            info = cl.media_info(media_pk)
            await wait.edit_text(f"✅ **Matn:**\n\n<code>{info.caption_text}</code>", parse_mode="HTML")
        except Exception:
            await wait.edit_text("❌ Akkauntni telefondan tasdiqlang!")

async def on_startup(dp):
    await bot.delete_webhook(drop_pending_updates=True)

if __name__ == "__main__":
    Thread(target=run_server, daemon=True).start()
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
    
