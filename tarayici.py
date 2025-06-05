import pygame
import random
import sys

# --- PYGAME İLK AYARLAR ---
pygame.init()

# Ekran Boyutları
GENISLIK, YUKSEKLIK = 800, 600
EKRAN = pygame.display.set_mode((GENISLIK, YUKSEKLIK))
pygame.display.set_caption("Sayı Dedektifleri: Kayıp Formülün Peşinde")

# Renkler
BEYAZ = (255, 255, 255)
SIYAH = (0, 0, 0)
MAVI = (0, 120, 215)
YESIL = (46, 204, 113)
KIRMIZI = (231, 76, 60)
GRI = (200, 200, 200)
KOYU_GRI = (100, 100, 100)

# Fontlar
FONT_BASLIK = pygame.font.Font(None, 64)
FONT_NORMAL = pygame.font.Font(None, 36)
FONT_KUCUK = pygame.font.Font(None, 24)

# --- OYUN DEĞİŞKENLERİ ---
form_parcalari_bulundu = 0
gerekli_parca_sayisi = 3

dedektif_not_defteri = {
    "Antik Sayı Tapınağı": "Henüz Ziyaret Edilmedi",
    "Kesirler Şehri": "Henüz Ziyaret Edilmedi",
    "Cebir Vadisi": "Henüz Ziyaret Edilmedi"
}

MEKANLAR = [
    {"ad": "Antik Sayı Tapınağı", "seviye": "kolay", "ipucu": "Tapınağın gizli geçidini açmak için şifreyi bulmalısın."},
    {"ad": "Kesirler Şehri", "seviye": "orta", "ipucu": "Nehrin karşı kıyısına geçmek için doğru kesir kombinasyonunu bulmalısın."},
    {"ad": "Cebir Vadisi", "seviye": "zor", "ipucu": "Antik kapıyı açan denklemin gizemini çözmelisin."}
]

# Oyun Durumları
DURUM_ANA_MENU = 0
DURUM_MEKAN_SECIM = 1
DURUM_SORU_EKRANI = 2
DURUM_NOT_DEFTERI = 3
DURUM_OYUN_SONU = 4

# --- SORU EKRANI DEĞİŞKENLERİ ---
aktif_soru = None
aktif_dogru_cevap = 0
aktif_mekan = None
cevap_kutusu_metin = ""
cevap_geri_bildirim_mesaji = ""
cevap_geri_bildirim_rengi = SIYAH

OYUN_DURUMU = DURUM_ANA_MENU

# --- FONKSİYONLAR ---

def matematik_sorusu_uret(seviye):
    if seviye == "kolay":
        sayi1 = random.randint(10, 50)
        sayi2 = random.randint(5, 20)
        operator = random.choice(['+', '-'])
        if operator == '+':
            soru_str = f"{sayi1} + {sayi2} = ?"
            cevap_val = sayi1 + sayi2
        else:
            if sayi1 < sayi2:
                sayi1, sayi2 = sayi2, sayi1
            soru_str = f"{sayi1} - {sayi2} = ?"
            cevap_val = sayi1 - sayi2
        return soru_str, cevap_val
    elif seviye == "orta":
        sayi1 = random.randint(5, 15)
        sayi2 = random.randint(2, 10)
        sayi3 = random.randint(1, 5)
        operator1 = random.choice(['*', '/'])
        operator2 = random.choice(['+', '-'])

        if operator1 == '*':
            ara_sonuc = sayi1 * sayi2
            if operator2 == '+':
                soru_str = f"({sayi1} * {sayi2}) + {sayi3} = ?"
                cevap_val = ara_sonuc + sayi3
            else:
                soru_str = f"({sayi1} * {sayi2}) - {sayi3} = ?"
                cevap_val = ara_sonuc - sayi3
        else:
            sayi1 = sayi2 * random.randint(2, 10)
            ara_sonuc = sayi1 // sayi2
            if operator2 == '+':
                soru_str = f"({sayi1} / {sayi2}) + {sayi3} = ?"
                cevap_val = ara_sonuc + sayi3
            else:
                soru_str = f"({sayi1} / {sayi2}) - {sayi3} = ?"
                cevap_val = ara_sonuc - sayi3
        return soru_str, cevap_val
    elif seviye == "zor":
        a = random.randint(2, 5)
        X = random.randint(3, 10)
        b = random.randint(1, 10)
        c = a * X + b
        soru_str = f"{a}X + {b} = {c} ise X = ?"
        cevap_val = X
        return soru_str, cevap_val
    return "Hata: Geçersiz seviye", 0

