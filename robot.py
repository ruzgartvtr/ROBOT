import cv2
import os
from glob import glob
# --- Yüz Tanıma Otomatik Kullanıcı Değiştirme Özelliği ---
# Global değişken: yüz tanıma aktif mi?
yuz_tanima_aktif = True

import os, threading, urllib.parse, webbrowser, requests, tempfile, subprocess, json, speech_recognition as sr, random, time
import re
import requests
import json
import time
import base64
from datetime import datetime
from elevenlabs.client import ElevenLabs
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.animation import Animation
from kivy.uix.camera import Camera
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image as KivyImage
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.metrics import dp
from kivy.uix.textinput import TextInput
from kivy.uix.camera import Camera
from kivy.uix.image import Image as KivyImage
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import subprocess
import zipfile
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from bs4 import BeautifulSoup
import wikipedia
import platform
from unidecode import unidecode
import difflib
import unicodedata
import os, pickle, numpy as np
from glob import glob
import vlc


try:
    import face_recognition
    _FACE_BACKEND = "fr"  # face_recognition
except Exception:
    _FACE_BACKEND = "cv2"  # LBPH fallback
def yeni_kullanici_ekle(ad, rol, yonerge):
    import json
    import os
    import cv2
    # settings.json'a ekle
    ayar = ayarlari_yukle()
    ayar["kullanicilar"].append({"ad": ad, "rol": rol, "yonerge": yonerge})
    with open(AYARLAR_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(ayar, f, ensure_ascii=False, indent=2)

    # fotoğraf çek ve faces/{ad}.jpg olarak kaydet
    os.makedirs("faces", exist_ok=True)
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    cam.release()
    if ret:
        face_path = os.path.join("faces", f"{ad}.jpg")
        cv2.imwrite(face_path, frame)
        print(f"[FaceManager] {ad} için fotoğraf kaydedildi: {face_path}")
    else:
        print("[FaceManager] Kamera görüntüsü alınamadı.")


GEMINI_API_KEY = "AIzaSyAi91-ZOM33gSV0-2dDaiLNQDlZ0h-RVF4"
VOICE_ID = "rDol2Ljxrvb0kzLzHooJ"
ELEVEN_API_KEY = "sk_ffde8aed6e2dca9ded66ae1e071a7f142247fa419dbc4d03"
GOZ_DOSYASI = "robot_goz.png"
TMDB_API_KEY = "f12c7e8322e92753f482f81ff60041ee"
AYARLAR_DOSYASI = "ayarlari.json"
SOHBET_GECMİSİ_DOSYASI = "Sohbet Geçmişi.txt"
cocukoyunulink = "https://raw.githubusercontent.com/ruzgartvtr/ROBOT/refs/heads/main/tarayici.py"
normaloyunlink = "https://www.dropbox.com/scl/fi/20ugfx7oioybvtrz9dv7j/cheese-is-the-reason.zip?rlkey=fn8lpak28ue0w2svsk6oi5v5x&e=1&st=xiv6keno&dl=1"
NORMAL_OYUN_KLASORU = r"C:\Users\ruzga\Downloads\cheese is the reason"
NORMAL_OYUN_EXE_YOLU = r"C:\Users\ruzga\Downloads\cheese is the reason\export 1 windows\Cheese is the reason.exe"
HABER_KAYNAKLARI = ["https://www.aa.com.tr/tr/rss/default?cat=guncel"]
ADB_YOLU = "adb"
CALENDARIFIC_API_KEY = "5S65ZPorvmu3JuZyukFM90JYKIafe3za"
PYCAW_AVAILABLE = False

# SPOTIFYIN BUNLAR
client_id = "e8658e3b5a244497af73614e995db59e"
client_secret = "db9a174b08434cae8814cc91a8958872"
redirect_uri = "http://localhost:8888/callback"
scope = "user-modify-playback-state user-read-playback-state streaming user-read-currently-playing"

# Spotify bağlantısı
sp = Spotify(auth_manager=SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scope
))


konusuyor_mu = False
robot_app_instance = None
aktif = False
gecmis_cumleler = []

# --- Çeviri Kulaklık Modu Durum ---
translator_running = False
translator_thread = None
#
# --- Google Fit: Çoklu Hesap Yardımcıları ---
SCOPES_FIT = ["https://www.googleapis.com/auth/fitness.activity.read"]

def get_fit_service(user="ruzgar"):
    from googleapiclient.discovery import build as gbuild
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    creds = None
    token_file = f"token_{user}.pkl"
    # Önce gmail_ prefiksi denenir, sonra düz isim
    prefer = [f"gmail_{user}.json", f"{user}.json"]
    creds_file = next((p for p in prefer if os.path.exists(p)), None)
    if not creds_file:
        raise FileNotFoundError(f"Kimlik dosyası bulunamadı: {prefer}")

    if os.path.exists(token_file):
        with open(token_file, "rb") as token:
            try:
                import pickle
                creds = pickle.load(token)
            except Exception:
                creds = None

    if not creds or not getattr(creds, "valid", False):
        if creds and getattr(creds, "expired", False) and getattr(creds, "refresh_token", None):
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES_FIT)
            creds = flow.run_local_server(port=0)
        with open(token_file, "wb") as token:
            import pickle
            pickle.dump(creds, token)

    return gbuild("fitness", "v1", credentials=creds)

def get_daily_steps(user="ruzgar"):
    import datetime
    service = get_fit_service(user)
    now = datetime.datetime.utcnow()
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = now
    dataset = f"{int(start.timestamp() * 1e9)}-{int(end.timestamp() * 1e9)}"
    steps = service.users().dataSources().datasets().get(
        userId="me",
        dataSourceId="derived:com.google.step_count.delta:com.google.android.gms:estimated_steps",
        datasetId=dataset
    ).execute()
    total = 0
    for point in steps.get("point", []):
        for value in point.get("value", []):
            total += value.get("intVal", 0)
    return total

# --- Gmail: Çoklu Hesap Yardımcıları ---
SCOPES_GMAIL = ["https://www.googleapis.com/auth/gmail.readonly"]

def get_gmail_service(user="ruzgar"):
    from googleapiclient.discovery import build as gbuild
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    import pickle
    creds = None
    token_file = f"gmail_token_{user}.pkl"
    prefer = [f"gmail_{user}.json", f"{user}.json"]
    creds_file = next((p for p in prefer if os.path.exists(p)), None)
    if not creds_file:
        raise FileNotFoundError(f"Gmail kimlik dosyası bulunamadı: {prefer}")

    if os.path.exists(token_file):
        with open(token_file, "rb") as token:
            try:
                creds = pickle.load(token)
            except Exception:
                creds = None

    if not creds or not getattr(creds, "valid", False):
        if creds and getattr(creds, "expired", False) and getattr(creds, "refresh_token", None):
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES_GMAIL)
            creds = flow.run_local_server(port=0)
        with open(token_file, "wb") as token:
            pickle.dump(creds, token)

    return gbuild("gmail", "v1", credentials=creds)

def gmail_list_unread(user="ruzgar", max_results=5, query="in:inbox is:unread"):
    try:
        svc = get_gmail_service(user)
        resp = svc.users().messages().list(userId="me", q=query, maxResults=max_results).execute()
        msgs = resp.get("messages", [])
        items = []
        for m in msgs:
            full = svc.users().messages().get(userId="me", id=m["id"], format="full").execute()
            headers = {h["name"]: h["value"] for h in full.get("payload", {}).get("headers", [])}
            frm = headers.get("From", "Bilinmiyor")
            sub = headers.get("Subject", "(Konu yok)")
            snippet = full.get("snippet", "")
            items.append((frm, sub, snippet))
        return items
    except Exception as e:
        print("[Gmail Hata]:", e)
        return []

# --- Bildirim & SMS Okuma (ADB) ---
def get_unread_notifications(app_filter="whatsapp", limit=5):
    try:
        out = subprocess.check_output([ADB_YOLU, "shell", "dumpsys", "notification", "--noredact"], encoding="utf-8", stderr=subprocess.DEVNULL, timeout=8)
        # Basit ayrıştırma: whatsapp/sms geçen satırları çek
        lines = [l.strip() for l in out.splitlines() if app_filter.lower() in l.lower()]
        # Kısa özet üret
        results = []
        for l in lines:
            txt = l
            # olası "tickerText=" veya "android.title=" alanlarını yakala
            m = re.search(r"(tickerText=|android\.title=)([^,]+)", l)
            if m:
                txt = m.group(2).strip()
            results.append(txt)
            if len(results) >= limit:
                break
        return results
    except Exception as e:
        print("[Bildirim Okuma Hata]:", e)
        return []

def get_sms_inbox(limit=5):
    # Bazı cihazlarda erişim kısıtlı olabilir; mümkünse content provider dene
    try:
        out = subprocess.check_output([ADB_YOLU, "shell", "content", "query", "--uri", "content://sms/inbox", "--projection", "address:body:date", "--sort", "date DESC", "--limit", str(limit)], encoding="utf-8", stderr=subprocess.DEVNULL, timeout=8)
        items = []
        for raw in out.strip().splitlines():
            addr = re.search(r"address=(.*?)(,|$)", raw)
            body = re.search(r"body=(.*?)(,|$)", raw)
            if addr or body:
                items.append(f"{addr.group(1) if addr else ''}: {body.group(1) if body else ''}")
        return items
    except Exception as e:
        print("[SMS Okuma Hata]:", e)
        return []

# --- Google Haritalar Rota ---
def ac_yol_tarifi(adres, travelmode="driving"):
    try:
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_status(f"Rota açılıyor: {adres}", color=(0.8,0.8,0,1)))
        q = urllib.parse.quote(adres)
        url = f"https://www.google.com/maps/dir/?api=1&destination={q}&travelmode={travelmode}"
        webbrowser.open(url)
        seslendir(f"{adres} için yol tarifi açıldı.")
    except Exception as e:
        print("[Rota Hata]:", e)
        seslendir("Yol tarifi açılamadı.")
    finally:
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_status(""))

# --- Canlı Çeviri (Kulaklık Modu) ---
def simple_translate(text, src="auto", tgt="tr"):
    try:
        # Google translate public endpoint (anahtar gerektirmez)
        params = {
            "client": "gtx",
            "sl": src,
            "tl": tgt,
            "dt": "t",
            "q": text
        }
        r = requests.get("https://translate.googleapis.com/translate_a/single", params=params, timeout=8)
        r.raise_for_status()
        data = r.json()
        translated = "".join([seg[0] for seg in data[0]])
        return translated
    except Exception as e:
        print("[Çeviri Hata]:", e)
        return ""

def _kulaklik_worker(src, tgt):
    global translator_running
    r = sr.Recognizer()
    with sr.Microphone() as source:
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_status(f"Kulaklık modu: {src}->{tgt} (Çıkmak için 'kulaklik_dur')", color=(0,1,0,1)))
        r.adjust_for_ambient_noise(source, duration=0.5)
        while translator_running:
            try:
                audio = r.listen(source, phrase_time_limit=6)
                text = r.recognize_google(audio, language=src)
                if not text.strip():
                    continue
                tr = simple_translate(text, src=src, tgt=tgt) or ""
                if tr:
                    seslendir(tr)
            except sr.UnknownValueError:
                continue
            except Exception as e:
                print("[Kulaklık Hata]:", e)
                continue
    if robot_app_instance:
        Clock.schedule_once(lambda dt: robot_app_instance.set_status(""))

def kulaklik_baslat(lang_pair="en-tr"):
    global translator_running, translator_thread
    try:
        src, tgt = lang_pair.split("-", 1)
    except Exception:
        src, tgt = "en", "tr"
    if translator_running:
        seslendir("Kulaklık modu zaten açık.")
        return
    translator_running = True
    import threading
    translator_thread = threading.Thread(target=_kulaklik_worker, args=(src, tgt), daemon=True)
    translator_thread.start()
    seslendir(f"Kulaklık modu başlatıldı: {src} → {tgt}")

def kulaklik_dur():
    global translator_running
    if translator_running:
        translator_running = False
        seslendir("Kulaklık modu kapatıldı.")
    else:
        seslendir("Kulaklık modu açık değil.")

print("AYARLAR DOSYASI YOLU:", os.path.abspath(AYARLAR_DOSYASI))
client = ElevenLabs(api_key=ELEVEN_API_KEY)
Window.clearcolor = (0.05, 0.05, 0.05, 1)

def ayarlari_yukle():
    """
    Uygulama ayarlarını JSON dosyasından yükler.
    Dosya yoksa varsayılan ayarları oluşturur.
    """
    if not os.path.exists(AYARLAR_DOSYASI):
        with open(AYARLAR_DOSYASI, "w", encoding="utf-8") as f:
            json.dump({"aktif_kullanici": 0, "kullanicilar": []}, f)
    with open(AYARLAR_DOSYASI, "r", encoding="utf-8") as f:
        return json.load(f)

def aktif_kullanici_bilgi():
    """
    Mevcut aktif kullanıcının bilgilerini döndürür.
    """
    ayar = ayarlari_yukle()
    i = ayar.get("aktif_kullanici", 0)
    if i < len(ayar["kullanicilar"]):
        return ayar["kullanicilar"][i]
    return {"ad": "Bilinmeyen", "rol": "Kullanici", "yonerge": "Cevap ver."}

