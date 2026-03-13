import os
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from flask import Flask
from threading import Thread

# --- SOZLAMALAR ---
API_TOKEN = '8618465943:AAHvDczmAX3Nyr3-xAZp2T0qs-YoRzCqUAQ'
ADMIN_ID = 6052580480  # <--- O'zingizni ID raqamingizni yozing

# --- FLASK (Render uxlab qolmasligi uchun) ---
app = Flask(__name__)
@app.route('/')
def home(): return "Bot ishlamoqda!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- TELEGRAM BOT ---
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Menyu tugmalarini yaratish funksiyasi
def get_main_menu(user_id):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    btn_prompt = KeyboardButton("📝 PROMPT")
    keyboard.add(btn_prompt)
    
    # Faqat admin uchun statistika tugmasi
    if user_id == ADMIN_ID:
        keyboard.add(KeyboardButton("📊 Statistika"))
    
    return keyboard

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer(
        "Xush kelibsiz! Instagram linkini yuboring yoki menyudan foydalaning.",
        reply_markup=get_main_menu(message.from_user.id)
    )

# 1. PROMPT tugmasi (Hamma uchun)
@dp.message_handler(lambda message: message.text == "📝 PROMPT")
async def send_prompt(message: types.Message):
    prompt_text = (
        "Men @INSTAGRAM_KASIMOV kanali administratoriman. Sening vazifang menga Reels va videolarim uchun "
        "global (ingliz tili) auditoriyaga moslangan professional marketing materiallari tayyorlab berish. "
        "Men senga video mavzusini yoki linkini yuborganimda, sen quyidagilarni taqdim etishing kerak:\n\n"
        "1️⃣ Hook & Caption: Odamni birinchi soniyada to'xtatadigan savol yoki fakt bilan boshlanuvchi, hissiyotga boy inglizcha matn.\n"
        "2️⃣ CTA: Videodan so'ng foydalanuvchini harakatga chorlovchi (obuna bo'lish yoki izoh qoldirish) yakuniy qism.\n"
        "3️⃣ 5 Ta Hashtag: Mavzuga oid eng ko'p qidiriladigan va viral bo'lishga yordam beradigan hashtaglar.\n"
        "4️⃣ SEO & Strategy: Agar video murakkab bo'lsa, uni qanday sarlavha bilan chiqarish bo'yicha qisqa maslahat.\n\n"
        "Hozir men senga yangi video yuboraman, tayyormisan?"
    )
    # Matnni ustiga bossa nusxa oladigan formatda yuboramiz
    await message.answer(f"```\n{prompt_text}\n```", parse_mode="Markdown")
    await message.answer("Tepadagi promptni nusxalab, HESHTEG bot sahifasiga video bilan qoʻshib yuboring!")

# 2. STATISTIKA tugmasi (Faqat ADMIN uchun)
@dp.message_handler(lambda message: message.text == "📊 Statistika")
async def show_stats(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("📊 Bot hozirda barqaror holatda.\nObunachilar: (bazaga qarab hisoblanadi)")
    else:
        await message.answer("Bu bo'lim faqat admin uchun.")

# 3. Instagram linklarini qayta ishlash (Sizning asosiy funksiyangiz)
@dp.message_handler()
async def handle_insta_link(message: types.Message):
    if "instagram.com" in message.text:
        await message.answer("⏳ Instagramdan ma'lumot olinmoqda, kuting...")
        # BU YERGA AVVALGI KODINGIZDAGI INSTAGRAMDAN MA'LUMOT OLISH QISMINI QO'YASIZ
        # Masalan: caption = get_insta_info(message.text)
        await message.answer("✅ Mana sizga kerakli hashtaglar!")
    else:
        await message.answer("Iltimos, Instagram linkini yuboring yoki menyudan foydalaning.")

if __name__ == '__main__':
    Thread(target=run_flask).start()
    executor.start_polling(dp, skip_updates=True)
    
