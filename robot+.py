# 🔧 Flask + ElevenLabs + Spotify + Xbox + Kamera + Gelişmiş Arayüz

import os, threading, cv2, subprocess, tempfile, pygame, requests, time
from flask import Flask, render_template_string, request, redirect, session, Response
from elevenlabs import ElevenLabs
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
import pyaudio

# Kamera indexini 0 yap
camera = cv2.VideoCapture(0)

# Spotify ayarları
SPOTIFY_CLIENT_ID = "e8658e3b5a244497af73614e995db59e"
SPOTIFY_CLIENT_SECRET = "db9a174b08434cae8814cc91a8958872"
SPOTIFY_REDIRECT_URI = "http://localhost:8888/callback"

sp = Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope="user-read-playback-state user-modify-playback-state",
    cache_path=".spotify_cache"
))

client = ElevenLabs(api_key="sk_ffde8aed6e2dca9ded66ae1e071a7f142247fa419dbc4d03")
VOICE_ID = "rDol2Ljxrvb0kzLzHooJ"

app = Flask(__name__)
app.secret_key = "gizli-anahtar-rüzgar"

kullanicilar = {
    "oylumsinan@gmail.com": {"sifre": "Oylum.182135", "foto": "https://raw.githubusercontent.com/ruzgartvtr/ROBOT/refs/heads/main/Oylum%20YEN%C4%B0.jpg", "ad": "Oylum"},
    "ruzgarhunerel@gmail.com": {"sifre": "Ruzgar.182135", "foto": "https://raw.githubusercontent.com/ruzgartvtr/ROBOT/refs/heads/main/R%C3%BCzgar.jpg", "ad": "Rüzgar"},
    "huriyesuren@gmail.com": {"sifre": "Huriye.182135", "foto": "https://raw.githubusercontent.com/ruzgartvtr/ROBOT/refs/heads/main/Huriye.jpg", "ad": "Huriye"}
}

latest_text = "Henüz konuşma yapılmadı."

# Kamera akışı

def gen_frames():
    while True:
        success, frame = camera.read()
        if not success:
            print("[KAMERA HATASI]")
            break
        _, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Mikrofon - hoparlör

def mikrofon_dinle():
    p = pyaudio.PyAudio()
    sin = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
    sout = p.open(format=pyaudio.paInt16, channels=1, rate=44100, output=True)
    def loop():
        while True:
            try:
                sout.write(sin.read(1024, exception_on_overflow=False))
            except: break
    threading.Thread(target=loop, daemon=True).start()

# Konuş