def sohbet_gecmisini_kaydet(kim, mesaj):
    """
    Sohbet mesajlarını 'Sohbet Geçmişi.txt' dosyasına kaydeder.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(SOHBET_GECMİSİ_DOSYASI, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {kim}: {mesaj}\n")

def sohbet_gecmisini_oku():
    """
    Sohbet geçmişi dosyasını okur ve içeriğini döndürür.
    Dosya yoksa boş bir dosya oluşturur.
    """
    if not os.path.exists(SOHBET_GECMİSİ_DOSYASI):
        with open(SOHBET_GECMİSİ_DOSYASI, "w", encoding="utf-8") as f:
            f.write("# Gemini İle Sohbet\n")
    with open(SOHBET_GECMİSİ_DOSYASI, "r", encoding="utf-8") as f:
        return f.read()

def seslendir(ses):
    """
    Verilen metni seslendirir. Öncelik sırası:
    1. ElevenLabs (premium)
    2. gTTS (Google TTS, ücretsiz)
    3. pyttsx3 (offline, sınırsız)
    """
    global konusuyor_mu
    if not ses.strip():
        return

    print("[Robot]:", ses)
    if robot_app_instance:
        Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(ses, "Robot"))
        Clock.schedule_once(lambda dt: robot_app_instance.set_status("Konuşuyor...", color=(0, 1, 0, 1)))

    sohbet_gecmisini_kaydet("Robot", ses)

    spotify_caliniyor = False
    try:
        # Spotify çalıyorsa durdur
        current = sp.current_playback()
        if current and current.get("is_playing"):
            spotify_caliniyor = True
            sp.pause_playback()
    except Exception as e:
        print("[Spotify Kontrol Hatası]:", e)

    tmp_path = None
    try:
        konusuyor_mu = True
        # --- 1. ElevenLabs ---
        try:
            audio_gen = client.text_to_speech.convert(
                text=ses,
                voice_id=VOICE_ID,
                model_id="eleven_multilingual_v2",
                output_format="mp3_44100_128"
            )
            audio_bytes = b"".join(audio_gen)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                tmp.write(audio_bytes)
                tmp_path = tmp.name
            subprocess.run(["ffplay", "-nodisp", "-autoexit", tmp_path],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return
        except Exception as e1:
            print(f"[Seslendirme Hatası - ElevenLabs]: {e1}")

        # --- 2. gTTS ---
        try:
            from gtts import gTTS
            tts = gTTS(text=ses, lang="tr")
            tmp_path = tempfile.mktemp(suffix=".mp3")
            tts.save(tmp_path)
            subprocess.run(["ffplay", "-nodisp", "-autoexit", tmp_path],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return
        except Exception as e2:
            print(f"[Seslendirme Hatası - gTTS]: {e2}")

        # --- 3. pyttsx3 ---
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.say(ses)
            engine.runAndWait()
            return
        except Exception as e3:
            print(f"[Seslendirme Hatası - pyttsx3]: {e3}")

    finally:
        if spotify_caliniyor:
            try:
                sp.start_playback()
            except Exception as e:
                print("[Spotify Başlatma Hatası]:", e)
        konusuyor_mu = False
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_status(""))

def youtube_ac(aranan):
    """YouTube'da arama yapar ve ilk sonucu oynatır."""
    try:
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_status(f"{aranan} YouTube'da aranıyor...", color=(0.8, 0.8, 0, 1)))
        sonuc = subprocess.check_output(['yt-dlp', f'ytsearch1:{aranan}', '--get-id', '--skip-download'],
                                        stderr=subprocess.DEVNULL, timeout=10).decode().strip()
        webbrowser.open(f"http://www.youtube.com/watch?v={sonuc}")
        seslendir(f"{aranan} YouTube'da açılıyor.")
    except FileNotFoundError:
        seslendir("yt-dlp bulunamadı. Lütfen yükleyin.")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj("yt-dlp bulunamadı. Lütfen yükleyin.", "Hata"))
    except subprocess.TimeoutExpired:
        seslendir("YouTube arama zaman aşımına uğradı.")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj("YouTube arama zaman aşımına uğradı.", "Hata"))
    except subprocess.CalledProcessError as e:
        print(f"[YouTube Arama Hatası]: {e}")
        seslendir("YouTube'da arama yapılırken bir hata oluştu.")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"YouTube'da arama yapılırken bir hata oluştu: {e}", "Hata"))
    except webbrowser.Error as e:
        print(f"[Web Tarayıcı Hatası]: {e}")
        seslendir("Web tarayıcı açılırken bir hata oluştu.")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"Web tarayıcı açılırken bir hata oluştu: {e}", "Hata"))
    except Exception as e:
        print(f"[YouTube Açma Hatası]: {e}")
        seslendir(f"{aranan} YouTube'da açılırken beklenmeyen bir hata oluştu.")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"{aranan} YouTube'da açılırken beklenmeyen bir hata oluştu: {e}", "Hata"))
    finally:
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_status(""))

def spotify_ac(aranan):
    """Spotify'da arama yapar ve ilk sonucu çalar."""
    try:
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_status(f"{aranan} Spotify'da aranıyor...", color=(0.8, 0.8, 0, 1)))

        sonuç = sp.search(q=aranan, type="track", limit=1)
        parçalar = sonuç.get("tracks", {}).get("items", [])

        if parçalar:
            track_uri = parçalar[0]["uri"]
            sp.start_playback(uris=[track_uri])  # Spotify'da çal

            isim = parçalar[0]["name"]
            sanatçı = parçalar[0]["artists"][0]["name"]
            seslendir(f"{sanatçı} - {isim} Spotify'da çalınıyor.")
        else:
            seslendir("Spotify'da sonuç bulunamadı.")
            if robot_app_instance:
                Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj("Spotify'da sonuç bulunamadı.", "Bilgi"))

    except Exception as e:
        print(f"[Spotify Oynatma Hatası]: {e}")
        seslendir("Spotify oynatma sırasında bir hata oluştu.")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"Hata: {e}", "Hata"))

    finally:
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_status(""))


def spotify_playlist_ac():
    """Verilen sabit Spotify çalma listesini başlatır."""
    try:
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_status("Spotify çalma listesi başlatılıyor...", color=(0.5, 1, 0.5, 1)))

        # Playlist ID sabit
        playlist_id = "0wDD3nkvra1FayZBNMQWBm"

        sp.start_playback(context_uri=f"spotify:playlist:{playlist_id}")
        seslendir("Çalma listesi başlatıldı.")

    except Exception as e:
        print(f"[Spotify Playlist Hatası]: {e}")
        seslendir("Çalma listesi başlatılırken bir hata oluştu.")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"Hata: {e}", "Hata"))

    finally:
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_status(""))


def google_ara(aranan):
    """Google'da arama yapar ve tarayıcıda açar."""
    try:
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_status(f"{aranan} Google'da aranıyor...", color=(0.8, 0.8, 0, 1)))
        url = f"https://www.google.com/search?q={urllib.parse.quote(aranan)}"
        webbrowser.open(url)
        seslendir(f"{aranan} Google'da aranıyor.")
    except webbrowser.Error as e:
        print(f"[Google Arama Tarayıcı Hatası]: {e}")
        seslendir("Web tarayıcı açılırken bir hata oluştu.")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"Web tarayıcı açılırken bir hata oluştu: {e}", "Hata"))
    except Exception as e:
        print(f"[Google Arama Hatası]: {e}")
        seslendir(f"{aranan} Google'da aranırken bir hata oluştu.")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"{aranan} Google'da aranırken bir hata oluştu: {e}", "Hata"))
    finally:
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_status(""))
def ses_dinle():
    """Mikrofondan ses alır ve Google Speech Recognition ile metne dönüştürür."""
    global gecmis_cumleler
    r = sr.Recognizer()
    with sr.Microphone() as source:
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_status("Dinliyorum...", color=(0, 1, 0, 1)))
        r.adjust_for_ambient_noise(source)
        try:
            ses = r.listen(source, phrase_time_limit=7)
        except sr.WaitTimeoutError:
            if robot_app_instance:
                Clock.schedule_once(lambda dt: robot_app_instance.set_status("Dinleme tamamlandı.", color=(0, 0.8, 0.8, 1)))
            return ""
    try:
        metin = r.recognize_google(ses, language="tr-TR")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(metin, "Kullanıcı"))
            Clock.schedule_once(lambda dt: robot_app_instance.set_status("İşleniyor...", color=(0.8, 0.8, 0, 1)))
        sohbet_gecmisini_kaydet("Kullanıcı", metin)
        if metin in gecmis_cumleler:
            return ""
        gecmis_cumleler.append(metin)
        if len(gecmis_cumleler) > 5:
            gecmis_cumleler.pop(0)
        return metin
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        print(f"Google Speech Recognition servisine bağlanılamadı; {e}")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"Ses tanıma servisine bağlanılamadı: {e}", "Hata"))
        return ""
    except Exception as e:
        print(f"[Ses Dinleme Hatası]: {e}")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"Ses dinlenirken bir hata oluştu: {e}", "Hata"))
        return ""
    finally:
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_status(""))

def dosya_indir(url, hedef_klasor=".", dosya_adi=None):
    """URL'den dosya indirir, ilerleme çubuğu gösterir ve hata yönetimi yapar."""
    try:
        if not os.path.exists(hedef_klasor):
            os.makedirs(hedef_klasor)

        if dosya_adi is None:
            parsed_url = urllib.parse.urlparse(url)
            dosya_adi = os.path.basename(parsed_url.path)
            if not dosya_adi:
                dosya_adi = "indirilen_dosya.zip"
                print(f"Uyarı: URL'den dosya adı çıkarılamadı. '{dosya_adi}' olarak kaydedilecek.")

        kayit_yolu = os.path.join(hedef_klasor, dosya_adi)

        print(f"'{url}' adresinden dosya indiriliyor...")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_status(f"İndiriliyor: {dosya_adi}...", color=(0.8, 0.8, 0, 1)))

        response = requests.get(url, stream=True, allow_redirects=True, timeout=(5, 30))
        response.raise_for_status()

        toplam_boyut = int(response.headers.get('content-length', 0))
        indirilen_boyut = 0

        with open(kayit_yolu, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                indirilen_boyut += len(chunk)
                if toplam_boyut > 0 and robot_app_instance:
                    tamamlanma_orani_str = f"{(indirilen_boyut / toplam_boyut):.0%}"

                    Clock.schedule_once(lambda dt, p=tamamlanma_orani_str: robot_app_instance.set_status(f"İndiriliyor: {dosya_adi} {p}", color=(0.8, 0.8, 0, 1)))

        print(f"Dosya başarıyla '{kayit_yolu}' konumuna kaydedildi.")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"Dosya başarıyla '{dosya_adi}' konumuna indirildi.", "Sistem"))
        return kayit_yolu

    except requests.exceptions.ConnectionError as e:
        print(f"Hata: Bağlantı hatası oluştu: {e}")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"Dosya indirilirken bağlantı hatası oluştu: {e}", "Hata"))
        return None
    except requests.exceptions.Timeout as e:
        print(f"Hata: İndirme zaman aşımına uğradı: {e}")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"Dosya indirilirken zaman aşımı yaşandı: {e}", "Hata"))
        return None
    except requests.exceptions.HTTPError as e:
        print(f"Hata: HTTP hatası oluştu: {e.response.status_code} - {e.response.reason}")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"Dosya indirilirken HTTP hatası oluştu: {e.response.status_code}", "Hata"))
        return None
    except requests.exceptions.RequestException as e:
        print(f"Hata: Dosya indirilirken genel bir istek hatası oluştu: {e}")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"Dosya indirilirken bir sorun oluştu: {e}", "Hata"))
        return None
    except Exception as e:
        print(f"Beklenmeyen bir hata oluştu: {e}")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"Dosya indirilirken beklenmeyen bir hata oluştu: {e}", "Hata"))
        return None
    finally:
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_status(""))



class FaceManager:
    def __init__(self):
        self.known_faces = {}
        if not os.path.exists("faces"):
            print("[FaceManager] Klasör yok: faces")
            return
        for path in glob("faces/*.jpg"):
            name = os.path.splitext(os.path.basename(path))[0]
            try:
                img = face_recognition.load_image_file(path)
                enc = face_recognition.face_encodings(img)
                if enc:
                    self.known_faces[name] = enc[0]
            except Exception as e:
                print(f"[FaceManager] {path} için yüz kodlama hatası: {e}")

    def recognize_from_camera(self):
        # Kamera ile bir kare al ve yüz tanı
        cam = cv2.VideoCapture(0)
        ret, frame = cam.read()
        cam.release()
        if not ret:
            print("[FaceManager] Kamera görüntüsü alınamadı.")
            return None
        rgb = frame[:, :, ::-1]
        try:
            locs = face_recognition.face_locations(rgb)
            encs = face_recognition.face_encodings(rgb, locs)
            for enc in encs:
                for name, known_enc in self.known_faces.items():
                    matches = face_recognition.compare_faces([known_enc], enc)
                    if matches and matches[0]:
                        print(f"[FaceManager] Tanındı: {name}")
                        # --- Kullanıcı ayarları ile eşleştir ve aktif yap ---
                        ayar = ayarlari_yukle()
                        kullanicilar = ayar.get("kullanicilar", [])
                        for i, kisi in enumerate(kullanicilar):
                            if kisi.get("ad", "").lower() == name.lower():
                                ayar["aktif_kullanici"] = i
                                with open(AYARLAR_DOSYASI, "w", encoding="utf-8") as f:
                                    json.dump(ayar, f, ensure_ascii=False, indent=2)
                                seslendir(f"Yüz tanındı. {name} aktif kullanıcı yapıldı.")
                                if robot_app_instance:
                                    Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"{name} aktif kullanıcı yapıldı.", "Sistem"))
                                break
                        return name
        except Exception as e:
            print(f"[FaceManager] Tanıma hatası: {e}")
        print("[FaceManager] Tanıma başarısız.")
        return None

# --- KİŞİ GETİR (BENİMİ TEMİZLE + fuzzy eşleştirme) ---
def kisi_numarasi_getir(isim):
    temiz_isim = unidecode(isim.lower().replace("benim", "").replace(" ", ""))
    eslesme_listesi = {}
    for ad, numara in KISILER.items():
        temiz_ad = unidecode(ad.lower().replace(" ", ""))
        eslesme_listesi[temiz_ad] = numara

    yakinlar = difflib.get_close_matches(temiz_isim, eslesme_listesi.keys(), n=1, cutoff=0.5)

    if yakinlar:
        eslesen = yakinlar[0]

        # 🔴 ÖZEL DURUM: Anneanne arandığında ekstra bir tıklama yap
        if "anneanne" in eslesen:
            print("[ÖZEL]: Anneanne tespit edildi, ekstra işlem yapılıyor...")
            # Örnek: ekranın bir yerine tıkla
            adb_komut("adb shell input tap 676 2273")


        return eslesme_listesi[eslesen]

    return None


# --- ADB Arama (standart arama komutu) ---
def adb_ile_arama_yap(telefon_numarasi):
    try:
        if not telefon_numarasi.startswith("tel:"):
            telefon_numarasi = "tel:" + telefon_numarasi
        komut = f'adb shell am start -a android.intent.action.CALL -d {telefon_numarasi}'
        subprocess.run(komut, shell=True)
        seslendir(f"{telefon_numarasi[4:]} numarası aranıyor.")
    except Exception as e:
        print(f"[ADB Arama Hatası]: {e}")
        seslendir("Arama başlatılamadı.")

# --- Tam otomatik arama (ekran kilidinden sonra) ---
def adb_ile_tam_otomatik_arama(numara):

    numara = numara.replace(" ", "").replace("-", "")
    adb_komut("adb shell input keyevent 26")
    time.sleep(1.2)
    adb_komut("adb shell input swipe 500 1500 500 500")
    time.sleep(1.5)
    adb_komut("adb shell input text 2015")
    time.sleep(1)
    adb_komut("adb shell input keyevent 66")
    time.sleep(3)
    adb_komut(f'adb shell am start -a android.intent.action.CALL -d tel:{numara}')
    adb_komut("scrcpy")


# --- Adrese göre arama (fuzzy + temiz) ---
def adb_ile_kisi_arama(kisi_adi):
    numara = kisi_numarasi_getir(kisi_adi)
    if numara:
        adb_ile_tam_otomatik_arama(numara)
    else:
        seslendir("Kişi bulunamadı.")

