import os
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
from threading import Thread
from instagrapi import Client  # Bu kutubxona link orqali captionni olish uchun eng yaxshisi

# --- SOZLAMALAR ---
API_TOKEN = '8618465943:AAHvDczmAX3Nyr3-xAZp2T0qs-YoRzCqUAQ'
ADMIN_ID = '6052580480' # <--- O'zingizni ID raqamingizni yozing

# --- FOYDALANUVCHILARNI HISOBLASH ---
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
cl = Client() # Instagram ma'lumotlarini olish uchun

# 1. Pastki menyu
def get_main_menu(user_id):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("📝 PROMPT"))
    if str(user_id) == str(ADMIN_ID):
        keyboard.add(KeyboardButton("📊 Statistika"))
    return keyboard

# 2. Inline tugma (PROMPT osti uchun)
def get_prompt_inline():
    inline_kb = InlineKeyboardMarkup()
    btn = InlineKeyboardButton(text="VIDEOGA HESHTEG OLISH", url="https://gemini.google.com/")
    inline_kb.add(btn)
    return inline_kb

# --- HANDLERLAR ---

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    add_user(message.from_user.id)
    await message.answer(
        "Assalomu alaykum!👋 Instagram linkini yuboring yoki quyidagi menyudan foydalaning👇:",
        reply_markup=get_main_menu(message.from_user.id)
    )

@dp.message_handler(lambda message: message.text == "📝 PROMPT")
async def send_prompt(message: types.Message):
    prompt_text = (
        "Men @INSTAGRAM_KASIMOV kanali administratoriman. Sening vazifang menga Reels va videolarim uchun global (ingliz tili) auditoriyaga moslangan professional marketing materiallari tayyorlab berish. Men senga video mavzusini yoki linkini yuborganimda, sen quyidagilarni taqdim etishing kerak:\n\n"
        "Hook & Caption: Odamni birinchi soniyada to'xtatadigan savol yoki fakt bilan boshlanuvchi, hissiyotga boy inglizcha matn.\n"
        "CTA: Videodan so'ng foydalanuvchini harakatga chorlovchi (obuna bo'lish yoki izoh qoldirish) yakuniy qism.\n"
        "5 Ta Hashtag: Mavzuga oid eng ko'p qidiriladigan va viral bo'lishga yordam beradigan hashtaglar.\n"
        "SEO & Strategy: Agar video murakkab bo'lsa, uni qanday sarlavha bilan chiqarish bo'yicha qisqa maslahat.\n\n"
        "Hozir men senga yangi video yuboraman, tayyormisan?"
    )
    await message.answer(f"```\n{prompt_text}\n```", parse_mode="Markdown", reply_markup=get_prompt_inline())

@dp.message_handler(lambda message: message.text == "📊 Statistika")
async def show_stats(message: types.Message):
    if str(message.from_user.id) == str(ADMIN_ID):
        total = count_users()
        await message.answer(f"📊 Jami foydalanuvchilar: {total} ta")

@dp.message_handler()
async def handle_instagram(message: types.Message):
    if "instagram.com" in message.text:
        status_msg = await message.answer("Y🔎 yuklanmoqda!...")
        try:
            # Link orqali media ID ni olish va captionni tortish
            media_pk = cl.media_pk_from_url(message.text)
            media_info = cl.media_info(media_pk)
            caption = media_info.caption_text
            
            if caption:
                await status_msg.edit_text(f"✅ **MANA HESHTEG👇:**\n\n`{caption}`", parse_mode="Markdown")
            else:
                await status_msg.edit_text("❌ Ushbu videoda caption topilmadi.")
        except Exception as e:
            await status_msg.edit_text(f"❌ Xatolik: Linkni tekshirib qayta yuboring.")
    else:
        await message.answer("Iltimos, faqat Instagram video linkini yuboring.")

if __name__ == '__main__':
    Thread(target=run_flask).start()
    executor.start_polling(dp, skip_updates=True)
    
