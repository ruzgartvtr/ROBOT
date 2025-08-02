import os, threading, urllib.parse, webbrowser, requests, tempfile, subprocess, json, speech_recognition as sr, random, time
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
try:

    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    PYCAW_AVAILABLE = True
except ImportError:
    PYCAW_AVAILABLE = False
    print("Uyarı: pycaw kütüphanesi bulunamadı. Ses seviyesi kontrolü çalışmayacaktır. (Sadece Windows'ta geçerlidir)")
except Exception as e:
    PYCAW_AVAILABLE = False
    print(f"Uyarı: pycaw yüklenirken bir hata oluştu: {e}. Ses seviyesi kontrolü çalışmayacaktır.")

GEMINI_API_KEY = "AIzaSyASyfZ1dGehA7gtE2XmzJch1KnUN_sBPvo"
VOICE_ID = "rDol2Ljxrvb0kzLzHooJ"
ELEVEN_API_KEY = "sk_ffde8aed6e2dca9ded66ae1e071a7f142247fa419dbc4d03"
GOZ_DOSYASI = "robot_goz.png"
TMDB_API_KEY = "f12c7e8322e92753f482f81ff60041ee"
AYARLAR_DOSYASI = r"C:\Users\ruzga\Downloads\Robot\ayarlari.json"
SOHBET_GECMİSİ_DOSYASI = "Sohbet Geçmişi.txt"
cocukoyunulink = "https://raw.githubusercontent.com/ruzgartvtr/ROBOT/refs/heads/main/tarayici.py"
normaloyunlink = "https://www.dropbox.com/scl/fi/20ugfx7oioybvtrz9dv7j/cheese-is-the-reason.zip?rlkey=fn8lpak28ue0w2svsk6oi5v5x&e=1&st=xiv6keno&dl=1"
NORMAL_OYUN_KLASORU = r"C:\Users\ruzga\Downloads\cheese is the reason"
NORMAL_OYUN_EXE_YOLU = r"C:\Users\ruzga\Downloads\cheese is the reason\export 1 windows\Cheese is the reason.exe"
HABER_KAYNAKLARI = ["https://www.aa.com.tr/tr/rss/default?cat=guncel"] 

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
    Verilen metni ElevenLabs API'si aracılığıyla seslendirir ve oynatır.
    Konuşma sırasında 'konusuyor_mu' global değişkenini yönetir.
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
        # Spotify çalıyor mu kontrolü
        current = sp.current_playback()
        if current and current.get("is_playing"):
            spotify_caliniyor = True
            sp.pause_playback()

        konusuyor_mu = True
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

    except requests.exceptions.ConnectionError as e:
        print(f"[Seslendirme Ağı Hatası]: Bağlantı kurulamadı - {e}")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj("Seslendirme için ElevenLabs'e bağlanılamadı. İnternet bağlantınızı kontrol edin.", "Hata"))
    except requests.exceptions.Timeout as e:
        print(f"[Seslendirme Zaman Aşımı Hatası]: ElevenLabs yanıt vermedi - {e}")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj("ElevenLabs seslendirme servisi zaman aşımına uğradı.", "Hata"))
    except requests.exceptions.RequestException as e:
        print(f"[Seslendirme API Hatası]: {e}")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"ElevenLabs API ile iletişimde hata oluştu: {e}", "Hata"))
    except FileNotFoundError:
        print("[Seslendirme Hatası]: ffplay bulunamadı. Lütfen ffplay'in PATH'inizde olduğundan emin olun.")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj("Ses oynatıcı (ffplay) bulunamadı. Lütfen yükleyin.", "Hata"))
    except Exception as e:
        print("[Seslendirme Genel Hatası]:", e)
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"Seslendirme sırasında beklenmeyen bir hata oluştu: {e}", "Hata"))
    finally:
        if spotify_caliniyor:
            try:
                sp.start_playback()
            except Exception as e:
                print("[Spotify Başlatma Hatası]:", e)
        konusuyor_mu = False
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
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
    scrcpy_baslat(ses_aktar=True)
    if robot_app_instance:
        Clock.schedule_once(lambda dt: robot_app_instance.arama_ekrani_goster())

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