# --- WhatsApp görüntülü arama (fuzzy + temiz + adb) ---
def whatsapp_goruntulu_arama_kisi_ara(kisi_adi):


    aranan = unidecode(kisi_adi.strip().lower().replace(" ", ""))  # yazılacak metin
    adb_komut("adb shell input keyevent 26")
    time.sleep(1)
    adb_komut("adb shell input swipe 500 1500 500 500")
    time.sleep(1)
    adb_komut("adb shell input text 2015")
    time.sleep(1)
    adb_komut("adb shell input keyevent 3")  # Home
    time.sleep(1)
    adb_komut("adb shell am force-stop com.whatsapp")
    time.sleep(1)
    adb_komut("adb shell input keyevent 66")
    time.sleep(2)
    adb_komut("adb shell input tap 409 1492")  # WhatsApp aç
    time.sleep(1)
    adb_komut("adb shell input tap 950 150")  # Arama kutusu
    time.sleep(1)
    adb_komut(f'adb shell input text "{aranan}"')  # sadeleştirilmiş yazı
    time.sleep(2)
    adb_komut("adb shell input tap 400 400")  # kişi tıkla
    time.sleep(1)
    adb_komut("adb shell input tap 762 180")  # görüntülü ara
    seslendir(f"{kisi_adi} görüntülü aranıyor.")
    adb_komut("scrcpy")


def whatsapp_mesaj_gonder(kisi_adi, mesaj):
    adb_komut("adb shell input keyevent 26")  # Ekranı aç
    time.sleep(1.2)
    adb_komut("adb shell input swipe 500 1500 500 500")  # Kilidi aç
    time.sleep(1.5)
    adb_komut("adb shell input text 2015")  # Şifre yaz
    time.sleep(1)
    adb_komut("adb shell input keyevent 66")  # Enter
    time.sleep(1)
    adb_komut("adb shell input keyevent 3")  # Ana ekran
    time.sleep(1)
    adb_komut("adb shell am force-stop com.whatsapp")  # WhatsApp'ı kapat
    time.sleep(1.5)
    adb_komut("adb shell monkey -p com.whatsapp -c android.intent.category.LAUNCHER 1")
    time.sleep(2)
    adb_komut("adb shell input tap 950 150")  # Arama kutusu
    time.sleep(1)
    if not mesaj.strip():
        print("[Uyarı]: Gönderilecek mesaj boş!")
    return
    adb_input_text_safe(kisi_adi)  # Aranacak kişiyi yaz
    time.sleep(2)
    adb_komut("adb shell input tap 400 400")  # Kişiye tıkla
    time.sleep(1.5)
    adb_input_text_safe(mesaj)  # Mesajı yaz (güvenli fonksiyonla)
    time.sleep(1)
    adb_komut("adb shell input keyevent 66")  # Gönder
    seslendir(f"{kisi_adi} kişisine mesaj gönderildi.")



def whatsapp_mesaj_yaz_uzun(mesaj):
    # WhatsApp'ta metin kutusuna yazmak için mesajı böl
    parcalar = [mesaj[i:i+90] for i in range(0, len(mesaj), 90)]
    for parcasi in parcalar:
        temiz = parcasi.replace(" ", "%s").replace("\n", "")
        komut = f'adb shell input text "{temiz}"'
        subprocess.run(komut, shell=True)
        time.sleep(0.8)  # Çok hızlı yazmasın diye beklet


def adb_input_text_safe(text):
    # Türkçe karakterleri temizle ve boşlukları %s ile değiştir
    text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('utf-8')
    text = text.replace(" ", "%s")
    komut = f'adb shell input text "{text}"'
    subprocess.run(komut, shell=True)



def zip_dosyasini_cikar(zip_yolu, hedef_klasor):
    """Zip dosyasını belirtilen klasöre çıkarır."""
    if not os.path.exists(zip_yolu):
        print(f"Hata: '{zip_yolu}' konumunda zip dosyası bulunamadı.")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"'{zip_yolu}' bulunamadı.", "Hata"))
        return False

    try:
        os.makedirs(hedef_klasor, exist_ok=True)
        with zipfile.ZipFile(zip_yolu, 'r') as zip_ref:
            zip_ref.extractall(hedef_klasor)
        print(f"'{zip_yolu}' başarıyla '{hedef_klasor}' konumuna çıkarıldı.")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"'{os.path.basename(zip_yolu)}' başarıyla çıkarıldı.", "Sistem"))
        return True
    except zipfile.BadZipFile:
        print(f"Hata: '{zip_yolu}' geçerli bir zip dosyası değil.")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"'{os.path.basename(zip_yolu)}' geçerli bir zip dosyası değil.", "Hata"))
        return False
    except FileNotFoundError:
        print(f"Hata: '{zip_yolu}' veya hedef klasör bulunamadı.")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"Dosya veya hedef klasör bulunamadı.", "Hata"))
        return False
    except PermissionError:
        print(f"Hata: '{hedef_klasor}' klasörüne yazma izni yok.")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"'{hedef_klasor}' klasörüne yazma izni yok.", "Hata"))
        return False
    except Exception as e:
        print(f"Zip dosyası çıkarılırken bir hata oluştu: {e}")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"Zip dosyası çıkarılırken bir hata oluştu: {e}", "Hata"))
        return False

def dosyayi_calistir(dosya_yolu):
    """Belirtilen dosya yolunu işletim sistemine uygun şekilde çalıştırır."""
    if not os.path.exists(dosya_yolu):
        print(f"Hata: '{dosya_yolu}' konumunda dosya bulunamadı.")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"'{os.path.basename(dosya_yolu)}' bulunamadı.", "Hata"))
        return

    try:
        print(f"'{dosya_yolu}' çalıştırılıyor...")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_status(f"'{os.path.basename(dosya_yolu)}' başlatılıyor...", color=(0.8, 0.8, 0, 1)))

        if platform.system() == 'Windows':
            os.startfile(dosya_yolu)
        elif platform.system() == 'Linux':
            subprocess.Popen(['xdg-open', dosya_yolu])
        elif platform.system() == 'Darwin':
            subprocess.Popen(['open', dosya_yolu])
        else:
            seslendir("Bu işletim sistemi için dosya çalıştırma desteklenmiyor.")
            if robot_app_instance:
                Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"'{platform.system()}' için dosya çalıştırma desteklenmiyor.", "Uyarı"))
            return

        print(f"'{dosya_yolu}' başarıyla çalıştırıldı (veya çalıştırma komutu gönderildi).")
        seslendir(f"'{os.path.basename(dosya_yolu)}' başlatıldı.")
    except FileNotFoundError:
        print(f"Hata: '{dosya_yolu}' dosyasını açacak uygun bir uygulama bulunamadı.")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"'{os.path.basename(dosya_yolu)}' açılamadı. Uygun bir uygulama bulunamadı.", "Hata"))
    except PermissionError:
        print(f"Hata: '{dosya_yolu}' çalıştırma izni yok.")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"'{os.path.basename(dosya_yolu)}' çalıştırma izni yok.", "Hata"))
    except Exception as e:
        print(f"Hata: Dosya çalıştırılırken bir sorun oluştu: {e}")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"Dosya çalıştırılırken bir hata oluştu: {e}", "Hata"))
    finally:
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_status(""))

def wikipedia_bilgi_al(konu):
    """Wikipedia'dan konu hakkında özet bilgi alır ve seslendirir."""
    try:
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_status(f"Wikipedia'dan {konu} aranıyor...", color=(0.8, 0.8, 0, 1)))
        wikipedia.set_lang("tr")

        page = wikipedia.page(konu, auto_suggest=True)
        summary = wikipedia.summary(konu, sentences=3, auto_suggest=True, redirect=True)

        seslendir(f"{konu} hakkında Wikipedia'dan özet: {summary}")
        webbrowser.open(page.url)
    except wikipedia.exceptions.PageError:
        seslendir(f"Üzgünüm, {konu} hakkında bir bilgi bulamadım.")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"{konu} hakkında bilgi bulunamadı.", "Robot"))
    except wikipedia.exceptions.DisambiguationError as e:
        seslendir(f"Sanırım ne demek istediğinizi tam anlayamadım. {konu} ile ilgili birkaç seçenek var: {', '.join(e.options[:3])}.")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"{konu} ile ilgili birden fazla seçenek bulundu: {', '.join(e.options[:3])}.", "Robot"))
    except requests.exceptions.ConnectionError:
        seslendir("Wikipedia'ya bağlanılamadı. İnternet bağlantınızı kontrol edin.")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj("Wikipedia'ya bağlanılamadı. İnternet bağlantınızı kontrol edin.", "Hata"))
    except requests.exceptions.Timeout:
        seslendir("Wikipedia'dan bilgi alırken zaman aşımı oluştu.")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj("Wikipedia'dan bilgi alırken zaman aşımı oluştu.", "Hata"))
    except Exception as e:
        print(f"[Wikipedia Hatası]: {e}")
        seslendir(f"Wikipedia'dan bilgi alınırken bir sorun oluştu.")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"Wikipedia'dan bilgi alınırken bir sorun oluştu: {e}", "Hata"))
    finally:
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_status(""))

def google_haritalar_ac(adres):
    """Verilen adresi Google Haritalar'da açar."""
    try:
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_status(f"{adres} haritalarda açılıyor...", color=(0.8, 0.8, 0, 1)))
        adres_url = urllib.parse.quote(adres)
        haritalar_url = f"https://www.google.com/maps/search/?api=1&query={adres_url}"
        webbrowser.open(haritalar_url)
        seslendir(f"{adres} Google Haritalar'da açılıyor.")
    except webbrowser.Error as e:
        print(f"[Google Haritalar Tarayıcı Hatası]: {e}")
        seslendir("Web tarayıcı açılırken bir hata oluştu.")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"Web tarayıcı açılırken bir hata oluştu: {e}", "Hata"))
    except Exception as e:
        print(f"[Google Haritalar Hatası]: {e}")
        seslendir(f"Google Haritalar açılırken bir hata oluştu.")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"Google Haritalar açılırken bir hata oluştu: {e}", "Hata"))
    finally:
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_status(""))

def haberleri_oku():
    """Belirli bir RSS kaynağından güncel haber başlıklarını okur."""
    try:
        if not HABER_KAYNAKLARI:
            seslendir("Haber kaynağı tanımlanmamış. Lütfen ayarlardan bir haber kaynağı ekleyin.")
            if robot_app_instance:
                Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj("Haber kaynağı tanımlanmamış.", "Uyarı"))
            return

        kaynak_url = HABER_KAYNAKLARI[-1]
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_status("Haberler alınıyor...", color=(0.8, 0.8, 0, 1)))
        response = requests.get(kaynak_url, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'xml')
        basliklar = soup.find_all('title')[1:6]

        if not basliklar:
            seslendir("Üzgünüm, haber başlığı bulunamadı.")
            if robot_app_instance:
                Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj("Haber başlığı bulunamadı.", "Robot"))
            return

        haber_metni = "Güncel haber başlıkları:\n"
        for i, baslik in enumerate(basliklar):
            haber_metni += f"{i+1}. {baslik.text}\n"

        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(haber_metni, "Haberler"))
        seslendir("Güncel haber başlıkları okunuyor.")
        for baslik in basliklar:
            seslendir(baslik.text)
    except requests.exceptions.ConnectionError:
        print("[Haber Okuma Ağı Hatası]: Bağlantı kurulamadı.")
        seslendir("Haberler alınırken ağ hatası oluştu. İnternet bağlantınızı kontrol edin.")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj("Haberler alınırken ağ hatası oluştu.", "Hata"))
    except requests.exceptions.Timeout:
        print("[Haber Okuma Zaman Aşımı]: Haber kaynağı yanıt vermedi.")
        seslendir("Haberler alınırken zaman aşımı oluştu. Haber kaynağına ulaşılamıyor olabilir.")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj("Haberler alınırken zaman aşımı oluştu.", "Hata"))
    except requests.exceptions.RequestException as e:
        print(f"[Haber Okuma Hatası]: {e}")
        seslendir("Haberler okunurken bir hata oluştu.")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"Haberler okunurken bir hata oluştu: {e}", "Hata"))
    except Exception as e:
        print(f"[Haber Okuma Genel Hatası]: {e}")
        seslendir("Haberler okunurken beklenmeyen bir hata oluştu.")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"Haberler okunurken beklenmeyen bir hata oluştu: {e}", "Hata"))
    finally:
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_status(""))

def sistemi_uyku_moduna_al():
    """Bilgisayarı uyku moduna alır."""
    try:
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_status("Bilgisayar uyku moduna alınıyor...", color=(0.8, 0.8, 0, 1)))
        if platform.system() == 'Windows':
            subprocess.run("rundll32.exe powrprof.dll,SetSuspendState 0,1,0", check=True, timeout=5)
        elif platform.system() == 'Linux':
            subprocess.run("systemctl suspend", shell=True, check=True, timeout=5)
        elif platform.system() == 'Darwin':
            subprocess.run("pmset sleepnow", check=True, timeout=5)
        else:
            seslendir("Bu işletim sistemi için uyku modu desteklenmiyor.")
            if robot_app_instance:
                Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj("Uyku modu bu işletim sistemi için desteklenmiyor.", "Uyarı"))
            return
        seslendir("Bilgisayar uyku moduna alındı.")
    except subprocess.TimeoutExpired:
        print("[Uyku Modu Hatası]: Komut zaman aşımına uğradı.")
        seslendir("Uyku modu komutu zaman aşımına uğradı.")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj("Uyku modu komutu zaman aşımına uğradı.", "Hata"))
    except subprocess.CalledProcessError as e:
        print(f"[Uyku Modu Hatası]: {e}")
        seslendir("Bilgisayar uyku moduna alınırken bir hata oluştu.")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj("Uyku moduna alınırken bir hata oluştu.", "Hata"))
    except FileNotFoundError:
        seslendir("Uyku modu komutu bulunamadı.")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj("Uyku modu komutu bulunamadı.", "Hata"))
    except Exception as e:
        print(f"[Uyku Modu Genel Hata]: {e}")
        seslendir("Uyku moduna alınırken beklenmeyen bir hata oluştu.")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj("Uyku moduna alınırken beklenmeyen bir hata oluştu.", "Hata"))
    finally:
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_status(""))

def sistemi_yeniden_baslat():
    """Bilgisayarı yeniden başlatır."""
    try:
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_status("Bilgisayar yeniden başlatılıyor...", color=(0.8, 0.8, 0, 1)))
        if platform.system() == 'Windows':
            subprocess.run("shutdown /r /t 1", shell=True, check=True, timeout=5)
        elif platform.system() == 'Linux':
            subprocess.run("sudo reboot", shell=True, check=True, timeout=5)
        elif platform.system() == 'Darwin':
            subprocess.run("sudo reboot", check=True, timeout=5)
        else:
            seslendir("Bu işletim sistemi için yeniden başlatma desteklenmiyor.")
            if robot_app_instance:
                Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj("Yeniden başlatma bu işletim sistemi için desteklenmiyor.", "Uyarı"))
            return
        seslendir("Bilgisayar yeniden başlatılıyor.")
    except subprocess.TimeoutExpired:
        print("[Yeniden Başlatma Hatası]: Komut zaman aşımına uğradı.")
        seslendir("Yeniden başlatma komutu zaman aşımına uğradı.")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj("Yeniden başlatma komutu zaman aşımına uğradı.", "Hata"))
    except subprocess.CalledProcessError as e:
        print(f"[Yeniden Başlatma Hatası]: {e}")
        seslendir("Bilgisayar yeniden başlatılırken bir hata oluştu.")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj("Yeniden başlatılırken bir hata oluştu.", "Hata"))
    except FileNotFoundError:
        seslendir("Yeniden başlatma komutu bulunamadı.")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj("Yeniden başlatma komutu bulunamadı.", "Hata"))
    except PermissionError:
        seslendir("Yeniden başlatmak için yetkiniz yok.")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj("Yeniden başlatmak için yetkiniz yok.", "Hata"))
    except Exception as e:
        print(f"[Yeniden Başlatma Genel Hata]: {e}")
        seslendir("Yeniden başlatılırken beklenmeyen bir hata oluştu.")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj("Yeniden başlatılırken beklenmeyen bir hata oluştu.", "Hata"))
    finally:
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_status(""))

