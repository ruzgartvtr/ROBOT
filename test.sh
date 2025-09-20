#!/usr/bin/env bash
# test.sh - Hızlı sistem ve ağ sağlık kontrolü
# Kullanım: chmod +x test.sh && ./test.sh
# Seçenekler:
#   --install  : (İsteğe bağlı) Homebrew (macOS) / paketler (Linux) ve küçük araçları kurmayı dener
#   --quiet    : Daha az çıktı
set -euo pipefail

QUIET=0
DO_INSTALL=0
LOGFILE="test_log.txt"
START_TS="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

for arg in "$@"; do
  case "$arg" in
    --install) DO_INSTALL=1 ;;
    --quiet)   QUIET=1 ;;
    *) echo "Bilinmeyen seçenek: $arg" ;;
  esac
done

log() {
  if [[ $QUIET -eq 0 ]]; then
    echo -e "$1" | tee -a "$LOGFILE"
  else
    echo -e "$1" >> "$LOGFILE"
  fi
}

hr() { log "\n────────────────────────────────────────"; }

trap 'log "\n[HATA] Komut başarısız oldu (exit code $?). Log: $LOGFILE"; exit 1' ERR

: > "$LOGFILE"
log "[BAŞLANGIÇ] $START_TS"
hr

# OS TESPİTİ
OS="$(uname -s)"
ARCH="$(uname -m)"
HOST="$(hostname || true)"
log "[BİLGİ] Sistem: $OS ($ARCH) • Host: $HOST"
case "$OS" in
  Darwin) PLATFORM="macOS" ;;
  Linux)  PLATFORM="Linux" ;;
  *)      PLATFORM="Bilinmiyor" ;;
esac
log "[BİLGİ] Platform: $PLATFORM"
hr

# (İSTEĞE BAĞLI) KURULUM ADIMLARI
if [[ $DO_INSTALL -eq 1 ]]; then
  log "[KURULUM] Gerekli yardımcıları kontrol ediyorum..."
  if [[ "$PLATFORM" == "macOS" ]]; then
    if ! command -v brew >/dev/null 2>&1; then
      log "[KURULUM] Homebrew yok, kurulum deneniyor..."
      /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
      log "[KURULUM] brew path eklemeniz gerekebilir."
    fi
    brew list --versions curl >/dev/null 2>&1 || brew install curl
    brew list --versions wget >/dev/null 2>&1 || brew install wget
    brew list --versions iperf3 >/dev/null 2>&1 || brew install iperf3
    brew list --versions jq >/dev/null 2>&1 || brew install jq
  elif [[ "$PLATFORM" == "Linux" ]]; then
    PKG=""
    if command -v apt-get >/dev/null 2>&1; then PKG="sudo apt-get update && sudo apt-get install -y";
    elif command -v dnf >/dev/null 2>&1; then PKG="sudo dnf install -y";
    elif command -v pacman >/devnull 2>&1; then PKG="sudo pacman -Sy --noconfirm";
    fi
    if [[ -n "$PKG" ]]; then
      bash -lc "$PKG curl wget iproute2 iperf3 jq || true"
    else
      log "[KURULUM] Paket yöneticisi bulunamadı, atlanıyor."
    fi
  fi
  hr
fi

# TARİH / SAAT
log "[ZAMAN] Yerel:  $(date)"
log "[ZAMAN] UTC:    $(date -u)"
hr

# AĞ TESTLERİ
log "[AĞ] IP adresleri:"
if command -v ip >/dev/null 2>&1; then
  ip addr show | sed 's/^/  /' | tee -a "$LOGFILE" >/dev/null
elif command -v ifconfig >/dev/null 2>&1; then
  ifconfig | sed 's/^/  /' | tee -a "$LOGFILE" >/dev/null
fi

