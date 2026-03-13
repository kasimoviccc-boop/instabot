import os
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
from threading import Thread

# --- SOZLAMALAR ---
API_TOKEN = '8618465943:AAHvDczmAX3Nyr3-xAZp2T0qs-YoRzCqUAQ'
ADMIN_ID = 6052580480 # <--- O'zingizni ID raqamingizni yozing

# --- FOYDALANUVCHILARNI HISOBLASH TIZIMI ---
# Foydalanuvchilarni saqlash uchun oddiy txt fayl
USER_FILE = "users.txt"

def add_user(user_id):
    if not os.path.exists(USER_FILE):
        with open(USER_FILE, "w") as f: f.write("")
    
    with open(USER_FILE, "r") as f:
        users = f.read().splitlines()
    
    if str(user_id) not in users:
        with open(USER_FILE, "a") as f:
            f.write(str(user_id) + "\n")

def count_users():
    if not os.path.exists(USER_FILE): return 0
    with open(USER_FILE, "r") as f:
        return len(f.read().splitlines())

# --- FLASK ---
app = Flask(__name__)
@app.route('/')
def home(): return "Bot active!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- TELEGRAM BOT ---
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# 1. Pastki menyu (Reply Keyboard)
def get_main_menu(user_id):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("📝 PROMPT"))
    if str(user_id) == str(ADMIN_ID):
        keyboard.add(KeyboardButton("📊 Statistika"))
    return keyboard

# 2. Inline tugma (Xabar ostidagi tugma)
def get_inline_btn():
    inline_kb = InlineKeyboardMarkup()
    # Siz aytgan nom va Gemini linki
    btn = InlineKeyboardButton("VIDEOGA HESHTEG OLISH", url="https://gemini.google.com/")
    inline_kb.add(btn)
    return inline_kb

# --- HANDLERLAR ---

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    # Yangi foydalanuvchini bazaga qo'shish
    add_user(message.from_user.id)
    
    await message.answer(
        "Assalomu alaykum!👋 Instagram linkini yuboring yoki quyidagi menyudan foydalaning👇:",
        reply_markup=get_main_menu(message.from_user.id)
    )

@dp.message_handler(lambda message: message.text == "📝 PROMPT")
async def send_prompt(message: types.Message):
    prompt_text = (
        "Men @INSTAGRAM_KASIMOV kanali administratoriman. Sening vazifang menga Reels va videolarim uchun "
        "global (ingliz tili) auditoriyaga moslangan professional marketing materiallari tayyorlab berish..."
    )
    await message.answer(f"```\n{prompt_text}\n```", parse_mode="Markdown")
    await message.answer("Tepadagi promptni nusxalab, ChatGPT'ga yuboring!")

@dp.message_handler(lambda message: message.text == "📊 Statistika")
async def show_stats(message: types.Message):
    if str(message.from_user.id) == str(ADMIN_ID):
        total = count_users()
        await message.answer(f"📊 **Bot statistikasi:**\n\n👤 Jami foydalanuvchilar: {total} ta", parse_mode="Markdown")
    else:
        await message.answer("Bu bo'lim faqat admin uchun.")

@dp.message_handler()
async def handle_all(message: types.Message):
    if "instagram.com" in message.text:
        # Link kelsa Inline tugma bilan javob qaytaradi
        await message.answer(
            "🔍 Link qabul qilindi. Ma'lumotlar olinmoqda...\n\nPastdagi tugma orqali Gemini'ga o'tishingiz mumkin:", 
            reply_markup=get_inline_btn()
        )
    else:
        await message.answer("Iltimos, Instagram linkini yuboring.")

if __name__ == '__main__':
    Thread(target=run_flask).start()
    executor.start_polling(dp, skip_updates=True)

