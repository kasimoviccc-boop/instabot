import os
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
from threading import Thread
from instagrapi import Client

# --- SOZLAMALAR ---
API_TOKEN = '8618465943:AAEM6BI2wM0TVanFN2Wc_85x1yLJ_JKqjfo'
ADMIN_ID = '6052580480' # <--- O'zingizni ID raqamingizni yozing

# --- FOYDALANUVCHI BAZASI (Oddiy fayl tizimi) ---
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

# --- INSTAGRAM INTEGRATSIYASI ---
insta_client = Client()

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

# Menyu Tugmalari
def main_keyboard(user_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("📝 PROMPT"))
    if str(user_id) == str(ADMIN_ID):
        markup.add(KeyboardButton("📊 Statistika"))
    return markup

# Inline Tugma
def gemini_inline():
    markup = InlineKeyboardMarkup()
    btn = InlineKeyboardButton(text="PROMPT ISHLATISH", url="https://gemini.google.com/")
    markup.add(btn)
    return markup

# --- HANDLERLAR ---

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    add_to_db(message.from_user.id)
    await message.answer(
        "Xush kelibsiz! Menga Instagram Reels yoki Video linkini yuboring, men sizga uning matnini (caption) olib beraman.",
        reply_markup=main_keyboard(message.from_user.id)
    )

@dp.message_handler(lambda message: message.text == "📝 PROMPT")
async def prompt_handler(message: types.Message):
    await message.answer(""Men @INSTAGRAM_KASIMOV kanali administratoriman. Sening vazifang menga Reels va videolarim uchun global (ingliz tili) auditoriyaga moslangan professional marketing materiallari tayyorlab berish. Men senga video mavzusini yoki linkini yuborganimda, sen quyidagilarni taqdim etishing kerak:
Hook & Caption: Odamni birinchi soniyada to'xtatadigan savol yoki fakt bilan boshlanuvchi, hissiyotga boy inglizcha matn.
CTA: Videodan so'ng foydalanuvchini harakatga chorlovchi (obuna bo'lish yoki izoh qoldirish) yakuniy qism.
5 Ta Hashtag: Mavzuga oid eng ko'p qidiriladigan va viral bo'lishga yordam beradigan hashtaglar.
SEO & Strategy: Agar video murakkab bo'lsa, uni qanday sarlavha bilan chiqarish bo'yicha qisqa maslahat.
Hozir men senga yangi video yuboraman, tayyormisan?"", reply_markup=gemini_inline())

@dp.message_handler(lambda message: message.text == "📊 Statistika")
async def stats_handler(message: types.Message):
    if str(message.from_user.id) == str(ADMIN_ID):
        count = get_total_users()
        await message.answer(f"📊 Botdan foydalanuvchilar jami soni: {count} ta")

@dp.message_handler()
async def instagram_downloader(message: types.Message):
    link = message.text
    if "instagram.com" in link:
        msg = await message.answer("⏳ Video tahlil qilinmoqda...")
        try:
            # Login qilmasdan ochiq ma'lumotni olishga urinish
            media_pk = insta_client.media_pk_from_url(link)
            media_info = insta_client.media_info(media_pk)
            caption_text = media_info.caption_text
            
            if caption_text:
                await msg.edit_text(f"✅ **Video matni (Caption):**\n\n`{caption_text}`", parse_mode="Markdown")
            else:
                await msg.edit_text("❌ Ushbu videoda matn (caption) topilmadi.")
        except Exception as e:
            await msg.edit_text("❌ Xatolik! Linkni tekshiring yoki video 'Private' (yopiq) emasligiga ishonch hosil qiling.")
    else:
        await message.answer("Iltimos, faqat Instagram video linkini yuboring.")

# --- ISHGA TUSHIRISH ---
if __name__ == "__main__":
    Thread(target=run_server).start()
    print("Bot ishga tushdi...")
    executor.start_polling(dp, skip_updates=True)
    