log "[AĞ] Ping testi (1.1.1.1, 3 paket):"
if ping -c 3 -W 2 1.1.1.1 >/tmp/ping_out 2>&1; then
  sed 's/^/  /' /tmp/ping_out | tee -a "$LOGFILE" >/dev/null
  log "[AĞ] Ping OK"
else
  sed 's/^/  /' /tmp/ping_out | tee -a "$LOGFILE" >/dev/null
  log "[AĞ] Ping BAŞARISIZ"
fi

log "[AĞ] DNS testi (github.com):"
if ping -c 1 -W 2 github.com >/dev/null 2>&1; then
  log "  DNS ÇÖZÜMLENDİ ✅"
else
  log "  DNS SORUNU ❌"
fi

log "[AĞ] HTTP testi (https://example.com):"
if curl -fsS --max-time 10 -I https://example.com >/tmp/http_head 2>&1; then
  head -n 5 /tmp/http_head | sed 's/^/  /' | tee -a "$LOGFILE" >/dev/null
  log "  HTTP OK"
else
  sed 's/^/  /' /tmp/http_head | tee -a "$LOGFILE" >/dev/null
  log "  HTTP BAŞARISIZ"
fi
hr

# DONANIM & KAYNAK
log "[KAYNAK] Disk kullanımı:"
df -h | sed 's/^/  /' | tee -a "$LOGFILE" >/dev/null

if [[ "$PLATFORM" == "Linux" ]]; then
  log "[KAYNAK] Bellek (Linux):"
  (free -h || cat /proc/meminfo | head -n 10) | sed 's/^/  /' | tee -a "$LOGFILE" >/dev/null
  log "[KAYNAK] CPU:"
  (lscpu || cat /proc/cpuinfo | head -n 20) | sed 's/^/  /' | tee -a "$LOGFILE" >/dev/null
elif [[ "$PLATFORM" == "macOS" ]]; then
  log "[KAYNAK] Bellek (macOS):"
  (vm_stat; echo ""; top -l 1 -n 0 | head -n 10) | sed 's/^/  /' | tee -a "$LOGFILE" >/dev/null
  log "[KAYNAK] CPU:"
  (sysctl -n machdep.cpu.brand_string || true) | sed 's/^/  /' | tee -a "$LOGFILE" >/dev/null
fi
hr

# PYTHON / PIP TESTİ
log "[PYTHON] Sürüm kontrolleri:"
if command -v python3 >/dev/null 2>&1; then
  log "  python3: $(python3 --version 2>&1)"
else
  log "  python3 bulunamadı ❌"
fi
if command -v pip3 >/dev/null 2>&1; then
  log "  pip3: $(pip3 --version 2>&1)"
  # Kullanıcının tercihi: pip3 ve --break-system-packages
  log "[PYTHON] Basit modül testi (json, ssl):"
  python3 - <<'PY'
import json, ssl, sys
print("json/ssl OK", sys.version)
PY
else
  log "  pip3 bulunamadı ❌"
fi
hr

# HIZLI DOSYA/İZİN TESTİ
TMPDIR="$(mktemp -d)"
log "[DOSYA] Geçici dizin: $TMPDIR"
echo "Test dosyası" > "$TMPDIR/test.txt"
if grep -q "Test dosyası" "$TMPDIR/test.txt"; then
  log "  Yazma/okuma OK"
else
  log "  Yazma/okuma SORUNU"
fi

# PORT TESTİ (isteğe bağlı, nc varsa)
if command -v nc >/dev/null 2>&1; then
  log "[PORT] 443/tcp erişim testi (github.com):"
  if nc -z -w 3 github.com 443; then
    log "  443 açık ✅"
  else
    log "  443 kapalı/engelli ❌"
  fi
fi
hr

# ÖZET
END_TS="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
log "[BİTİŞ] $END_TS"
log "[ÖZET] Log kaydı: $(realpath "$LOGFILE" 2>/dev/null || echo "$LOGFILE")"
log "[DURUM] Tamamlandı ✅"