def buton_ciz(ekran, metin, x, y, genislik, yukseklik, pasif_renk, aktif_renk, font_obj, eylem=None):
    fare_pos = pygame.mouse.get_pos()
    tiklandi = pygame.mouse.get_pressed()[0]

    buton_dikdortgen = pygame.Rect(x, y, genislik, yukseklik)

    if buton_dikdortgen.collidepoint(fare_pos):
        pygame.draw.rect(ekran, aktif_renk, buton_dikdortgen)
        if tiklandi:
            return True
    else:
        pygame.draw.rect(ekran, pasif_renk, buton_dikdortgen)

    metin_yuzey = font_obj.render(metin, True, BEYAZ)
    metin_dikdortgen = metin_yuzey.get_rect(center=buton_dikdortgen.center)
    ekran.blit(metin_yuzey, metin_dikdortgen)
    return False


def ekran_ana_menu():
    EKRAN.fill(MAVI)
    baslik = FONT_BASLIK.render("Sayı Dedektifleri", True, BEYAZ)
    baslik_dikdortgen = baslik.get_rect(center=(GENISLIK / 2, YUKSEKLIK / 4))
    EKRAN.blit(baslik, baslik_dikdortgen)

    global OYUN_DURUMU
    if buton_ciz(EKRAN, "OYUNA BAŞLA", GENISLIK / 2 - 100, YUKSEKLIK / 2 - 30, 200, 60, YESIL, GRI, FONT_NORMAL):
        OYUN_DURUMU = DURUM_MEKAN_SECIM
    if buton_ciz(EKRAN, "ÇIKIŞ", GENISLIK / 2 - 100, YUKSEKLIK / 2 + 50, 200, 60, KIRMIZI, KOYU_GRI, FONT_NORMAL):
        pygame.quit()
        sys.exit()

def ekran_mekan_secim():
    # Bu satır en başta olmalı
    global OYUN_DURUMU, aktif_mekan, aktif_soru, aktif_dogru_cevap, \
           cevap_kutusu_metin, cevap_geri_bildirim_mesaji, cevap_geri_bildirim_rengi

    EKRAN.fill(BEYAZ)
    baslik = FONT_BASLIK.render("Mekan Seçimi", True, SIYAH)
    baslik_dikdortgen = baslik.get_rect(center=(GENISLIK / 2, 50))
    EKRAN.blit(baslik, baslik_dikdortgen)


    y_offset = 150
    for mekan in MEKANLAR:
        mekan_durumu = dedektif_not_defteri[mekan["ad"]]
        
        pasif_renk = KOYU_GRI if mekan_durumu == "Başarılı" else MAVI
        aktif_renk = GRI if mekan_durumu == "Başarılı" else YESIL

        if buton_ciz(EKRAN, mekan["ad"], GENISLIK / 2 - 150, y_offset, 300, 60, pasif_renk, aktif_renk, FONT_NORMAL):
            if mekan_durumu != "Başarılı":
                aktif_mekan = mekan
                aktif_soru, aktif_dogru_cevap = matematik_sorusu_uret(mekan["seviye"])
                
                cevap_kutusu_metin = ""
                cevap_geri_bildirim_mesaji = ""
                cevap_geri_bildirim_rengi = SIYAH
                
                OYUN_DURUMU = DURUM_SORU_EKRANI
        y_offset += 80

    if buton_ciz(EKRAN, "DEDEKTİF NOT DEFTERİ", GENISLIK / 2 - 150, YUKSEKLIK - 80, 300, 60, MAVI, GRI, FONT_NORMAL):
        OYUN_DURUMU = DURUM_NOT_DEFTERI