def uygulama_ac(uygulama_adi):
    """Belirtilen uygulamayı açmaya çalışır."""
    try:
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_status(f"{uygulama_adi} açılıyor...", color=(0.8, 0.8, 0, 1)))
        if platform.system() == 'Windows':
            subprocess.Popen(uygulama_adi, shell=True)
        elif platform.system() == 'Linux':
            subprocess.Popen(uygulama_adi.lower(), shell=True)
        elif platform.system() == 'Darwin':
            subprocess.Popen(['open', '-a', uygulama_adi])
        else:
            seslendir("Bu işletim sisteminde uygulama açma desteklenmiyor.")
            if robot_app_instance:
                Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj("Uygulama açma bu işletim sisteminde desteklenmiyor.", "Uyarı"))
            return
        seslendir(f"{uygulama_adi} açılıyor.")
    except FileNotFoundError:
        seslendir(f"{uygulama_adi} bulunamadı. Uygulama adını veya yolunu kontrol edin.")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"{uygulama_adi} bulunamadı.", "Hata"))
    except Exception as e:
        print(f"[Uygulama Açma Hatası]: {e}")
        seslendir(f"{uygulama_adi} açılırken bir hata oluştu.")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"{uygulama_adi} açılırken bir hata oluştu: {e}", "Hata"))
    finally:
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_status(""))

def uygulama_kapat(uygulama_adi):
    """Belirtilen uygulamayı kapatmaya çalışır."""
    try:
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_status(f"{uygulama_adi} kapatılıyor...", color=(0.8, 0.8, 0, 1)))
        if platform.system() == 'Windows':
            subprocess.run(f"taskkill /im {uygulama_adi}.exe /f", check=True, timeout=5)
        elif platform.system() == 'Linux':
            subprocess.run(f"pkill -f {uygulama_adi}", shell=True, check=True, timeout=5)
        elif platform.system() == 'Darwin':
            subprocess.run(f"pkill -f {uygulama_adi}", check=True, timeout=5)
        else:
            seslendir("Bu işletim sisteminde uygulama kapatma desteklenmiyor.")
            if robot_app_instance:
                Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj("Uygulama kapatma bu işletim sisteminde desteklenmiyor.", "Uyarı"))
            return
        seslendir(f"{uygulama_adi} kapatılıyor.")
    except subprocess.TimeoutExpired:
        print("[Uygulama Kapatma Hatası]: Komut zaman aşımına uğradı.")
        seslendir(f"{uygulama_adi} kapatma komutu zaman aşımına uğradı.")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"{uygulama_adi} kapatma komutu zaman aşımına uğradı.", "Hata"))
    except subprocess.CalledProcessError as e:
        print(f"[Uygulama Kapatma Hatası]: {e}")
        seslendir(f"{uygulama_adi} kapatılırken bir hata oluştu (uygulama bulunamadı veya yetki sorunu olabilir).")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"{uygulama_adi} kapatılırken bir hata oluştu: {e}", "Hata"))
    except Exception as e:
        print(f"[Uygulama Kapatma Genel Hata]: {e}")
        seslendir(f"{uygulama_adi} kapatılırken beklenmeyen bir hata oluştu.")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"{uygulama_adi} kapatılırken beklenmeyen bir hata oluştu: {e}", "Hata"))
    finally:
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_status(""))


def zamanlayici_kur(saniye, mesaj):
    """Belirli bir süre sonra mesajı seslendirir."""
    def hatirlat():
        seslendir(f"Zamanlayıcı sona erdi: {mesaj}")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"Zamanlayıcı sona erdi: {mesaj}", "Sistem"))

    try:
        saniye = int(saniye)
        if saniye <= 0:
            seslendir("Zamanlayıcı süresi pozitif bir sayı olmalı.")
            if robot_app_instance:
                Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj("Zamanlayıcı süresi geçersiz.", "Uyarı"))
            return

        threading.Timer(saniye, hatirlat).start()
        seslendir(f"{saniye} saniye sonra hatırlatıcı kuruldu: {mesaj}")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"{saniye} saniye sonra '{mesaj}' hatırlatıcısı kuruldu.", "Sistem"))
    except ValueError:
        seslendir("Geçerli bir saniye değeri girin.")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj("Zamanlayıcı için geçerli bir süre girin.", "Hata"))
    except Exception as e:
        print(f"[Zamanlayıcı Hatası]: {e}")
        seslendir("Zamanlayıcı kurulurken bir hata oluştu.")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"Zamanlayıcı kurulurken bir hata oluştu: {e}", "Hata"))

def site_ozetle(url_str):
    """Verilen URL'deki site içeriğini özetlemek için Gemini'ye gönderir."""
    try:
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_status(f"Site içeriği alınıyor ve özetleniyor...", color=(0.8, 0.8, 0, 1)))

        parsed_url = urllib.parse.urlparse(url_str)
        if not parsed_url.scheme:
            url_str = "http://" + url_str

        response = requests.get(url_str, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        for script in soup(["script", "style"]):
            script.extract()
        text = soup.get_text(separator=' ', strip=True)

        if len(text) > 4000:
            text = text[:4000] + "..."

        prompt_text = f"Aşağıdaki site içeriğini Türkçe olarak özetle:\n\n{text}"

        ozet_yanit = gemini_yanit_al(prompt_text, is_summary_request=True)
        if ozet_yanit:
            seslendir(f"Site özeti: {ozet_yanit}")
        else:
            seslendir("Site özeti alınamadı.")

    except requests.exceptions.ConnectionError:
        seslendir("Siteye bağlanılamadı. İnternet bağlantınızı kontrol edin veya URL'yi doğrulayın.")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj("Site özeti için bağlantı hatası.", "Hata"))
    except requests.exceptions.Timeout:
        seslendir("Siteye bağlanırken zaman aşımı oluştu. Siteye ulaşılamıyor olabilir.")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj("Site özeti için zaman aşımı.", "Hata"))
    except requests.exceptions.RequestException as e:
        print(f"[Site Özetleme Ağı Hatası]: {e}")
        seslendir("Site içeriği alınırken bir hata oluştu.")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"Site özeti için hata: {e}", "Hata"))
    except Exception as e:
        print(f"[Site Özetleme Hatası]: {e}")
        seslendir("Site özetlenirken beklenmeyen bir sorun oluştu.")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"Site özetlenirken hata: {e}", "Hata"))
    finally:
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_status(""))

def hangi_adb_cihaz():
    try:
        output = subprocess.check_output(["adb", "devices"], encoding="utf-8")
        lines = output.strip().split("\n")[1:]
        cihazlar = [line.split("\t")[0] for line in lines if "device" in line]
        return cihazlar[0] if cihazlar else None
    except Exception as e:
        print("[ADB Cihaz Tespiti Hatası]:", e)
        return None

def rehberden_kisileri_getir():
    kisiler = {}
    try:
        output = subprocess.check_output(
            [ADB_YOLU, 'shell', 'content', 'query', '--uri', 'content://contacts/phones/', '--projection', 'display_name:number'],
            encoding='utf-8', stderr=subprocess.DEVNULL
        )
        for satir in output.strip().splitlines():
            if "display_name=" in satir and "number=" in satir:
                ad = ""
                numara = ""
                parcalar = satir.split(",")
                for parca in parcalar:
                    if "display_name=" in parca:
                        ad = parca.split("display_name=")[-1].strip().lower()
                    elif "number=" in parca:
                        numara = parca.split("number=")[-1].strip()
                if ad and numara:
                    kisiler[ad] = numara
    except Exception as e:
        print(f"[REHBER OKUMA HATASI]: {e}")
    return kisiler



def vcf_oku_yeni_kisiler(vcf_dosya_yolu):
    kisiler = {}
    try:
        with open(vcf_dosya_yolu, "r", encoding="utf-8") as f:
            lines = f.readlines()
            ad = None
            tel = None
            for line in lines:
                line = line.strip()
                if line.startswith("FN:"):
                    ad = line[3:].strip()
                elif line.startswith("TEL:") or "TEL;" in line:
                    tel = line.split(":")[-1].strip()
                elif line == "END:VCARD" and ad and tel:
                    kisiler[ad.lower()] = tel
                    ad = None
                    tel = None
    except Exception as e:
        print("[VCF OKUMA HATASI]:", e)
    return kisiler

cihaz_seri = hangi_adb_cihaz()

if cihaz_seri == "R5CW11M6E7R":
    print("Orijinal cihaz bağlı! KISILER elle atanacak.")
    KISILER = {
    "aaa": "05548181045",
    "ahsenteyze": "5445628499",
    "ali": "5548169584",
    "huriş": "+90 506 029 45 15",
    "huriye": "+90 506 029 45 15",
    "anneciğim": "+90 506 029 45 15",
    "anne": "05445482209",
    "annem": "+90 544 548 22 09",
    "babaanneciim": "05465656616",
    "babam": "05465656610",
    "burak": "05543141757",
    "chatgpt": "+18002428478",
    "dedem": "+905354371401",
    "denizkuzen": "+905449191540",
    "ebrubakolu": "+905538484498",
    "kankamata": "+905418648788",
    "nefes": "+905442754740",
    "okan": "905516563681",
    "oylumerot": "+905445482209",
    "ruzgar": "0532 771 95 69",
    "rzgar": "+905546729201",
    "tanerabi": "+905414838272"
}

else:
    print("Yeni cihaz bağlı! Telefonda rehberden kişiler çekiliyor...")
    KISILER = rehberden_kisileri_getir()
    print(f"{len(KISILER)} kişi yüklendi: {list(KISILER.keys())}")



def adb_komut(cmd):
    print("[ADB]:", cmd)
    subprocess.run(cmd, shell=True)