# --- Adrese göre arama (fuzzy + temiz) ---
def adb_ile_kisi_arama(kisi_adi):
    numara = kisi_numarasi_getir(kisi_adi)
    if numara:
        adb_ile_tam_otomatik_arama(numara)
    else:
        seslendir("Kişi bulunamadı.")

# --- WhatsApp görüntülü arama (fuzzy + temiz + adb) ---
def whatsapp_goruntulu_arama_kisi_ara(kisi_adi):
    scrcpy_baslat(ses_aktar=True)
    if robot_app_instance:
        Clock.schedule_once(lambda dt: robot_app_instance.arama_ekrani_goster())

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
    adb_komut("adb shell input tap 409 1492")  # WhatsApp ikonuna tıkla
    time.sleep(2)
    adb_komut("adb shell input tap 950 150")  # Arama kutusu
    time.sleep(1)
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

def scrcpy_baslat(ses_aktar=False):
    try:
        komut = ["scrcpy"]
        if ses_aktar:
            komut.append("--audio")
        subprocess.Popen(komut)
        seslendir("Telefon ekranı gösteriliyor.")
    except FileNotFoundError:
        seslendir("SCRCPY bulunamadı. Lütfen yükleyin.")
    except Exception as e:
        print("[SCRCPY Hatası]:", e)
        seslendir("SCRCPY başlatılırken hata oluştu.")



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

def ses_seviyesini_ayarla(yuzde):
    """Ses seviyesini ayarlar (sadece Windows için pycaw gerektirir)."""
    if not PYCAW_AVAILABLE:
        seslendir("Ses seviyesi kontrolü için gerekli kütüphane (pycaw) yüklü değil veya işletim sisteminiz Windows değil.")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj("Ses seviyesi kontrolü kullanılamıyor (pycaw eksik).", "Uyarı"))
        return

    try:
        yuzde = max(0, min(100, int(yuzde)))
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_status(f"Ses seviyesi %{yuzde} olarak ayarlanıyor...", color=(0.8, 0.8, 0, 1)))

        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMasterVolumeLevelScalar(yuzde / 100, None)
        seslendir(f"Ses seviyesi %{yuzde} olarak ayarlandı.")
    except Exception as e:
        print(f"[Ses Seviyesi Hatası]: {e}")
        seslendir("Ses seviyesi ayarlanırken bir hata oluştu.")
        if robot_app_instance:
            Clock.schedule_once(lambda dt: robot_app_instance.set_mesaj(f"Ses seviyesi ayarlanırken bir hata oluştu: {e}", "Hata"))
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


def adb_komut(cmd):
    print("[ADB]:", cmd)
    subprocess.run(cmd, shell=True)