def ekran_soru():
    # Bu satır en başta olmalı
    global OYUN_DURUMU, form_parcalari_bulundu, cevap_geri_bildirim_mesaji, cevap_geri_bildirim_rengi, \
           cevap_kutusu_metin # Bu değişken de burada güncellendiği için eklenmeli

    EKRAN.fill(BEYAZ)
    
    baslik = FONT_BASLIK.render(aktif_mekan["ad"], True, SIYAH)
    baslik_dikdortgen = baslik.get_rect(center=(GENISLIK / 2, 50))
    EKRAN.blit(baslik, baslik_dikdortgen)

    ipucu_metin = FONT_KUCUK.render(aktif_mekan["ipucu"], True, KOYU_GRI)
    ipucu_dikdortgen = ipucu_metin.get_rect(center=(GENISLIK / 2, 100))
    EKRAN.blit(ipucu_metin, ipucu_dikdortgen)

    soru_yuzey = FONT_NORMAL.render(aktif_soru, True, SIYAH)
    soru_dikdortgen = soru_yuzey.get_rect(center=(GENISLIK / 2, YUKSEKLIK / 2 - 50))
    EKRAN.blit(soru_yuzey, soru_dikdortgen)

    cevap_kutusu_rect = pygame.Rect(GENISLIK / 2 - 100, YUKSEKLIK / 2, 200, 50)
    pygame.draw.rect(EKRAN, KOYU_GRI, cevap_kutusu_rect, 2)
    cevap_yuzey = FONT_NORMAL.render(cevap_kutusu_metin, True, SIYAH)
    EKRAN.blit(cevap_yuzey, (cevap_kutusu_rect.x + 5, cevap_kutusu_rect.y + 5))

    feedback_yuzey = FONT_NORMAL.render(cevap_geri_bildirim_mesaji, True, cevap_geri_bildirim_rengi)
    feedback_dikdortgen = feedback_yuzey.get_rect(center=(GENISLIK / 2, YUKSEKLIK / 2 + 100))
    EKRAN.blit(feedback_yuzey, feedback_dikdortgen)

    if buton_ciz(EKRAN, "CEVAPLA", GENISLIK / 2 - 75, YUKSEKLIK / 2 + 150, 150, 50, YESIL, GRI, FONT_NORMAL):
        try:
            girilen_cevap = int(cevap_kutusu_metin)
            
            if girilen_cevap == aktif_dogru_cevap:
                cevap_geri_bildirim_mesaji = "Doğru! Formül parçasını buldun!"
                cevap_geri_bildirim_rengi = YESIL
                if dedektif_not_defteri[aktif_mekan["ad"]] != "Başarılı":
                    dedektif_not_defteri[aktif_mekan["ad"]] = "Başarılı"
                    form_parcalari_bulundu += 1
                
                pygame.time.wait(1000)
                cevap_kutusu_metin = ""
                cevap_geri_bildirim_mesaji = ""
                cevap_geri_bildirim_rengi = SIYAH
                OYUN_DURUMU = DURUM_MEKAN_SECIM
            else:
                cevap_geri_bildirim_mesaji = "Yanlış cevap. Tekrar dene."
                cevap_geri_bildirim_rengi = KIRMIZI
        except ValueError:
            cevap_geri_bildirim_mesaji = "Lütfen geçerli bir sayı girin."
            cevap_geri_bildirim_rengi = KIRMIZI

    if buton_ciz(EKRAN, "GERİ DÖN", GENISLIK / 2 - 75, YUKSEKLIK - 70, 150, 50, KOYU_GRI, GRI, FONT_NORMAL):
        cevap_kutusu_metin = ""
        cevap_geri_bildirim_mesaji = ""
        cevap_geri_bildirim_rengi = SIYAH
        OYUN_DURUMU = DURUM_MEKAN_SECIM

def ekran_not_defteri():
    EKRAN.fill(BEYAZ)
    baslik = FONT_BASLIK.render("Dedektif Not Defteri", True, SIYAH)
    baslik_dikdortgen = baslik.get_rect(center=(GENISLIK / 2, 50))
    EKRAN.blit(baslik, baslik_dikdortgen)

    y_offset = 150
    for mekan, durum in dedektif_not_defteri.items():
        durum_renk = YESIL if durum == "Başarılı" else KIRMIZI if durum == "Tekrar Denemeli" else KOYU_GRI
        metin_yuzey = FONT_NORMAL.render(f"{mekan}: {durum}", True, durum_renk)
        metin_dikdortgen = metin_yuzey.get_rect(center=(GENISLIK / 2, y_offset))
        EKRAN.blit(metin_yuzey, metin_dikdortgen)
        y_offset += 50
    
    parca_sayisi_metin = FONT_NORMAL.render(f"Bulunan Parçalar: {form_parcalari_bulundu}/{gerekli_parca_sayisi}", True, MAVI)
    parca_sayisi_dikdortgen = parca_sayisi_metin.get_rect(center=(GENISLIK / 2, y_offset + 50))
    EKRAN.blit(parca_sayisi_metin, parca_sayisi_dikdortgen)

    global OYUN_DURUMU
    if buton_ciz(EKRAN, "GERİ DÖN", GENISLIK / 2 - 100, YUKSEKLIK - 80, 200, 60, MAVI, GRI, FONT_NORMAL):
        OYUN_DURUMU = DURUM_MEKAN_SECIM