def gemini_yanit_al(metin, max_deneme=3, bekleme_suresi=2, is_summary_request=False, kamera_ekle=False):
    """
    Gemini API'sinden yanıt alır. Bağlantı ve diğer hataları detaylı yönetir.
    'is_summary_request' bayrağı, prompt'un farklı formatlanmasını sağlar.
    'kamera_ekle' bayrağı, isteğe kamera görüntüsü eklenip eklenmeyeceğini belirler.
    """
    kullanici = aktif_kullanici_bilgi()

    parts = []

    # 1. Metin içeriğini oluştur
    if is_summary_request:
        prompt_metni = metin
    else:
        komut_listesi = """
        - youtube:... (müzik veya video arar)
        - spotify:... (müzik arar)
        - playlist: (playlist açar)
        - gec: (spotify geçer)
        - geri: (spotifyda önceki şarkı)
        - durdur: (spotifyı durdurur)
        - baslat: (spotifyı başlatır)
        - google:... (genel arama yapar)
        - harita:... (adres veya konum arar)
        - saat: (şu anki saati söyler)
        - tarih: (bugünün tarihini söyler)
        - kilitle: (bilgisayarı kilitler)
        - film: (rastgele film önerir)
        - haberler: (güncel haber başlıklarını okur)
        - uyku: (bilgisayarı uyku moduna alır)
        - yeniden_baslat: (bilgisayarı yeniden başlatır)
        - uygulama_ac:... (uygulama açar, örn: uygulama_ac:notepad)
        - uygulama_kapat:... (uygulama kapatır, örn: uygulama_kapat:chrome)
        - ses_ayarla:... (ses seviyesini ayarlar, örn: ses_ayarla:50)
        - hatirlat:saniye:mesaj (ör: hatirlat:300:Yemek hazır)
        - kamera: (kamerayı açar)
        - wikipedia:... (Wikipedia'dan bilgi alır)
        - not:... (not alır)
        - site:... (site açar)
        - site_ozetle:... (bir sitenin içeriğini özetler)
        - ceviri:... (Google Translate'i açar)
        - kapat: (bilgisayarı kapatır)
        - klasor:... (klasör açar)
        - ekran: (ekran görüntüsü alır)
        - gorev: (Görev Yöneticisi'ni açar)
        - netflix:... (Netflix'te arama yapar)
        - disney:... (Disney Plus'ta arama yapar)
        - kitap:... (e-kitap arar)
        - tema:siyah/beyaz (uygulama temasını değiştirir)
        - tatil:... (tatilleri gösterir)
        - ucus:... (uçuşları gösterir)
        - trend (trendleri gösterir)
        - sözleri:.... (şarkı sözleri gösterir)
        - uzay fotoğrafı: (uzay fotoğrafı gösterir)
        - kedi resmi:
        - köpek resmi:
        - ara:..... (belirtilen numarayı arar)
        - ara:.... (kişiyi rehberden bulur ve arar)
        - whatsappgoruntulu:.... (whatsappdan rehberden bulur ve görüntülü arar)
        - wpsms:kisi:mesaj:      (whatsappdan sms)
        - radyo:... (belirtilen radyoyu açar)
        - ışık aç: (ışık açar)
        - ışık kapat: (ışık kapatır)
        - özel gün: (özel gün mü diye kontrol eder)
        - iss: (ISS konumu gösterir)
        - mars: (Mars hava durumu)
        - gökyüzü: (yıldız haritası gösterir)
        - tweet:... (Twitter’a yazı gönderir)
        - instaindir:... (Instagram’dan içerik indirir)
        - sms:kisi:mesaj (SMS gönderir)
        - zar (1–6 arası rastgele sayı üretir)
        - tombala (rastgele tombala numarası üretir)
        - espri (rastgele şaka yapar)
        - adım (adım sayısını gösterir)
        - bitcoin (Bitcoin fiyatı gösterir)
        - dolar (USD/TRY kuru)
        - borsa:... (hisse fiyatını getirir)
        - rota:... (Google Haritalar'da yol tarifi açar)
        - kamera_acikla (kameradan bir kare alır ve ne gördüğünü açıklar)
        - haber_ozet (son haberlerden kısa özetler okur)
        - alarm:HH:MM:mesaj (belirtilen saatte bir defa çalar)
        - alarm_tekrar:HH:MM:mesaj (her gün aynı saatte çalar)
        - alarm_iptal (tüm kurulu alarmları iptal eder)
        - neredeyim (IP tabanlı yaklaşık konumu söyler)
        - yakin:... (bulunduğun konuma yakın yerleri haritada açar)
        """
        sohbet_gecmisi = sohbet_gecmisini_oku()
        prompt_metni = f"Geçmiş Sohbet:\n{sohbet_gecmisi}\n\nKullanici adi: {kullanici['ad']}\nRol: {kullanici['rol']}\nYonerge: {kullanici['yonerge']}\nKullanici soyle dedi: '{metin}'\n\nEger ozel komut varsa bu formatlardan biriyle cevap ver:\n{komut_listesi}. Respond concisely and Keep it brief. Sadece komutu veya ilgili yanıtı ver, ekleme yapma. Normal konuşma dışında komut verme. Komut verdiğinde sadece komutu yaz."

    parts.append({"text": prompt_metni})

    # 2. Kamera görüntüsünü isteğe bağlı ekle
    if kamera_ekle:
        try:
            import cv2, base64
            cam = cv2.VideoCapture(0)
            ret, frame = cam.read()
            cam.release()
            if ret:
                temp_file = "gemini_capture.jpg"
                cv2.imwrite(temp_file, frame)
                with open(temp_file, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
                parts.append({
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": encoded_string
                    }
                })
                print("[Gemini] Kamera görüntüsü eklendi.")
            else:
                print("[Gemini] Kamera görüntüsü alınamadı.")
        except Exception as e:
            print(f"[Gemini Hatası] Kamera kare eklenemedi: {e}")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"role": "user", "parts": parts}]}

    for deneme in range(max_deneme):
        try:
            if robot_app_instance:
                Clock.schedule_once(lambda dt: robot_app_instance.set_status("Cevap oluşturuluyor...", color=(0.8, 0.8, 0, 1)))
            response = requests.post(url, headers=headers, data=json.dumps(data), timeout=15)
            response.raise_for_status()

            result = response.json()
            if "candidates" in result and len(result["candidates"]) > 0 and \
               "content" in result["candidates"][0] and "parts" in result["candidates"][0]["content"] and \
               len(result["candidates"][0]["content"]["parts"]) > 0:
                return result["candidates"][0]["content"]["parts"][0]["text"].strip().lower()
            else:
                print(f"[Gemini Hatası] Deneme {deneme + 1}/{max_deneme}: Geçersiz yanıt yapısı veya boş adaylar. Yanıt: {response.text}")
                if robot_app_instance:
                    Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"Gemini'den geçersiz yanıt alındı. Tekrar deneniyor.", "Hata"))
                time.sleep(bekleme_suresi)
                bekleme_suresi *= 2
                continue

        except requests.exceptions.ConnectionError as e:
            print(f"[Gemini API Bağlantı Hatası] Deneme {deneme + 1}/{max_deneme}: Bağlantı kurulamadı. Yeniden deniyor... Bekleme süresi: {bekleme_suresi}s. Hata: {e}")
            if robot_app_instance:
                Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"Gemini API'ye bağlanılamadı. İnternet bağlantınızı kontrol edin. Tekrar deneniyor.", "Hata"))
            time.sleep(bekleme_suresi)
            bekleme_suresi *= 2
        except requests.exceptions.Timeout as e:
            print(f"[Gemini API Zaman Aşımı Hatası] Deneme {deneme + 1}/{max_deneme}: İstek zaman aşımına uğradı. Yeniden deniyor... Bekleme süresi: {bekleme_suresi}s. Hata: {e}")
            if robot_app_instance:
                Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"Gemini API yanıt vermedi (zaman aşımı). Tekrar deneniyor.", "Hata"))
            time.sleep(bekleme_suresi)
            bekleme_suresi *= 2
        except requests.exceptions.HTTPError as e:
            print(f"[Gemini API HTTP Hatası] Deneme {deneme + 1}/{max_deneme}: HTTP {e.response.status_code}. Yeniden deniyor... Bekleme süresi: {bekleme_suresi}s. Yanıt: {e.response.text}")
            if robot_app_instance:
                Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"Gemini API'den HTTP {e.response.status_code} hatası alındı. Tekrar deneniyor.", "Hata"))
            time.sleep(bekleme_suresi)
            bekleme_suresi *= 2
        except json.JSONDecodeError:
            print(f"[Gemini Hatası] Deneme {deneme + 1}/{max_deneme}: JSON yanıtı ayrıştırılamadı. Yeniden deniyor... Bekleme süresi: {bekleme_suresi}s")
            if robot_app_instance:
                Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"Gemini'den bozuk yanıt alındı. Tekrar deneniyor.", "Hata"))
            time.sleep(bekleme_suresi)
            bekleme_suresi *= 2
        except Exception as e:
            print(f"[Gemini Genel Hatası] Deneme {deneme + 1}/{max_deneme}: Beklenmeyen hata: {e}")
            if robot_app_instance:
                Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"Gemini ile iletişimde beklenmeyen bir hata oluştu: {e}. Tekrar deneniyor.", "Hata"))
            time.sleep(bekleme_suresi)
            bekleme_suresi *= 2

    print(f"[Gemini API] Maksimum {max_deneme} denemeye rağmen yanıt alınamadı.")
    if robot_app_instance:
        Clock.schedule_once(lambda dt: robot_app_instance.set_status(f"Gemini API'den yanıt alınamadı. Lütfen daha sonra tekrar deneyin veya internet bağlantınızı kontrol edin.", "Hata"))
    return ""

    if robot_app_instance:
        Clock.schedule_once(lambda dt: robot_app_instance.set_status(""))


def kameraac():
    try:
        html_kamera_yolu = os.path.join(tempfile.gettempdir(), "kamera_goruntule.html")
        with open(html_kamera_yolu, "w", encoding="utf-8") as f:
            f.write('''<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Kamera</title>
  <style>
    html, body {
      margin: 0;
      padding: 0;
      background: black;
      height: 100%;
      overflow: hidden;
    }
    video {
      position: fixed;
      top: 0; left: 0;
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
  </style>
</head>
<body>
  <video id="kamera" autoplay playsinline></video>
  <script>
    navigator.mediaDevices.getUserMedia({ video: true })
      .then(stream => {
        document.getElementById('kamera').srcObject = stream;
      })
      .catch(err => {
        alert("Kamera açılamadı: " + err);
      });
  </script>
</body>
</html>''')

        webbrowser.open(f"file:///{html_kamera_yolu}")
        seslendir("Kamera tarayıcıda açıldı.")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj("Kamera tarayıcıda açıldı.", "Sistem"))

    except Exception as e:
        print(f"[Kamera HTML Açma Hatası]: {e}")
        seslendir("Kamera tarayıcıda açılamadı.")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"Kamera açma hatası: {e}", "Hata"))

def film_oner_tmdb():
    """TMDB API'sinden rastgele bir popüler film önerir."""
    try:
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_status("Film önerisi alınıyor...", color=(0.8, 0.8, 0, 1)))
        sayfa = random.randint(1, 5)
        response = requests.get(
            f'https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=tr-TR&page={sayfa}',
            timeout=5
        )
        response.raise_for_status()
        data = response.json()
        if 'results' in data and data['results']:
            film = random.choice(data['results'])
            ad = film['title']
            seslendir(f"Film önerim: {ad}.")
        else:
            seslendir("Film bulunamadı veya öneri alınamadı.")
            if robot_app_instance:
                Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj("Film bulunamadı veya öneri alınamadı.", "Robot"))
    except requests.exceptions.ConnectionError:
        print("[Film Öneri Bağlantı Hatası]: Bağlantı kurulamadı.")
        seslendir("Film önerisi alınamadı, internet bağlantınızı kontrol edin.")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj("Film önerisi için bağlantı hatası.", "Hata"))
    except requests.exceptions.Timeout:
        print("[Film Öneri Zaman Aşımı]: TMDB yanıt vermedi.")
        seslendir("Film önerisi alınırken zaman aşımı oluştu.")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj("Film önerisi için zaman aşımı.", "Hata"))
    except requests.exceptions.RequestException as e:
        print(f"[Film Öneri API Hatası]: {e}")
        seslendir("Film önerisi alınırken bir hata oluştu.")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"Film önerisi alınırken bir hata oluştu: {e}", "Hata"))
    except json.JSONDecodeError:
        print("[Film Öneri Hatası]: TMDB yanıtı ayrıştırılamadı.")
        seslendir("Film önerisi alınamadı.")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj("Film önerisi alınırken yanıt ayrıştırma hatası.", "Hata"))
    except Exception as e:
        print("[Film Öneri Genel Hatası]:", e)
        seslendir("Film önerisi alınamadı.")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"Film önerisi alınırken beklenmeyen bir hata oluştu: {e}", "Hata"))
    finally:
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_status(""))


# === (2) Görsel Tanıma & Açıklama ===
def kamera_acikla():
    """Kameradan tek kare alır, Gemini ile kısa açıklama üretir ve seslendirir."""
    try:
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_status("Kamera çerçevesi alınıyor...", color=(0.8, 0.8, 0, 1)))
        aciklama = gemini_yanit_al("Bu görüntüyü kısa ve basit Türkçe ile açıkla.", kamera_ekle=True)
        if aciklama:
            seslendir(aciklama)
            if robot_app_instance:
                Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(aciklama, "Görüntü Açıklama"))
        else:
            seslendir("Görüntü açıklaması alınamadı.")
    except Exception as e:
        print("[Kamera Açıklama Hatası]:", e)
        seslendir("Görüntü açıklaması sırasında bir hata oluştu.")
    finally:
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_status(""))

# === (4) Sesli Haber Özetleyici ===
def haber_ozetleri(sayi=3, feed_url="https://feeds.bbci.co.uk/turkce/rss.xml"):
    """RSS'ten son haberleri çeker, her bir haberin sayfasını özetleyip seslendirir."""
    try:
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_status("Haberler özetleniyor...", color=(0.8, 0.8, 0, 1)))
        import xml.etree.ElementTree as ET
        r = requests.get(feed_url, timeout=8)
        r.raise_for_status()
        root = ET.fromstring(r.text)
        ns = {"dc": "http://purl.org/dc/elements/1.1/"}
        items = root.findall(".//item")[:sayi]
        if not items:
            seslendir("Haber bulunamadı.")
            return
        for it in items:
            baslik = (it.findtext("title") or "(Başlık yok)").strip()
            link = (it.findtext("link") or "").strip()
            seslendir(f"Haber: {baslik}")
            if not link:
                continue
            try:
                resp = requests.get(link, timeout=10)
                resp.raise_for_status()
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(resp.content, 'html.parser')
                for s in soup(["script", "style", "noscript"]):
                    s.extract()
                text = soup.get_text(separator=' ', strip=True)
                if len(text) > 4000:
                    text = text[:4000] + "..."
                ozet = gemini_yanit_al(f"Şu haberi 2-3 cümlede, sade Türkçe ile özetle:\n\n{text}", is_summary_request=True)
                if ozet:
                    seslendir(ozet)
            except Exception as e:
                print("[Haber Özet Hatası]:", e)
                continue
    except Exception as e:
        print("[Haber Özetleyici Genel Hata]:", e)
        seslendir("Haber özetleri alınamadı.")
    finally:
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_status(""))

# === (6) Gelişmiş Alarm & Hatırlatıcı ===
aktif_alarmlar = []

def _alarm_calis(mesaj, tekrarla, saat_str):
    seslendir(f"Alarm: {mesaj}")
    if robot_app_instance:
        Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"Alarm: {mesaj}", "Alarm"))
    if tekrarla:
        # Bir sonraki gün için yeniden kur
        alarm_kur(saat_str, mesaj, tekrarla=True)

def alarm_kur(saat_str, mesaj, tekrarla=False):
    """HH:MM formatında alarm kurar. tekrarla=True ise her gün tekrarlar."""
    try:
        import datetime, threading
        hh, mm = saat_str.split(":")
        hh = int(hh); mm = int(mm)
        now = datetime.datetime.now()
        hedef = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
        if hedef <= now:
            hedef += datetime.timedelta(days=1)
        delta = (hedef - now).total_seconds()
        t = threading.Timer(delta, _alarm_calis, args=(mesaj, tekrarla, saat_str))
        t.daemon = True
        t.start()
        aktif_alarmlar.append(t)
        if tekrarla:
            seslendir(f"Her gün {saat_str} için alarm kuruldu: {mesaj}")
        else:
            seslendir(f"{saat_str} için alarm kuruldu: {mesaj}")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"Alarm kuruldu: {saat_str} - {mesaj}", "Sistem"))
    except Exception as e:
        print("[Alarm Kurma Hatası]:", e)
        seslendir("Alarm kurulamadı.")

def alarm_iptal():
    """Tüm bekleyen alarmları iptal eder."""
    try:
        say = 0
        for t in list(aktif_alarmlar):
            try:
                t.cancel()
                say += 1
            except Exception:
                pass
            finally:
                try:
                    aktif_alarmlar.remove(t)
                except ValueError:
                    pass
        seslendir(f"{say} alarm iptal edildi.")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"{say} alarm iptal edildi.", "Sistem"))
    except Exception as e:
        print("[Alarm İptal Hatası]:", e)
        seslendir("Alarm iptal edilemedi.")

# === (7) Harita + Lokasyon Bilgisi ===
def neredeyim():
    """IP tabanlı yaklaşık konumu söyler."""
    try:
        r = requests.get("https://ipinfo.io/json", timeout=6)
        r.raise_for_status()
        data = r.json()
        sehir = data.get("city", "bilinmeyen")
        ulke = data.get("country", "")
        loc = data.get("loc", "")
        seslendir(f"Yaklaşık konum: {sehir} {ulke}")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"Konum: {sehir} {ulke} ({loc})", "Sistem"))
        return loc
    except Exception as e:
        print("[Konum Hatası]:", e)
        seslendir("Konum alınamadı.")
        return None

def yakin_ara(terim):
    """Bulunduğun konuma yakın yerleri Google Haritalar'da açar."""
    try:
        loc = neredeyim()
        if not loc:
            return
        lat, lng = loc.split(",")
        q = urllib.parse.quote(terim)
        url = f"https://www.google.com/maps/search/{q}/@{lat},{lng},14z"
        webbrowser.open(url)
        seslendir(f"Yakınındaki {terim} için arama açıldı.")
    except Exception as e:
        print("[Yakın Arama Hatası]:", e)
        seslendir("Yakın arama açılamadı.")

# Tam entegre komut_coz_ve_isle fonksiyonu

