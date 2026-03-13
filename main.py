import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from flask import Flask
from threading import Thread

# --- SOZLAMALAR ---
# O'zingizning ma'lumotlaringizni kiriting
API_TOKEN = '8618465943:AAHvDczmAX3Nyr3-xAZp2T0qs-YoRzCqUAQ' # Bot tokeningiz
ADMIN_ID = 6052580480 # <--- O'zingizni ID raqamingizni yozing (masalan: 55443322)

# --- FLASK (Render uxlab qolmasligi uchun) ---
app = Flask(__name__)
@app.route('/')
def home(): return "Bot ishlamoqda!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- TELEGRAM BOT SOZLAMALARI ---
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# --- TUGMALAR (MENU) ---
def get_main_menu(user_id):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    
    # PROMPT tugmasi hamma uchun (Obunachilar va Admin)
    btn_prompt = KeyboardButton("📝 PROMPT")
    keyboard.add(btn_prompt)
    
    # Statistika faqat admin uchun ko'rinadi
    # ADMIN_ID ni str() ga o'girish xatolikni oldini oladi
    if str(user_id) == str(ADMIN_ID):
        btn_stat = KeyboardButton("📊 Statistika")
        keyboard.add(btn_stat)
    
    return keyboard

# --- HANDLERLAR ---

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    # Foydalanuvchi ID raqamiga qarab menyu yuborish
    menu = get_main_menu(message.from_user.id)
    await message.answer(
        "Xush kelibsiz! Instagram linkini yuboring yoki quyidagi menyudan foydalaning:",
        reply_markup=menu
    )

@dp.message_handler(lambda message: message.text == "📝 PROMPT")
async def send_prompt(message: types.Message):
    prompt_text = (
        "Men @INSTAGRAM_KASIMOV kanali administratoriman. Sening vazifang menga Reels va videolarim uchun "
        "global (ingliz tili) auditoriyaga moslangan professional marketing materiallari tayyorlab berish. "
        "Men senga video mavzusini yoki linkini yuborganimda, sen quyidagilarni taqdim etishing kerak:\n\n"
        "**Hook & Caption:** Odamni birinchi soniyada to'xtatadigan savol yoki fakt bilan boshlanuvchi, hissiyotga boy inglizcha matn.\n\n"
        "**CTA:** Videodan so'ng foydalanuvchini harakatga chorlovchi (obuna bo'lish yoki izoh qoldirish) yakuniy qism.\n\n"
        "**5 Ta Hashtag:** Mavzuga oid eng ko'p qidiriladigan va viral bo'lishga yordam beradigan hashtaglar.\n\n"
        "**SEO & Strategy:** Agar video murakkab bo'lsa, uni qanday sarlavha bilan chiqarish bo'yicha qisqa maslahat.\n\n"
        "Hozir men senga yangi video yuboraman, tayyormisan?"
    )
    # Matn ustiga bossa nusxa oladigan format (MarkdownV2)
    # Ba'zi belgilarni escape qilish shart emas agar oddiy matn ishlatsak
    await message.answer(f"```\n{prompt_text}\n```", parse_mode="Markdown")
    await message.answer("Tepadagi promptni nusxalab, ChatGPT'ga yuboring!")

@dp.message_handler(lambda message: message.text == "📊 Statistika")
async def show_stats(message: types.Message):
    if str(message.from_user.id) == str(ADMIN_ID):
        await message.answer("📊 Bot hozirda barqaror ishlamoqda.\nKanal: @INSTAGRAM_KASIMOV")
    else:
        await message.answer("Kechirasiz, bu bo'lim faqat administrator uchun.")

# Instagram linklarini ushlash qismi
@dp.message_handler()
async def handle_message(message: types.Message):
    if "instagram.com" in message.text:
        await message.answer("🔍 Link qabul qilindi. Ma'lumotlar olinmoqda...")
        # Bu yerga o'zingizning instagram ma'lumot olish kodingizni ulab qo'ying
    else:
        # Agar oddiy matn yozsa, tugmalarni ko'rsatish
        await message.answer("Iltimos, Instagram linkini yuboring yoki tugmalardan foydalaning.", 
                             reply_markup=get_main_menu(message.from_user.id))

# --- ISHGA TUSHIRISH ---
if __name__ == '__main__':
    # Flaskni alohida potokda ishga tushiramiz
    Thread(target=run_flask).start()
    
    # Telegram botni ishga tushiramiz
    print("Bot muvaffaqiyatli ishga tushdi...")
    executor.start_polling(dp, skip_updates=True)
    