def ekran_oyun_sonu():
    EKRAN.fill(YESIL)
    baslik = FONT_BASLIK.render("TEBRİKLER DEDEKTİF!", True, BEYAZ)
    baslik_dikdortgen = baslik.get_rect(center=(GENISLIK / 2, YUKSEKLIK / 3))
    EKRAN.blit(baslik, baslik_dikdortgen)

    mesaj = FONT_NORMAL.render("Tüm formül parçalarını buldun ve evreni kurtardın!", True, BEYAZ)
    mesaj_dikdortgen = mesaj.get_rect(center=(GENISLIK / 2, YUKSEKLIK / 2))
    EKRAN.blit(mesaj, mesaj_dikdortgen)
    
    if buton_ciz(EKRAN, "ÇIKIŞ", GENISLIK / 2 - 75, YUKSEKLIK - 100, 150, 50, KIRMIZI, KOYU_GRI, FONT_NORMAL):
        pygame.quit()
        sys.exit()

# --- ANA OYUN DÖNGÜSÜ ---
def oyun_dongusu():
    global OYUN_DURUMU, cevap_kutusu_metin

    calisiyor = True
    while calisiyor:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                calisiyor = False
            
            if OYUN_DURUMU == DURUM_SORU_EKRANI:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        cevap_kutusu_metin = cevap_kutusu_metin[:-1]
                    elif event.unicode.isdigit():
                        cevap_kutusu_metin += event.unicode
                    elif event.key == pygame.K_RETURN:
                        try:
                            girilen_cevap = int(cevap_kutusu_metin)
                            # Bu değişkenler bu scope'ta doğrudan atanacağı (değiştirileceği) için global bildirimine ihtiyaç duyar
                            global form_parcalari_bulundu, cevap_geri_bildirim_mesaji, cevap_geri_bildirim_rengi

                            if girilen_cevap == aktif_dogru_cevap:
                                cevap_geri_bildirim_mesaji = "Doğru! Formül parçasını buldun!"
                                cevap_geri_bildirim_rengi = YESIL
                                if dedektif_not_defteri[aktif_mekan["ad"]] != "Başarılı":
                                    dedektif_not_defteri[aktif_mekan["ad"]] = "Başarılı"
                                    form_parcalari_bulundu += 1
                                pygame.time.wait(1000)
                                cevap_kutusu_metin = ""
                                cevap_geri_bildirim_mesaji = ""
                                cevap_geri_bildirim_rengi = SIYAH
                                OYUN_DURUMU = DURUM_MEKAN_SECIM
                            else:
                                cevap_geri_bildirim_mesaji = "Yanlış cevap. Tekrar dene."
                                cevap_geri_bildirim_rengi = KIRMIZI
                        except ValueError:
                            cevap_geri_bildirim_mesaji = "Lütfen geçerli bir sayı girin."
                            cevap_geri_bildirim_rengi = KIRMIZI

        if OYUN_DURUMU == DURUM_ANA_MENU:
            ekran_ana_menu()
        elif OYUN_DURUMU == DURUM_MEKAN_SECIM:
            if all(durum == "Başarılı" for durum in dedektif_not_defteri.values()):
                OYUN_DURUMU = DURUM_OYUN_SONU
            else:
                ekran_mekan_secim()
        elif OYUN_DURUMU == DURUM_SORU_EKRANI:
            ekran_soru()
        elif OYUN_DURUMU == DURUM_NOT_DEFTERI:
            ekran_not_defteri()
        elif OYUN_DURUMU == DURUM_OYUN_SONU:
            ekran_oyun_sonu()
        
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    oyun_dongusu()