def komut_coz_ve_isle(metin):
    if not metin.strip():
        return

    yanit = gemini_yanit_al(metin)
    print("[Gemini Yanıtı]:", yanit)

    # --- Yeni Komutlar (erken işle) ---
    if yanit.startswith("kamera_acikla"):
        kamera_acikla()
        return
    if yanit.startswith("haber_ozet"):
        haber_ozetleri()
        return
    if yanit.startswith("alarm_tekrar:"):
        try:
            _, saat, mesaj = yanit.split(":", 2)
            alarm_kur(saat.strip(), mesaj.strip(), tekrarla=True)
        except Exception:
            seslendir("Alarm formatı: alarm_tekrar:HH:MM:mesaj")
        return
    if yanit.startswith("alarm:"):
        try:
            _, saat, mesaj = yanit.split(":", 2)
            alarm_kur(saat.strip(), mesaj.strip(), tekrarla=False)
        except Exception:
            seslendir("Alarm formatı: alarm:HH:MM:mesaj")
        return
    if yanit.startswith("alarm_iptal"):
        alarm_iptal()
        return
    if yanit.startswith("neredeyim"):
        neredeyim()
        return
    if yanit.startswith("yakin:"):
        terim = yanit.split(":", 1)[1].strip()
        yakin_ara(terim)
        return
    if yanit.startswith("kulaklik:"):
        pair = yanit.split(":", 1)[1].strip() or "en-tr"
        kulaklik_baslat(pair)
        return
    if "kulaklik_dur" in yanit:
        kulaklik_dur()
        return
    if yanit.startswith("mail:"):
        kisi = yanit.split(":",1)[1].strip().lower()
        kisi = {"ruzgar":"ruzgar","huriye":"huriye","oylum":"oylum"}.get(kisi, "ruzgar")
        items = gmail_list_unread(kisi, max_results=5)
        if not items:
            seslendir("Okunmamış e-posta bulunamadı veya erişilemedi.")
        else:
            for frm, sub, snip in items:
                seslendir(f"{frm} - {sub}")
        return
    if yanit.startswith("bildirim:"):
        app = yanit.split(":",1)[1].strip().lower()
        if app == "sms":
            lst = get_sms_inbox(limit=5)
        else:
            lst = get_unread_notifications(app_filter=app, limit=5)
        if not lst:
            seslendir("Bildirim bulunamadı.")
        else:
            for it in lst:
                seslendir(it[:200])
        return
    if yanit.startswith("rota:"):
        adres = yanit.split(":",1)[1].strip()
        if adres:
            ac_yol_tarifi(adres, travelmode="driving")
        else:
            seslendir("Hedef adres bulunamadı.")
        return

    # WhatsApp Görüntülü Arama
    # --- YENİ KOMUTLAR ---
    if "iss" in yanit:
        seslendir("ISS şu an Dünya üzerinde X konumunda.")  # Buraya gerçek API entegrasyonu yapılabilir
    elif "mars" in yanit:
        seslendir("Mars yüzeyinde hava sıcaklığı yaklaşık -60 derece.")  # Örnek yanıt
    elif "gökyüzü" in yanit:
        webbrowser.open("https://stellarium.org/")  # Gökyüzü haritası
        seslendir("Gökyüzü haritası açılıyor.")
    elif "tweet:" in yanit:
        icerik = yanit.split("tweet:", 1)[1].strip()
        seslendir(f"Tweet gönderiliyor: {icerik}")  # Twitter API ile gönderilebilir
    elif "instaindir:" in yanit:
        link = yanit.split("instaindir:", 1)[1].strip()
        seslendir(f"Instagram içeriği indiriliyor: {link}")
    elif "sms:" in yanit:
        try:
            _, kisi, mesaj = yanit.split(":", 2)
            hedef = kisi.strip()
            seslendir(f"{hedef} numarasına SMS gönderiliyor: {mesaj}")
            adb_komut("adb shell input keyevent 26")  # Ekranı aç
            time.sleep(1.2)
            adb_komut("adb shell input swipe 500 1500 500 500")  # Kilidi aç
            time.sleep(1.5)
            adb_komut("adb shell input text 2015")  # Şifre yaz
            time.sleep(1)
            adb_komut("adb shell input keyevent 66")  # Enter
            time.sleep(1)
            adb_komut("adb shell input keyevent 3")  # Ana ekran
            time.sleep(2)
            adb_komut(f'adb shell am start -a android.intent.action.SENDTO -d sms:{hedef} --es sms_body "{mesaj}"')
            time.sleep(5)
            adb_komut("adb shell input keyevent 22")  # Gönder tuşuna odaklan
            time.sleep(2)
            adb_komut("adb shell input keyevent 66")  # Enter = Gönder
        except Exception as e:
            print("[SMS Hata]:", e)
            seslendir("SMS gönderilemedi.")
    elif "zar" in yanit:
        seslendir(f"Zar sonucu: {random.randint(1, 6)}")
    elif "tombala" in yanit:
        seslendir(f"Tombala numarası: {random.randint(1, 90)}")
    elif "espri" in yanit:
        espriler = ["Bu robot çok komik!", "Bilgisayarım virüs kapmış... Şimdi hasta bilgisayar oldum!", "Benim şakam RAM gibi hızlı!"]
        seslendir(random.choice(espriler))
    elif "kalori:" in yanit:
        yemek = yanit.split("kalori:", 1)[1].strip()
        seslendir(f"{yemek} yaklaşık 250 kalori.")  # Buraya gerçek hesap eklenebilir
    elif "adım" in yanit:
        try:
            r = get_daily_steps("ruzgar")
            h = get_daily_steps("huriye")
            o = get_daily_steps("oylum")
            mesaj = f"Rüzgar {r} adım, Huriye {h} adım, Oylum {o} adım attı."
            seslendir(mesaj)
            if robot_app_instance:
                Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(mesaj, "Sistem"))
        except Exception as e:
            print("[Adım Hata]:", e)
            seslendir("Adım bilgileri alınamadı.")
    elif "uyku" in yanit:
        seslendir("Son uyku analizine göre 7 saat 20 dakika uyudunuz.")  # Örnek veri
    elif "bitcoin" in yanit:
        seslendir("Bitcoin fiyatı şu an 65 bin dolar civarında.")  # Gerçek API bağlanabilir
    elif "dolar" in yanit:
        seslendir("1 Amerikan Doları = 32 Türk Lirası.")  # Örnek veri
    elif "borsa:" in yanit:
        hisse = yanit.split("borsa:", 1)[1].strip()
        seslendir(f"{hisse} hissesi bugün %2 arttı.")  # Örnek veri
    # WhatsApp Görüntülü Ara
    elif "whatsappgoruntulu:" in yanit:
        kisi = yanit.split("whatsappgoruntulu:", 1)[1].strip().lower().replace(" ", "")
        for ad, numara in KISILER.items():
            if kisi in ad:
                whatsapp_goruntulu_arama_kisi_ara(ad)
                return
        seslendir("Kişi bulunamadı.")

    # WhatsApp Mesaj Gönderme
    elif "wpsms:" in yanit:
        try:
            parcalar = yanit.split("wpsms:")[1].strip().split(":")
            kisi = parcalar[0].strip()
            mesaj = parcalar[1].strip()
            whatsapp_mesaj_gonder(kisi, mesaj)
            return
        except:
            seslendir("WhatsApp mesajı gönderilemedi.")

    # YouTube Aç
    elif "youtube:" in yanit:
        sarki = yanit.split("youtube:", 1)[1].strip()
        youtube_ac(sarki)


    elif "playlist" in yanit:
        spotify_playlist_ac()
    elif "gec" in yanit:
        sp.next_track()
    elif "geri" in yanit:
        sp.previous_track()
    elif "baslat" in yanit:
        sp.start_playback()
    elif "durdur" in yanit:
        sp.pause_playback()
    elif "spotify:" in yanit:
        sarki = yanit.split("spotify:", 1)[1].strip()
        spotify_ac(sarki)
    elif "google:" in yanit:
        arama = yanit.split("google:", 1)[1].strip()
        google_ara(arama)
    elif "harita:" in yanit:
        adres = yanit.split("harita:", 1)[1].strip()
        google_haritalar_ac(adres)
    elif "kilitle:" in yanit:
        seslendir("Bilgisayarı kilitliyorum.")
        subprocess.run("rundll32.exe user32.dll,LockWorkStation")
    elif "hava:" in yanit:
        try:
            sehir = yanit.split("hava:", 1)[1].strip()
            if robot_app_instance:
                Clock.schedule_once(lambda dt: robot_app_instance.set_status(f"{sehir} için hava durumu alınıyor...", color=(0.8, 0.8, 0, 1)))
            url = f"https://wttr.in/{urllib.parse.quote(sehir)}?format=3"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            seslendir(response.text)
        except Exception as e:
            print(f"[Hava Durumu Hatası]: {e}")
            seslendir("Hava durumu alınamadı.")
    elif "film:" in yanit:
        film_oner_tmdb()
    elif "oyun:" in yanit:
        webbrowser.open("https://store.playstation.com/tr-tr/category/12a53448-199e-459b-956d-074feeed2d7d/1")
        seslendir("PlayStation Store'da yeni çıkan oyunlar açılıyor.")
    elif "kamera" in yanit:
        kameraac()
    elif "wikipedia:" in yanit:
        konu = yanit.split("wikipedia:", 1)[1].strip()
        wikipedia_bilgi_al(konu)
    elif "site:" in yanit and not "site_ozetle:" in yanit:
        site = yanit.split("site:", 1)[1].strip()
        if not site.startswith("http"):
            site = "https://" + site
        webbrowser.open(site)
        seslendir(f"{site} açılıyor.")
    elif "site_ozetle:" in yanit:
        site_ozetle(yanit.split("site_ozetle:", 1)[1].strip())
    elif "ceviri:" in yanit:
        ceviri_metni = yanit.split("ceviri:", 1)[1].strip()
        webbrowser.open(f"https://translate.google.com/?sl=auto&tl=tr&text={urllib.parse.quote(ceviri_metni)}")
        seslendir("Çeviri Google Translate'de açılıyor.")
    elif "kapat:" in yanit:
        seslendir("Bilgisayarı kapatıyorum.")
        subprocess.run("shutdown /s /t 1", shell=True)
    elif "klasor:" in yanit:
        yol = yanit.split("klasor:", 1)[1].strip()
        dosyayi_calistir(yol if yol else os.getcwd())
    elif "ekran:" in yanit:
        from PIL import ImageGrab
        path = os.path.join(os.getcwd(), f"ekran_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        ImageGrab.grab().save(path)
        seslendir("Ekran görüntüsü alındı.")
    elif "gorev:" in yanit:
        subprocess.Popen("taskmgr")
        seslendir("Görev yöneticisi açılıyor.")
    elif "netflix:" in yanit:
        film_adi = yanit.split("netflix:", 1)[1].strip()
        webbrowser.open(f"https://www.netflix.com/search?q={urllib.parse.quote(film_adi)}")
        seslendir(f"Netflix'te {film_adi} aranıyor.")
    elif "disney:" in yanit:
        film_adi = yanit.split("disney:", 1)[1].strip()
        webbrowser.open(f"https://www.disneyplus.com/search?q={urllib.parse.quote(film_adi)}")
        seslendir(f"Disney Plus'ta {film_adi} aranıyor.")
    elif "kitap:" in yanit:
        kitap_adi = yanit.split("kitap:", 1)[1].strip()
        google_ara(f"{kitap_adi} e-kitap")
        seslendir(f"{kitap_adi} için e-kitap araması yapılıyor.")
    elif "tema:" in yanit:
        tema_metni = yanit.split("tema:", 1)[1].strip().lower()
        if "siyah" in tema_metni:
            Window.clearcolor = (0.05, 0.05, 0.05, 1)
            seslendir("Tema siyaha ayarlandı.")
        elif "beyaz" in tema_metni:
            Window.clearcolor = (0.9, 0.9, 0.9, 1)
            seslendir("Tema beyaza ayarlandı.")
    elif "uyku:" in yanit:
        sistemi_uyku_moduna_al()
    elif "yeniden_baslat:" in yanit:
        sistemi_yeniden_baslat()
    elif "uygulama_ac:" in yanit:
        uygulama_ac(yanit.split("uygulama_ac:", 1)[1].strip())
    elif "uygulama_kapat:" in yanit:
        uygulama_kapat(yanit.split("uygulama_kapat:", 1)[1].strip())
    elif "selamlama:" in yanit:
        seslendir("Merhaba! Size nasıl yardımcı olabilirim?")
    elif "ara:" in yanit:
        hedef = yanit.split("ara:", 1)[1].strip()
        if hedef.replace(" ", "").isdigit() or hedef.startswith("+90"):
            adb_ile_tam_otomatik_arama(hedef)
        else:
            adb_ile_kisi_arama(hedef)

        # Radyo Aç
    elif "radyo:" in yanit:
        kanal = yanit.split("radyo:", 1)[1].strip().lower()
        radyo_linkleri = {
            "Kral": "http://46.20.3.204:80/",
            "90lar": "https://moondigitalmaster.radyotvonline.net/90lar/playlist.m3u8",
            "Power Türk": "https://live.powerapp.com.tr/powerturk/abr/playlist.m3u8"
        }
        if kanal in radyo_linkleri:
            webbrowser.open(radyo_linkleri[kanal])
            seslendir(f"{kanal} radyosu açılıyor.")
        else:
            seslendir("Bu radyo kanalı listede yok.")

    # Tatil Günleri
    elif "tatil" in yanit:
        try:
            url = f"https://calendarific.com/api/v2/holidays?&api_key={CALENDARIFIC_API_KEY}&country=TR&year={datetime.now().year}"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            if "response" in data and "holidays" in data["response"]:
                tatiller = data["response"]["holidays"]
                mesaj = ", ".join([f"{t['date']['iso']} {t['name']}" for t in tatiller[:5]])
                seslendir(f"Türkiye'deki bazı resmi tatiller: {mesaj}")
            else:
                seslendir("Tatil bilgisi alınamadı.")
        except Exception as e:
            print(f"[Tatil Hatası]: {e}")
            seslendir("Tatil bilgisi alınamadı.")

    # Bugün Özel Bir Gün mü
    elif "özel gün" in yanit or "bugün özel" in yanit:
        try:
            url = f"https://calendarific.com/api/v2/holidays?&api_key={CALENDARIFIC_API_KEY}&country=TR&year={datetime.now().year}&month={datetime.now().month}&day={datetime.now().day}"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            if "response" in data and "holidays" in data["response"] and data["response"]["holidays"]:
                gun = data["response"]["holidays"][0]["name"]
                seslendir(f"Evet, bugün {gun}.")
            else:
                seslendir("Bugün özel bir gün değil.")
        except Exception as e:
            print(f"[Özel Gün Hatası]: {e}")
            seslendir("Bugün için özel gün bilgisi alınamadı.")

    # Işık Aç/Kapat
    elif "ışık aç" in yanit:
        try:
            # Buraya kendi akıllı ev API isteğini koyabilirsin
            # Örn: requests.post("http://192.168.1.50/light/on")
            seslendir("Işıklar açıldı.")
        except Exception as e:
            print(f"[Işık Açma Hatası]: {e}")
            seslendir("Işıklar açılamadı.")
    elif "ışık kapat" in yanit:
        try:
            # Buraya kendi akıllı ev API isteğini koyabilirsin
            # Örn: requests.post("http://192.168.1.50/light/off")
            seslendir("Işıklar kapatıldı.")
        except Exception as e:
            print(f"[Işık Kapama Hatası]: {e}")
            seslendir("Işıklar kapatılamadı.")


    elif yanit:
        if len(yanit) <= 200:
            seslendir(yanit)
        else:
            if robot_app_instance:
                Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(yanit, "Robot"))
            seslendir("Yanıtım uzun olduğu için ekrana yazıyorum.")
    else:
        seslendir("Anlamadım veya komutu işleyemedim.")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj("Anlayamadım veya komutu işleyemedim.", "Robot"))


