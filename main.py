from instagrapi import Client
import time
from threading import Thread
from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot active!"

def run_flask():
    # Render uchun port 10000 bo'lishi shart
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- INSTAGRAM MA'LUMOTLARI ---
USERNAME = 'kasmvvc'
PASSWORD = 'ZEARZEAR1'
JAVOB_MATNI = "😂😂 Follow me! 1k goal soon🔥"

cl = Client()

def bot_logic():
    print("Instagramga ulanish...")
    try:
        cl.login(USERNAME, PASSWORD)
        print("Muvaffaqiyatli kirdik!")
    except Exception as e:
        print(f"Login xatosi: {e}")
    
    while True:
        try:
            user_id = cl.user_id_from_username(USERNAME)
            medias = cl.user_medias(user_id, amount=2) # Oxirgi 2 ta post
            for media in medias:
                comments = cl.media_comments(media.id)
                for comment in comments:
                    if USERNAME not in comment.text and comment.user_id != user_id:
                        cl.comment_reply(media.id, JAVOB_MATNI, comment.pk)
                        print(f"Javob berildi: {comment.text[:15]}...")
                        time.sleep(2)
        except Exception as e:
            print(f"Xato: {e}")
        time.sleep(420) # 7 daqiqa kutish

if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot_logic()
    