def gemini_yanit_al(metin, max_deneme=3, bekleme_suresi=2, is_summary_request=False):
    """
    Gemini API'sinden yanıt alır. Bağlantı ve diğer hataları detaylı yönetir.
    'is_summary_request' bayrağı, prompt'un farklı formatlanmasını sağlar.
    """
    kullanici = aktif_kullanici_bilgi()

    if is_summary_request:
        mesaj = metin 
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
        - cocuk_oyunu: (çocuk oyunu başlatır)
        - normal_oyun: (normal oyun başlatır)
        - soru: (soru sorar)
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
        """
        sohbet_gecmisi = sohbet_gecmisini_oku()
        mesaj = f"Geçmiş Sohbet:\n{sohbet_gecmisi}\n\nKullanici adi: {kullanici['ad']}\nRol: {kullanici['rol']}\nYonerge: {kullanici['yonerge']}\nKullanici soyle dedi: '{metin}'\n\nEger ozel komut varsa bu formatlardan biriyle cevap ver:\n{komut_listesi}. Respond concisely and Keep it brief. Sadece komutu veya ilgili yanıtı ver, ekleme yapma. Normal konuşma dışında komut verme. Komut verdiğinde sadece komutu yaz."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"role": "user", "parts": [{"text": mesaj}]}]}

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

# Tam entegre komut_coz_ve_isle fonksiyonu

def komut_coz_ve_isle(metin):
    if not metin.strip(): 
        return

    yanit = gemini_yanit_al(metin)
    print("[Gemini Yanıtı]:", yanit)

    # WhatsApp Görüntülü Arama
    if "whatsappgoruntulu:" in yanit:
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

class RobotApp(App):
    def build(self):
        global robot_app_instance
        robot_app_instance = self

        self.load_chat_history_to_ui()

        self.layout = FloatLayout()

        self.chat_history_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.chat_history_layout.bind(minimum_height=self.chat_history_layout.setter('height'))
        self.chat_scroll = ScrollView(size_hint=(1, 0.4), pos_hint={"center_x": 0.5, "y": 0.58}, do_scroll_x=False)
        self.chat_scroll.add_widget(self.chat_history_layout)
        self.layout.add_widget(self.chat_scroll)

        self.status_label = Label(text="Hazır!", font_size=16, color=(0, 1, 0, 1), size_hint=(1, None), height=30,
                                  pos_hint={"center_x": 0.5, "y": 0.54})
        self.layout.add_widget(self.status_label)

        self.img = Image(source=GOZ_DOSYASI, size_hint=(None, None), size=(300, 300), pos_hint={"center_x": 0.5, "center_y": 0.7})
        self.layout.add_widget(self.img)

        self.buton_ekle("🎤 Sesli Komut", 0.22)
        self.buton_ekle("👤 Kullanıcı Değiştir", 0.12, self.kullanici_degistir)

        self.eye_animation_scheduled = None 
        Clock.schedule_interval(self.update_eye_animation, 0.1) 

        threading.Thread(target=arkaplan_dinleyici, daemon=True).start()
        return self.layout

    def load_chat_history_to_ui(self):
        """Uygulama başladığında sohbet geçmişini UI'a yükler."""
        history_content = sohbet_gecmisini_oku().split('\n')

        for line in history_content:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            if ']: ' in line:
                try:
                    parts = line.split(']: ', 1)
                    sender_msg = parts[1]
                    if sender_msg.startswith("Kullanıcı:"):
                        sender = "Kullanıcı"
                        message = sender_msg.split("Kullanıcı:", 1)[1].strip()
                    elif sender_msg.startswith("Robot:"):
                        sender = "Robot"
                        message = sender_msg.split("Robot:", 1)[1].strip()
                    else: 
                        sender = "Sistem"
                        message = sender_msg

                    Clock.schedule_once(lambda dt, msg=message, s=sender, fh=True: self.set_mesaj(msg, s, from_history=fh))
                except Exception as e:
                    print(f"Sohbet geçmişi satırı ayrıştırılırken hata: {line} - {e}")

                    Clock.schedule_once(lambda dt, line_err=line: self.set_mesaj(f"Geçmiş yükleme hatası: {line_err}", "Hata", from_history=True))

    def set_mesaj(self, text, sender="Robot", from_history=False):
        """
        Sohbet geçmişine yeni bir mesaj ekler ve UI'ı günceller.
        'from_history' bayrağı, geçmişten yüklenen mesajlar için animasyonları engeller.
        Bu fonksiyon artık sadece ana Kivy iş parçacığında çalışır.
        """

        bubble_box = BoxLayout(orientation='vertical', size_hint_y=None, padding=[10, 5, 10, 5])
        msg_label = Label(text=text, font_size=16, size_hint_y=None, markup=True,
                          halign="left", valign="top", padding_x=10, padding_y=5)
        msg_label.bind(texture_size=msg_label.setter('size'))

        msg_label.text_size = (self.chat_scroll.width * 0.9, None) 

        if sender == "Kullanıcı":
            msg_label.text = f"[b]Siz:[/b] {text}"
            msg_label.color = (1, 1, 1, 1)
            bubble_box.background_color = (0.2, 0.5, 0.8, 0.8) 
            bubble_box.padding = [self.chat_scroll.width * 0.1, 5, 10, 5] 
            msg_label.halign = "right"
        elif sender == "Robot":
            msg_label.text = f"[b]Robot:[/b] {text}"
            msg_label.color = (0, 1, 0, 1)
            bubble_box.background_color = (0.1, 0.1, 0.1, 0.8) 
            bubble_box.padding = [10, 5, self.chat_scroll.width * 0.1, 5] 
            msg_label.halign = "left"
        elif sender == "Sistem":
            msg_label.text = f"[b]Sistem:[/b] {text}"
            msg_label.color = (1, 1, 0, 1) 
            bubble_box.background_color = (0.3, 0.3, 0.3, 0.8)
            bubble_box.padding = [10, 5, 10, 5]
            msg_label.halign = "center"
        elif sender == "Hata":
            msg_label.text = f"[b]Hata:[/b] {text}"
            msg_label.color = (1, 1, 1, 1)
            bubble_box.background_color = (0.8, 0.2, 0.2, 0.8) 
            bubble_box.padding = [10, 5, 10, 5]
            msg_label.halign = "center"

        with bubble_box.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(*bubble_box.background_color)

            self.rect = RoundedRectangle(size=bubble_box.size, pos=bubble_box.pos, radius=[10])

        bubble_box.bind(size=lambda x, y: setattr(self.rect, 'size', y),
                        pos=lambda x, y: setattr(self.rect, 'pos', y))

        self.chat_history_layout.add_widget(bubble_box)
        bubble_box.add_widget(msg_label) 

        Clock.schedule_once(lambda dt: self.chat_scroll.scroll_y == 0)

        if not from_history:
            anim = Animation(opacity=0, duration=0) + Animation(opacity=1, duration=0.5)
            anim.start(bubble_box)
    
    def set_status(self, text, color=(0, 1, 0, 1)):
        """Durum etiketini günceller."""

        self.status_label.text = text
        self.status_label.color = color

    def update_eye_animation(self, dt):
        """Robot konuşurken göz animasyonunu duraklatır."""
        if konusuyor_mu:
            if self.eye_animation_scheduled:
                Clock.unschedule(self.eye_animation_scheduled)
                self.eye_animation_scheduled = None
            self.img.opacity = 1 
        else:
            if not self.eye_animation_scheduled:
                self.eye_animation_scheduled = Clock.schedule_interval(self.kirp, 3) 

    def kirp(self, dt):
        """Göz kırpma animasyonunu yapar."""
        anim = Animation(opacity=0.1, duration=0.2) + Animation(opacity=1, duration=0.2)
        anim.start(self.img)

    def buton_ekle(self, yazi, y_pos, fonk=None):
        """UI'a bir buton ekler."""
        buton = Button(text=yazi, size_hint=(0.9, 0.08), pos_hint={"center_x": 0.5, "y": y_pos}, 
                       background_normal="", background_color=(1, 0.75, 0, 1), color=(0,0,0,1), font_size=16)
        buton.bind(on_release=fonk if fonk else lambda x: buton_sesli_komut())
        self.layout.add_widget(buton)

    def kullanici_degistir(self, *args):
        """Kullanıcı değiştirme pop-up'ını açar."""
        ayar = ayarlari_yukle()
        kullanici_adlari = [k["ad"] for k in ayar["kullanicilar"]]
        if not kullanici_adlari:
            seslendir("Henüz kayıtlı kullanıcı bulunamadı. Lütfen ayarlari.json dosyasını kontrol edin ve kullanıcı ekleyin.")
            if self.robot_app_instance:
                Clock.schedule_once(lambda dt: self.robot_app_instance.set_mesaj("Kayıtlı kullanıcı yok.", "Uyarı"))
            return

        spinner = Spinner(text="Kullanıcı Seç", values=kullanici_adlari, size_hint=(None, None), size=(200, 50))

        def on_select(spinner_instance, text):
            ayar["aktif_kullanici"] = spinner_instance.values.index(text)
            try:
                with open(AYARLAR_DOSYASI, "w", encoding="utf-8") as f:
                    json.dump(ayar, f, ensure_ascii=False, indent=2)
                popup.dismiss()
                seslendir(f"{text} aktif kullanıcı olarak seçildi.")
            except Exception as e:
                seslendir(f"Kullanıcı değiştirilirken hata oluştu: {e}")
                if self.robot_app_instance:
                    Clock.schedule_once(lambda dt: self.robot_app_instance.set_mesaj(f"Kullanıcı değiştirme hatası: {e}", "Hata"))

        spinner.bind(text=on_select)
        popup = Popup(title="Kullanıcı Değiştir", content=spinner, size_hint=(None, None), size=(300, 200))
        popup.open()

if __name__ == "__main__":
    subprocess.Popen(["python", "arama_ekrani.py"])
    RobotApp().run()