# --- Yüz Tanıma Dinleyici Thread'i ---
def yuz_tanima_dinleyici():
    global yuz_tanima_aktif
    fm = FaceManager()
    while yuz_tanima_aktif:
        ad = fm.recognize_from_camera()
        if ad:
            try:
                data = ayarlari_yukle()
                for i, kisi in enumerate(data.get("kullanicilar", [])):
                    if kisi.get("ad", "").lower() == ad.lower():
                        data["aktif_kullanici"] = i
                        with open(AYARLAR_DOSYASI, "w", encoding="utf-8") as f:
                            json.dump(data, f, ensure_ascii=False, indent=2)
                        seslendir(f"Yüz tanındı. {ad} aktif kullanıcı yapıldı.")
                        if robot_app_instance:
                            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"{ad} aktif kullanıcı yapıldı.", "Sistem"))
                        break
            except Exception as e:
                print("[Yüz Tanıma Kullanıcı Değiştirme Hatası]:", e)
        time.sleep(5)




def buton_sesli_komut():
    """Sesli komut düğmesine basıldığında tetiklenir."""
    threading.Thread(target=lambda: komut_coz_ve_isle(ses_dinle()), daemon=True).start()

def arkaplan_dinleyici():
    """Robotun sürekli olarak arka planda ses dinlemesini sağlar."""
    global aktif
    while True:
        if konusuyor_mu:
            time.sleep(0.5)
            continue

        metin = ses_dinle()
        if not metin:
            continue

        metin_lower = metin.lower()
        if not aktif and ("robot" in metin_lower or "hey robot" in metin_lower):
            aktif = True
            seslendir("Dinliyorum.")
        elif aktif:
            if "robot dur" in metin_lower or "bekle robot" in metin_lower:
                aktif = False
                seslendir("Bekleme moduna geçtim.")
            else:
                komut_coz_ve_isle(metin)




from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.uix.camera import Camera
from kivy.uix.image import Image as KivyImage


class Theme:
    bg1 = (0.1,0.1,0.1,1)
    txt = (1,1,1,1)
    sub = (0.7,0.7,0.7,1)

class RoundPanel(BoxLayout): pass
class PrimaryButton(Label): pass
class GhostButton(Label): pass

class FaceManager:
    def __init__(self, faces_dir="faces"):
        self.known_encodings = []
        self.known_names = []
        self.load_faces(faces_dir)

    def load_faces(self, faces_dir):
        if not os.path.exists(faces_dir):
            print("[FaceManager] Klasör yok:", faces_dir)
            return
        for file in os.listdir(faces_dir):
            path = os.path.join(faces_dir, file)
            if not file.lower().endswith((".jpg", ".png", ".jpeg")):
                continue
            img = face_recognition.load_image_file(path)
            encs = face_recognition.face_encodings(img)
            if encs:
                self.known_encodings.append(encs[0])
                name = file.split("_")[0]
                self.known_names.append(name)
        print(f"[FaceManager] {len(self.known_names)} kişi yüklendi:", self.known_names)

    def recognize_from_camera(self, cam_index=0, num_frames=3):
        cap = cv2.VideoCapture(cam_index)
        names_detected = []
        for _ in range(num_frames):
            ret, frame = cap.read()
            if not ret:
                continue
            rgb = frame[:, :, ::-1]
            locs = face_recognition.face_locations(rgb)
            encs = face_recognition.face_encodings(rgb, locs)
            for enc in encs:
                matches = face_recognition.compare_faces(self.known_encodings, enc)
                if True in matches:
                    idx = matches.index(True)
                    names_detected.append(self.known_names[idx])
        cap.release()
        if names_detected:
            return max(set(names_detected), key=names_detected.count)
        return None