def konus_metni(metin):
    try:
        audio = client.text_to_speech.convert(
            text=metin,
            voice_id=VOICE_ID,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128"
        )
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tmp.write(b''.join(audio))
            subprocess.run(["ffplay", "-nodisp", "-autoexit", tmp.name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            os.remove(tmp.name)
    except Exception as e:
        print(f"[SES HATASI]: {e}")

# Spotify

def spotify_cal_playlist():
    try:
        playlist_id = "37i9dQZF1DXcBWIGoYBM5M"
        playlist = sp.playlist_tracks(playlist_id)
        if playlist and playlist["items"]:
            sp.start_playback(uris=[playlist["items"][0]["track"]["uri"]])
            konus_metni("Spotify'dan müzik çalıyorum.")
    except Exception as e:
        print(f"[SPOTIFY HATA]: {e}")

# Giriş

def giris_yetkili():
    return "email" in session and session["email"] in kullanicilar

@app.route('/')
def home():
    if not giris_yetkili(): return redirect('/login')
    u = kullanicilar[session["email"]]
    return render_template_string(HOME_PAGE, email=session["email"], foto=u["foto"], ad=u["ad"], metin=latest_text)

@app.route('/login', methods=['GET', 'POST'])
def login():
    hata = None
    if request.method == 'POST':
        email = request.form.get("email", "").lower()
        sifre = request.form.get("sifre", "")
        if email in kullanicilar and kullanicilar[email]["sifre"] == sifre:
            session["email"] = email
            return redirect('/')
        hata = "Hatalı giriş"
    return render_template_string(LOGIN_PAGE, hata=hata)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/konus', methods=['POST'])
def konus():
    global latest_text
    metin = request.form.get("metin")
    if metin:
        latest_text = metin
        threading.Thread(target=konus_metni, args=(metin,), daemon=True).start()
    return redirect('/')

@app.route('/gonder', methods=['POST'])
def gonder():
    komut = request.form.get("komut")
    if komut == "merhaba": konus_metni("Merhaba! Ben buradayım.")
    elif komut == "spotify": threading.Thread(target=spotify_cal_playlist, daemon=True).start()
    elif komut == "kapat": os._exit(0)
    return ('', 204)

# Xbox

def xbox_kontrolcusu_dinle():
    pygame.init()
    pygame.joystick.init()
    last_sent = ''
    while True:
        if pygame.joystick.get_count() == 0:
            time.sleep(2)
            continue
        js = pygame.joystick.Joystick(0)
        js.init()
        while True:
            pygame.event.pump()
            y = js.get_axis(1)
            x = js.get_axis(0)
            komut = 'stop'
            if y < -0.5: komut = 'w'
            elif y > 0.5: komut = 's'
            elif x < -0.5: komut = 'a'
            elif x > 0.5: komut = 'd'
            if js.get_button(0): komut = 'merhaba'
            elif js.get_button(2): komut = 'spotify'
            elif js.get_button(1): komut = 'kapat'
            if komut != last_sent or komut in ['w','a','s','d']:
                try:
                    requests.post("http://localhost:5000/gonder", data={"komut": komut})
                    last_sent = komut
                except: break
            time.sleep(0.15)

# Arayüz HTML

LOGIN_PAGE = """
<!DOCTYPE html><html><head><meta charset='utf-8'>
<title>Giriş Yap</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head><body class="bg-dark text-white d-flex align-items-center justify-content-center" style="height:100vh;">
<div class="card p-4" style="width: 90%%; max-width: 400px;">
  <h4 class="text-center mb-3">🔐 Giriş Yap</h4>
  <form method="post" onsubmit="rememberMe()">
    <div class="mb-3">
      <label class="form-label">E-posta</label>
      <input id="email" name='email' type="email" class="form-control" required>
    </div>
    <div class="mb-3">
      <label class="form-label">Şifre</label>
      <input name='sifre' type="password" class="form-control" required>
    </div>
    <div class="form-check mb-3">
      <input type="checkbox" class="form-check-input" id="rememberMe">
      <label class="form-check-label" for="rememberMe">Beni hatırla</label>
    </div>
    <button class="btn btn-primary w-100">Giriş</button>
    {% if hata %}<p class="text-danger mt-2">{{ hata }}</p>{% endif %}
  </form>
</div>
<script>
  const saved = localStorage.getItem("email");
  if (saved) document.getElementById("email").value = saved;

  function rememberMe() {
    const box = document.getElementById("rememberMe");
    const email = document.getElementById("email").value;
    if (box.checked) localStorage.setItem("email", email);
    else localStorage.removeItem("email");
  }
</script>
</body></html>
"""



HOME_PAGE = """
<!DOCTYPE html><html><head><meta charset='utf-8'>
<title>Robot Paneli</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
  body.dark-mode { background-color: #121212; color: white; }
  body.light-mode { background-color: #f8f9fa; color: black; }
  .bubble { display: inline-block; padding: 10px 15px; border-radius: 20px; margin-top: 10px; max-width: 80%%; }
  .bubble.robot { background-color: #198754; color: white; }
  .joystick-button {
    width: 60px; height: 60px;
    background-color: #0d6efd;
    color: white; border-radius: 50%%;
    display: flex; align-items: center; justify-content: center;
    font-size: 24px; margin: 10px;
    user-select: none; touch-action: none;
  }
</style>
</head>
<body class="dark-mode" id="body">
<div class="container py-4">
  <div class="text-end">
    <button onclick="toggleTheme()" class="btn btn-sm btn-outline-secondary">🌓 Tema</button>
  </div>
  <div class="text-center mb-4">
    <h2>🤖 Merhaba, {{ ad }}</h2>
    <img src="{{ foto }}" class="rounded-circle" width="100" height="100" style="object-fit:cover;"><br>
    <a href="/logout" class="btn btn-outline-light mt-2">Çıkış</a>
  </div>

  <div class="row">
    <div class="col-md-6 text-center">
      <h5>🎥 Kamera</h5>
      <img src='/video_feed' width='100%%' class="border rounded">
    </div>
    <div class="col-md-6">
      <h5>🗣️ Robotla Konuş</h5>
      <form method="post" action="/konus" class="mb-3">
        <div class="input-group">
          <input name="metin" class="form-control" placeholder="Bir şey yaz..." required>
          <button class="btn btn-success">Gönder</button>
        </div>
      </form>

      <h5>🎮 Hızlı Komutlar</h5>
      <form method="post" action="/gonder" class="d-grid gap-2">
        <button name='komut' value='spotify' class="btn btn-warning">🎵 Spotify</button>
        <button name='komut' value='merhaba' class="btn btn-info">👋 Merhaba</button>
        <button name='komut' value='kapat' class="btn btn-danger">❌ Kapat</button>
      </form>
    </div>
  </div>

  <div class="mt-4 text-center">
    <h6>💬 Robotun Mesajı</h6>
    <div class="bubble robot">{{ metin }}</div>
  </div>

  <div class="mt-5 text-center">
    <h6>🎮 Dokunmatik Joystick</h6>
    <div class="d-flex justify-content-center flex-column align-items-center">
      <div class="joystick-button" ontouchstart="hareketGonder('w')">⬆️</div>
      <div class="d-flex">
        <div class="joystick-button" ontouchstart="hareketGonder('a')">⬅️</div>
        <div class="joystick-button" ontouchstart="hareketGonder('s')">⬇️</div>
        <div class="joystick-button" ontouchstart="hareketGonder('d')">➡️</div>
      </div>
    </div>
  </div>

</div>
<script>
function toggleTheme() {
  let body = document.getElementById("body");
  if (body.classList.contains("dark-mode")) {
    body.classList.remove("dark-mode");
    body.classList.add("light-mode");
    localStorage.setItem("theme", "light-mode");
  } else {
    body.classList.remove("light-mode");
    body.classList.add("dark-mode");
    localStorage.setItem("theme", "dark-mode");
  }
}
(function() {
  let theme = localStorage.getItem("theme") || "dark-mode";
  document.getElementById("body").className = theme;
})();
function hareketGonder(komut) {
  fetch('/gonder', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: 'komut=' + komut
  });
}
</script>
</body></html>
"""



# Başlat
if __name__ == '__main__':
    threading.Thread(target=mikrofon_dinle, daemon=True).start()
    threading.Thread(target=xbox_kontrolcusu_dinle, daemon=True).start()
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)
