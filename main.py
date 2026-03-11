from instagrapi import Client
import time
import os

# --- SOZLAMALAR ---
USERNAME = 'kasmvvc' # Instagram ismingiz
PASSWORD = 'ZEARZEAR1' # Instagram parolingiz
JAVOB_MATNI = "Rahmat! Tez orada siz bilan bog'lanamiz. 😊" 
CHECK_INTERVAL = 420 # 7 daqiqa = 420 soniya

cl = Client()

def login_user():
    print("Instagramga kirish qilinmoqda...")
    try:
        cl.login(USERNAME, PASSWORD)
        print("Muvaffaqiyatli kirdik!")
    except Exception as e:
        print(f"Kirishda xatolik: {e}")

def check_and_reply():
    print(f"\n{time.ctime()}: Kommentariyalarni tekshiryapman...")
    try:
        user_id = cl.user_id_from_username(USERNAME)
        # Oxirgi 3 ta postni tekshiradi (hammasiga ulgurish uchun)
        medias = cl.user_medias(user_id, amount=3)
        
        for media in medias:
            comments = cl.media_comments(media.id)
            for comment in comments:
                # Agar kommentda hali bizning javobimiz bo'lmasa va u bizniki bo'lmasa
                if USERNAME not in comment.text and comment.user_id != user_id:
                    # Bu yerda oddiy tekshiruv: agar avval javob bermagan bo'lsak
                    # (instagrapi da reply tekshiruvi uchun sodda mantiq)
                    cl.comment_reply(media.id, JAVOB_MATNI, comment.pk)
                    print(f"Yangi kommentga javob berildi: {comment.text[:20]}...")
                    time.sleep(2) # Instagram bloklamasligi uchun kichik pauza
                    
    except Exception as e:
        print(f"Xatolik yuz berdi: {e}")
        # Agar login chiqib ketgan bo'lsa, qayta kiradi
        if "login_required" in str(e).lower():
            login_user()

if __name__ == "__main__":
    login_user()
    while True:
        check_and_reply()
        print(f"{CHECK_INTERVAL/60} daqiqa kutish...")
        time.sleep(CHECK_INTERVAL)
      