class AddPersonPopup(Popup):
    """Gorsellerdeki 'KISI EKLE' ekrani; 3 sutun: Kamera / Ad / Talimat + sag ustte BITIR."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = ""
        self.size_hint = (0.95, 0.9)
        self.auto_dismiss = False
        root = BoxLayout(orientation="vertical", padding=20, spacing=20)

        # Header
        header = BoxLayout(size_hint_y=None, height=70)
        header.add_widget(Label(text="KISI EKLE", font_size=36, bold=True, color=(.8,.8,.8,1)))
        header.add_widget(Widget())
        self.btn_finish = Button(text="BITIR", size_hint=(None,None), size=(180,60),
                                 background_normal="", background_color=(.6,1,.6,1), color=(0,0,0,1))
        self.btn_finish.bind(on_release=self._on_finish)
        header.add_widget(self.btn_finish)
        root.add_widget(header)

        body = BoxLayout(spacing=30)

        # 1) Kamera sütunu
        left = BoxLayout(orientation="vertical", spacing=16, size_hint_x=.33)
        self.cam_holder = BoxLayout(size_hint_y=None, height=260)
        with self.cam_holder.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(.6,1,.6,1)
            self._rect = Rectangle(pos=self.cam_holder.pos, size=self.cam_holder.size)
        self.cam_holder.bind(size=lambda _,v: setattr(self._rect, "size", v),
                             pos=lambda _,v: setattr(self._rect, "pos", v))
        try:
            self.camera = Camera(resolution=(1280,720), play=True)
            self.cam_holder.add_widget(self.camera)
        except Exception as e:
            self.camera = None
            self.cam_holder.add_widget(Label(text="Kamera bulunamadi", color=(0,0,0,1)))
            print("[KisiEkle] Camera yok:", e)

        left.add_widget(self.cam_holder)
        btn_snap = Button(text="FOTOGRAF CEK", size_hint=(None,None), height=68, width=360,
                          background_normal="", background_color=(.6,1,.6,1), color=(0,0,0,1))
        btn_snap.bind(on_release=self._snap)
        left.add_widget(btn_snap)

        btn_cancel = Button(text="IPTAL", size_hint=(None,None), height=68, width=360,
                            background_normal="", background_color=(1,.3,.3,1), color=(0,0,0,1))
        btn_cancel.bind(on_release=lambda *_: self.dismiss())
        left.add_widget(btn_cancel)
        body.add_widget(left)

        # 2) Ad sütunu
        mid = BoxLayout(orientation="vertical", spacing=16, size_hint_x=.34)
        mid.add_widget(Label(text="Ad Girin", font_size=48, bold=True, color=(.6,.6,.6,1),
                             size_hint_y=None, height=60))
        name_box = BoxLayout(size_hint_y=None, height=80, padding=8)
        with name_box.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(1,1,1,1); self._name_rect = Rectangle(pos=name_box.pos, size=name_box.size)
        name_box.bind(size=lambda _,v: setattr(self._name_rect,"size",v),
                      pos=lambda _,v: setattr(self._name_rect,"pos",v))
        self.in_name = TextInput(hint_text="AD GIRILECEK YER", multiline=False,
                                 background_color=(0,0,0,0), foreground_color=(0,0,0,1),
                                 cursor_color=(0,0,0,1), write_tab=False)
        name_box.add_widget(self.in_name)
        mid.add_widget(name_box)
        self.lbl_photo_path = Label(text="", size_hint_y=None, height=24, color=(.7,.7,.7,1), font_size=12)
        mid.add_widget(self.lbl_photo_path)
        body.add_widget(mid)

        # 3) Talimat sütunu
        right = BoxLayout(orientation="vertical", spacing=16, size_hint_x=.33)
        right.add_widget(Label(text="Talimat Girin", font_size=48, bold=True, color=(.6,.6,.6,1),
                               size_hint_y=None, height=60))
        note_box = BoxLayout(padding=8)
        with note_box.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(1,1,1,1); self._note_rect = Rectangle(pos=note_box.pos, size=note_box.size)
        note_box.bind(size=lambda _,v: setattr(self._note_rect,"size",v),
                      pos=lambda _,v: setattr(self._note_rect,"pos",v))
        self.in_note = TextInput(hint_text="TALIMAT GIRILECEK YER", multiline=True,
                                 background_color=(0,0,0,0), foreground_color=(0,0,0,1),
                                 cursor_color=(0,0,0,1))
        note_box.add_widget(self.in_note)
        right.add_widget(note_box)
        body.add_widget(right)

        root.add_widget(body)
        self.content = root
        self.captured_path = ""

    def _snap(self, *_):
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        path = os.path.join(tempfile.gettempdir(), f"kisi_{ts}.png")
        try:
            if self.camera:
                self.camera.export_to_png(path)
            else:
                from PIL import Image as PILImage
                PILImage.new("RGB", (800,450), (120,220,120)).save(path)
            self.captured_path = path
            self.lbl_photo_path.text = f"Kaydedildi: {os.path.basename(path)}"
            print("[KisiEkle] Foto kayit:", path)
        except Exception as e:
            self.lbl_photo_path.text = "Foto kaydedilemedi"
            print("[KisiEkle] Snap hata:", e)

    def _on_finish(self, *_):
        ad = (self.in_name.text or "").strip()
        talimat = (self.in_note.text or "").strip()
        foto = self.captured_path
        if not ad:
            self.lbl_photo_path.text = "Lutfen ad girin."
            return
        data = ayarlari_yukle()
        data.setdefault("kullanicilar", [])
        data["kullanicilar"].append({"ad": ad, "rol": "Kullanici", "yonerge": talimat, "foto": foto})
        data["aktif_kullanici"] = len(data["kullanicilar"]) - 1
        with open(AYARLAR_DOSYASI, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        seslendir(f"{ad} eklendi.")
        self.dismiss()
        EditPersonPopup(initial={"ad": ad, "talimat": talimat, "foto": foto}).open()


class Theme:
    bg1   = (0.06, 0.07, 0.10, 1)   # ana arka plan
    bg2   = (0.10, 0.11, 0.15, 0.85) # kart
    acc   = (0.38, 0.78, 0.58, 1)   # vurgulu (yeşil)
    warn  = (0.98, 0.76, 0.36, 1)   # kehribar
    danger= (0.95, 0.35, 0.35, 1)   # kırmızı
    txt   = (0.92, 0.94, 0.97, 1)
    sub   = (0.65, 0.70, 0.78, 1)

class RoundPanel(BoxLayout):
    """Cam/blur hissi veren yuvarlatılmış panel (statik)."""
    def __init__(self, radius=18, fill=Theme.bg2, **kwargs):
        super().__init__(**kwargs)
        self.radius = radius
        self.fill = fill
        self.padding = [dp(14), dp(12), dp(14), dp(12)]
        self.spacing = dp(10)
        with self.canvas.before:
            Color(*self.fill)
            self._rr = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])
        self.bind(size=self._update, pos=self._update)

    def _update(self, *_):
        self._rr.pos = self.pos
        self._rr.size = self.size

class GhostButton(Button):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.background_normal = ""
        self.background_color = (0,0,0,0)
        self.color = Theme.txt
        self.bold = True
        self.font_size = dp(16)
        self.size_hint = (None, None)
        if not self.size:
            self.size = (dp(140), dp(44))
        with self.canvas.before:
            Color(1,1,1,0.08)
            self._rr = RoundedRectangle(pos=self.pos, size=self.size, radius=[14])
        self.bind(pos=self._sync, size=self._sync)

    def _sync(self, *_):
        self._rr.pos = self.pos
        self._rr.size = self.size

class PrimaryButton(Button):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.background_normal = ""
        self.background_color = Theme.acc
        self.color = (0,0,0,1)
        self.bold = True
        self.font_size = dp(16)
        self.size_hint = (None, None)
        if not self.size:
            self.size = (dp(160), dp(48))
        with self.canvas.before:
            Color(*Theme.acc)
            self._rr = RoundedRectangle(pos=self.pos, size=self.size, radius=[16])
        self.bind(pos=self._sync, size=self._sync)

    def _sync(self, *_):
        self._rr.pos = self.pos
        self._rr.size = self.size

class DangerButton(PrimaryButton):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.background_color = Theme.danger
        with self.canvas.before:
            Color(*Theme.danger)
            self._rr = RoundedRectangle(pos=self.pos, size=self.size, radius=[16])

# ——— KİŞİ EKLE ———
class AddPersonPopup(Popup):
    """Görseldeki tarzda ama daha modern: 3 sütun + sağ üstte BİTİR."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = ""
        self.size_hint = (0.96, 0.9)
        self.auto_dismiss = False
        self.background = ""  # default gölgelendirmeyi kapat
        self.separator_height = 0

        root = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(18))
        # Üst çubuk
        top = BoxLayout(size_hint_y=None, height=dp(56), spacing=dp(10))
        title = Label(text="KİŞİ EKLE", color=Theme.txt, bold=True, font_size=dp(26), halign="left", valign="middle")
        title.bind(size=lambda _,v: setattr(title, "text_size", v))
        top.add_widget(title); top.add_widget(Widget())
        btn_finish = PrimaryButton(text="BİTİR")
        btn_finish.bind(on_release=self._on_finish)
        top.add_widget(btn_finish)
        root.add_widget(top)

        # Gövde
        body = BoxLayout(spacing=dp(18))

        # 1) Kamera
        left = BoxLayout(orientation="vertical", spacing=dp(12), size_hint_x=.36)
        cam_card = RoundPanel()
        cam_box = BoxLayout(size_hint_y=None, height=dp(260))
        with cam_box.canvas.before:
            Color(0.6,1,0.6,0.15); Rectangle(pos=cam_box.pos, size=cam_box.size)
        cam_box.bind(pos=lambda *_: None, size=lambda *_: None)
        try:
            self.camera = Camera(resolution=(1280,720), play=True)
            cam_box.add_widget(self.camera)
        except Exception as e:
            self.camera = None
            cam_box.add_widget(Label(text="Kamera bulunamadı", color=Theme.sub))
            print("[KisiEkle] Camera yok:", e)
        cam_card.add_widget(cam_box)
        left.add_widget(cam_card)

        row_btns = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(52))
        snap = PrimaryButton(text="📸 Fotoğraf Çek", size=(dp(180), dp(48)))
        snap.bind(on_release=self._snap)
        cancel = DangerButton(text="İptal", size=(dp(120), dp(48)))
        cancel.bind(on_release=lambda *_: self.dismiss())
        row_btns.add_widget(snap); row_btns.add_widget(cancel); row_btns.add_widget(Widget())
        left.add_widget(row_btns)
        body.add_widget(left)

        # 2) Ad
        mid = BoxLayout(orientation="vertical", spacing=dp(12), size_hint_x=.32)
        mid.add_widget(Label(text="Ad", color=Theme.sub, font_size=dp(20), size_hint_y=None, height=dp(26)))
        name_card = RoundPanel()
        self.in_name = TextInput(hint_text="Ad girin",
                                 multiline=False,
                                 background_color=(0,0,0,0),
                                 foreground_color=(0,0,0,1),
                                 cursor_color=(0,0,0,1),
                                 padding=[dp(10), dp(12), dp(10), dp(12)])
        name_card.add_widget(self.in_name)
        mid.add_widget(name_card)
        self.lbl_photo_path = Label(text="", color=Theme.sub, font_size=dp(12), size_hint_y=None, height=dp(20))
        mid.add_widget(self.lbl_photo_path)
        body.add_widget(mid)

        # 3) Talimat
        right = BoxLayout(orientation="vertical", spacing=dp(12), size_hint_x=.32)
        right.add_widget(Label(text="Talimat", color=Theme.sub, font_size=dp(20), size_hint_y=None, height=dp(26)))
        note_card = RoundPanel()
        self.in_note = TextInput(hint_text="Talimat yazın",
                                 multiline=True,
                                 background_color=(0,0,0,0),
                                 foreground_color=(0,0,0,1),
                                 cursor_color=(0,0,0,1),
                                 padding=[dp(10), dp(12), dp(10), dp(12)])
        note_card.add_widget(self.in_note)
        right.add_widget(note_card)
        body.add_widget(right)

        root.add_widget(body)
        self.content = root
        self.captured_path = ""

    def _snap(self, *_):
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        path = os.path.join(tempfile.gettempdir(), f"kisi_{ts}.png")
        try:
            if self.camera:
                self.camera.export_to_png(path)
            else:
                from PIL import Image as PILImage
                PILImage.new("RGB", (800,450), (120,220,120)).save(path)
            self.captured_path = path
            self.lbl_photo_path.text = f"[bb]Kaydedildi:[/bb] {os.path.basename(path)}"
            print("[KisiEkle] Foto kayit:", path)
        except Exception as e:
            self.lbl_photo_path.text = "[bb]Hata:[/bb] Foto kaydedilemedi"
            print("[KisiEkle] Snap hata:", e)

    def _on_finish(self, *_):
        ad = (self.in_name.text or "").strip()
        talimat = (self.in_note.text or "").strip()
        foto = self.captured_path
        if not ad:
            self.lbl_photo_path.text = "Lütfen ad girin."
            return
        data = ayarlari_yukle()
        data.setdefault("kullanicilar", [])
        data["kullanicilar"].append({"ad": ad, "rol": "Kullanici", "yonerge": talimat, "foto": foto})
        data["aktif_kullanici"] = len(data["kullanicilar"]) - 1
        with open(AYARLAR_DOSYASI, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        seslendir(f"{ad} eklendi.")
        self.dismiss()
        EditPersonPopup(initial={"ad": ad, "talimat": talimat, "foto": foto}).open()

# ——— KİŞİ DÜZENLE ———
class EditPersonPopup(Popup):
    def __init__(self, initial=None, **kwargs):
        super().__init__(**kwargs)
        self.title = ""
        self.size_hint = (0.96, 0.9)
        self.auto_dismiss = True
        self.initial = initial or {}
        self.background = ""
        self.separator_height = 0

        root = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(18))

        top = BoxLayout(size_hint_y=None, height=dp(56))
        title = Label(text="KİŞİ DÜZENLE", color=Theme.txt, bold=True, font_size=dp(26), halign="left", valign="middle")
        title.bind(size=lambda _,v: setattr(title, "text_size", v))
        top.add_widget(title); top.add_widget(Widget())
        root.add_widget(top)

        body = BoxLayout(spacing=dp(18))

        # Foto
        col1 = BoxLayout(orientation="vertical", spacing=dp(12), size_hint_x=.36)
        col1.add_widget(Label(text="Fotoğraf", color=Theme.sub, font_size=dp(20), size_hint_y=None, height=dp(26)))
        img_card = RoundPanel()
        img_box = BoxLayout(size_hint_y=None, height=dp(260))
        self.img = KivyImage(allow_stretch=True, keep_ratio=True)
        if self.initial.get("foto") and os.path.exists(self.initial["foto"]):
            self.img.source = self.initial["foto"]
        img_box.add_widget(self.img)
        img_card.add_widget(img_box)
        col1.add_widget(img_card)
        btn_recap = GhostButton(text="📷 Yeni Fotoğraf Çek", size=(dp(220), dp(44)))
        btn_recap.bind(on_release=lambda *_: AddPersonPopup().open())
        col1.add_widget(btn_recap)
        body.add_widget(col1)

        # Ad
        col2 = BoxLayout(orientation="vertical", spacing=dp(12), size_hint_x=.32)
        col2.add_widget(Label(text="Ad", color=Theme.sub, font_size=dp(20), size_hint_y=None, height=dp(26)))
        name_card = RoundPanel()
        self.ed_name = TextInput(text=self.initial.get("ad",""), hint_text="Ad",
                                 multiline=False, background_color=(0,0,0,0),
                                 foreground_color=(0,0,0,1), cursor_color=(0,0,0,1),
                                 padding=[dp(10), dp(12), dp(10), dp(12)])
        name_card.add_widget(self.ed_name)
        col2.add_widget(name_card)
        btn_name = PrimaryButton(text="Kaydet", size=(dp(140), dp(44)))
        btn_name.bind(on_release=self._save_name)
        col2.add_widget(btn_name)
        body.add_widget(col2)

        # Talimat
        col3 = BoxLayout(orientation="vertical", spacing=dp(12), size_hint_x=.32)
        col3.add_widget(Label(text="Talimat", color=Theme.sub, font_size=dp(20), size_hint_y=None, height=dp(26)))
        note_card = RoundPanel()
        self.ed_note = TextInput(text=self.initial.get("talimat",""), hint_text="Talimat",
                                 multiline=True, background_color=(0,0,0,0),
                                 foreground_color=(0,0,0,1), cursor_color=(0,0,0,1),
                                 padding=[dp(10), dp(12), dp(10), dp(12)])
        note_card.add_widget(self.ed_note)
        col3.add_widget(note_card)
        btn_note = PrimaryButton(text="Kaydet", size=(dp(140), dp(44)))
        btn_note.bind(on_release=self._save_note)
        col3.add_widget(btn_note)
        body.add_widget(col3)

        root.add_widget(body)
        self.content = root

    def _save_name(self, *_):
        data = ayarlari_yukle()
        i = data.get("aktif_kullanici", 0)
        if 0 <= i < len(data.get("kullanicilar", [])):
            data["kullanicilar"][i]["ad"] = self.ed_name.text.strip()
            with open(AYARLAR_DOSYASI, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            seslendir("Ad güncellendi.")

    def _save_note(self, *_):
        data = ayarlari_yukle()
        i = data.get("aktif_kullanici", 0)
        if 0 <= i < len(data.get("kullanicilar", [])):
            data["kullanicilar"][i]["yonerge"] = self.ed_note.text.strip()
            with open(AYARLAR_DOSYASI, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            seslendir("Talimat güncellendi.")

# ——— ANA UYGULAMA ———
from kivy.graphics import Color, Rectangle  # üst importlarda yoksa ekli kalsın

class RobotApp(App):
    def build(self):
        global robot_app_instance
        robot_app_instance = self

        # --- Arka plan (self.layout) ---
        self.layout = FloatLayout()
        with self.layout.canvas.before:
            Color(*Theme.bg1)
            self._bg_rect = Rectangle(pos=self.layout.pos, size=self.layout.size)

        def _sync_bg(*_):
            if hasattr(self, "_bg_rect"):
                self._bg_rect.size = self.layout.size
                self._bg_rect.pos = self.layout.pos

        self.layout.bind(size=_sync_bg, pos=_sync_bg)

        # Üst Uygulama Çubuğu
        appbar = RoundPanel(size_hint=(1, None), height=dp(64), pos_hint={"x": 0, "top": 1})
        bar = BoxLayout()
        title = Label(text="ROBOT", color=Theme.txt, bold=True, font_size=dp(22),
                      size_hint_x=None, width=dp(120))
        bar.add_widget(title)
        bar.add_widget(Widget())
        # Hızlı durum etiketi
        self.status_label = Label(text="Hazır", color=Theme.sub, font_size=dp(14))
        bar.add_widget(self.status_label)
        appbar.add_widget(bar)
        self.layout.add_widget(appbar)

        # Orta: Sohbet Geçmişi (kart)
        chat_card = RoundPanel(size_hint=(1, None), height=dp(300), pos_hint={"x": 0, "y": 0.58})
        self.chat_history_layout = BoxLayout(
            orientation='vertical', size_hint_y=None,
            padding=[dp(12), dp(8), dp(12), dp(8)], spacing=dp(6)
        )
        self.chat_history_layout.bind(minimum_height=self.chat_history_layout.setter('height'))
        self.chat_scroll = ScrollView(do_scroll_x=False)
        self.chat_scroll.add_widget(self.chat_history_layout)
        chat_card.add_widget(self.chat_scroll)
        self.layout.add_widget(chat_card)

        # Orta: “göz” görseli (kart)
        eye_card = RoundPanel(size_hint=(None, None), size=(dp(320), dp(320)),
                              pos_hint={"center_x": 0.5, "center_y": 0.72})
        try:
            self.img = Image(source=GOZ_DOSYASI, allow_stretch=True, keep_ratio=True)
        except Exception:
            self.img = Image(allow_stretch=True, keep_ratio=True)
        eye_card.add_widget(self.img)
        self.layout.add_widget(eye_card)

        # Alt Aksiyon Barı (scroll'lu, butonlar üst üste binmez)
        actions = RoundPanel(size_hint=(1, None), height=dp(86), pos_hint={"x": 0, "y": 0.02})

        sv = ScrollView(size_hint=(1, 1), do_scroll_y=False, do_scroll_x=True, bar_width=dp(4))
        row = BoxLayout(orientation="horizontal",
                        spacing=dp(10),
                        padding=[dp(12), dp(10), dp(12), dp(10)],
                        size_hint=(None, 1))
        row.bind(minimum_width=row.setter("width"))

        btn_mic = PrimaryButton(text="🎤 Sesli Komut", size_hint=(None, 1), width=dp(220))
        btn_mic.bind(on_release=lambda *_: buton_sesli_komut() if 'buton_sesli_komut' in globals() else None)

        btn_user = GhostButton(text="👤 Kullanıcı Değiştir", size_hint=(None, 1), width=dp(220))
        btn_user.bind(on_release=self.kullanici_degistir)

        btn_add = GhostButton(text="➕ Kişi Ekle", size_hint=(None, 1), width=dp(220))
        btn_add.bind(on_release=self.kisi_ekle_ac)

        row.add_widget(btn_mic)
        row.add_widget(btn_user)
        row.add_widget(btn_add)

        sv.add_widget(row)
        actions.add_widget(sv)
        self.layout.add_widget(actions)

        # Animasyon + arkaplan dinleyici
        self.eye_animation_scheduled = None
        Clock.schedule_interval(self.update_eye_animation, 0.1)
        if 'arkaplan_dinleyici' in globals():
            threading.Thread(target=arkaplan_dinleyici, daemon=True).start()
        # --- Yüz tanıma dinleyici thread'i başlat ---
        threading.Thread(target=yuz_tanima_dinleyici, daemon=True).start()

        # Sohbet geçmişini UI kurulduktan sonra yükle
        Clock.schedule_once(lambda dt: self.load_chat_history_to_ui(), 0)

        return self.layout

    # —— Açıcılar ——
    def kisi_ekle_ac(self, *_):
        if 'AddPersonPopup' in globals():
            AddPersonPopup().open()
        else:
            self.set_mesaj("AddPersonPopup tanımlı değil.", "Hata")

    def kullanici_degistir(self, *_):
        if 'ayarlari_yukle' not in globals():
            self.set_mesaj("ayarlari_yukle() bulunamadı.", "Hata")
            return
        ayar = ayarlari_yukle()
        names = [k.get("ad", "Adsız") for k in ayar.get("kullanicilar", [])]
        if not names:
            seslendir("Kayıtlı kullanıcı bulunamadı.")
            self.set_mesaj("Kayıtlı kullanıcı yok.", "Sistem")
            return
        sp = Spinner(text="Kullanıcı Seç", values=names, size_hint=(None, None), size=(dp(220), dp(48)))

        def on_select(spinner_instance, text):
            ayar["aktif_kullanici"] = spinner_instance.values.index(text)
            try:
                with open(AYARLAR_DOSYASI, "w", encoding="utf-8") as f:
                    json.dump(ayar, f, ensure_ascii=False, indent=2)
                pop.dismiss()
                seslendir(f"{text} aktif kullanıcı.")
            except Exception as e:
                self.set_mesaj(f"Hata: {e}", "Hata")

        sp.bind(text=on_select)
        pop = Popup(title="", content=RoundPanel(children=[sp]),
                    size_hint=(None, None), size=(dp(320), dp(160)))
        pop.open()

    # —— Sohbet geçmişi & durum ——
    def load_chat_history_to_ui(self):
        if 'sohbet_gecmisini_oku' not in globals():
            return
        for line in sohbet_gecmisini_oku().split("\n"):
            t = line.strip()
            if not t or t.startswith("#") or "]: " not in t:
                continue
            parts = t.split("]: ", 1)
            sender_msg = parts[1]
            if sender_msg.startswith("Kullanıcı:"):
                self.set_mesaj(sender_msg.split("Kullanıcı:", 1)[1].strip(), "Kullanıcı", from_history=True)
            elif sender_msg.startswith("Robot:"):
                self.set_mesaj(sender_msg.split("Robot:", 1)[1].strip(), "Robot", from_history=True)
            else:
                self.set_mesaj(sender_msg, "Sistem", from_history=True)

    def set_mesaj(self, text, sender="Robot", from_history=False):
        bubble = RoundPanel(radius=14, fill=(0.12, 0.13, 0.18, 0.9))
        bubble.size_hint_y = None
        bubble.height = dp(56)
        lbl = Label(
            text=f"[b]{sender}:[/b] {text}" if sender in ("Robot", "Sistem", "Hata") else f"[b]Siz:[/b] {text}",
            markup=True, color=Theme.txt, halign="left", valign="middle"
        )
        lbl.bind(size=lambda _, v: setattr(lbl, "text_size", v))
        bubble.add_widget(lbl)
        self.chat_history_layout.add_widget(bubble)
        Clock.schedule_once(lambda dt: setattr(self.chat_scroll, "scroll_y", 0))
        if not from_history:
            anim = Animation(opacity=0, duration=0)
            anim += Animation(opacity=1, duration=0.35)
            anim.start(bubble)

    def set_status(self, text, color=Theme.sub):
        self.status_label.text = text
        self.status_label.color = color

    # —— Göz kırpma ——
    def update_eye_animation(self, dt):
        if 'konusuyor_mu' in globals() and konusuyor_mu:
            if self.eye_animation_scheduled:
                Clock.unschedule(self.eye_animation_scheduled)
                self.eye_animation_scheduled = None
            self.img.opacity = 1
        else:
            if not self.eye_animation_scheduled:
                self.eye_animation_scheduled = Clock.schedule_interval(self.kirp, 3)

    def kirp(self, dt):
        anim = Animation(opacity=0.1, duration=0.18) + Animation(opacity=1, duration=0.18)
        anim.start(self.img)


if __name__ == "__main__":
    RobotApp().run()
