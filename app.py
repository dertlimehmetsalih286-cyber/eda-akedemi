from flask import Flask, render_template, request, redirect, url_for, session
import requests
from apscheduler.schedulers.background import BackgroundScheduler
import datetime

app = Flask(__name__)
app.secret_key = "eda_akademi_super_gizli_anahtar"

# --- FİREBASE BAĞLANTILARI ---
FIREBASE_USER_URL = "https://firestore.googleapis.com/v1/projects/edaakedemi-a9543/databases/(default)/documents/kullanicilar"
FIREBASE_TASK_URL = "https://firestore.googleapis.com/v1/projects/edaakedemi-a9543/databases/(default)/documents/gorevler"
FIREBASE_QUIZ_URL = "https://firestore.googleapis.com/v1/projects/edaakedemi-a9543/databases/(default)/documents/quizler"
FIREBASE_QUESTION_URL = "https://firestore.googleapis.com/v1/projects/edaakedemi-a9543/databases/(default)/documents/sorular"
FIREBASE_RESOURCE_URL = "https://firestore.googleapis.com/v1/projects/edaakedemi-a9543/databases/(default)/documents/kaynaklar"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    kullanici = request.form.get('username')
    sifre = request.form.get('password')
    try:
        cevap = requests.get(FIREBASE_USER_URL)
        if cevap.status_code != 200: return "<h1>Hata: Veritabanına ulaşılamadı.</h1>"
        for doc in cevap.json().get('documents', []):
            alanlar = doc.get('fields', {})
            db_kullanici = alanlar.get('kullanici_adi', {}).get('stringValue', '')
            db_sifre = alanlar.get('sifre', {}).get('stringValue', '')
            db_rol = alanlar.get('rol', {}).get('stringValue', '')
            db_isim = alanlar.get('isim', {}).get('stringValue', db_kullanici.capitalize())
            
            if db_kullanici == kullanici and db_sifre == sifre:
                session['kullanici_adi'] = db_kullanici
                session['rol'] = db_rol
                session['isim'] = db_isim
                return redirect(url_for('ogretmen_paneli') if db_rol == 'ogretmen' else url_for('ogrenci_dashboard'))
        return "<h1>Hata: Kullanıcı adı veya şifre yanlış!</h1>"
    except Exception as e: return f"Sistem Hatası: {e}"

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# =========================================================================
# ÖĞRETMEN PANELİ ROTALARI
# =========================================================================

@app.route('/ogretmen')
def ogretmen_paneli():
    if session.get('rol') != 'ogretmen': return redirect(url_for('index'))
    return render_template('ogretmen.html')

# ÖĞRENCİLER ROTASI GERİ EKLENDİ (HATASIZ HİZALAMA)
@app.route('/ogrenciler')
def ogrenciler():
    if session.get('rol') != 'ogretmen': return redirect(url_for('index'))
    try:
        cevap = requests.get(FIREBASE_USER_URL)
        ogrenci_listesi = []
        if cevap.status_code == 200:
            for doc in cevap.json().get('documents', []):
                alanlar = doc.get('fields', {})
                if alanlar.get('rol', {}).get('stringValue') == 'ogrenci':
                    puan_val = alanlar.get('puan', {})
                    puan = int(puan_val.get('integerValue', puan_val.get('stringValue', '0')))
                    tamamlanan = puan // 10 
                    ogrenci_listesi.append({"isim": alanlar.get('isim', {}).get('stringValue', 'Öğrenci'), "kullanici_adi": alanlar.get('kullanici_adi', {}).get('stringValue', ''), "puan": puan, "tamamlanan": tamamlanan})
        
        ogrenci_listesi = sorted(ogrenci_listesi, key=lambda x: x['puan'], reverse=True)
        toplam_ogrenci = len(ogrenci_listesi)
        en_yuksek_puan = ogrenci_listesi[0]['puan'] if toplam_ogrenci > 0 else 0
        toplam_tamamlanan = sum(o['tamamlanan'] for o in ogrenci_listesi)
        return render_template('ogrenciler.html', ogrenciler=ogrenci_listesi, toplam_ogrenci=toplam_ogrenci, en_yuksek_puan=en_yuksek_puan, toplam_tamamlanan=toplam_tamamlanan)
    except: return render_template('ogrenciler.html', ogrenciler=[], toplam_ogrenci=0, en_yuksek_puan=0, toplam_tamamlanan=0)


@app.route('/ogretmen_analiz')
def ogretmen_analiz():
    if session.get('rol') != 'ogretmen': return redirect(url_for('index'))
    try:
        cevap = requests.get(FIREBASE_USER_URL)
        ogrenciler = []
        toplam_puan = 0
        if cevap.status_code == 200:
            for doc in cevap.json().get('documents', []):
                alanlar = doc.get('fields', {})
                if alanlar.get('rol', {}).get('stringValue') == 'ogrenci':
                    p_val = alanlar.get('puan', {})
                    puan = int(p_val.get('integerValue', p_val.get('stringValue', '0')))
                    toplam_puan += puan
                    ogrenciler.append({"isim": alanlar.get('isim', {}).get('stringValue', 'Öğrenci'), "puan": puan})
        
        ogrenci_sayisi = len(ogrenciler)
        ortalama = (toplam_puan / ogrenci_sayisi) if ogrenci_sayisi > 0 else 0
        sirali = sorted(ogrenciler, key=lambda x: x['puan'], reverse=True)
        en_iyi = sirali[0]['isim'] if ogrenci_sayisi > 0 else "Yok"
        en_dusuk = sirali[-1]['isim'] if ogrenci_sayisi > 0 else "Yok"
        
        tavsiyeler = []
        if ortalama < 30:
            tavsiyeler.append("Sınıfın genel başarı ortalaması zayıf görünüyor. Kaynaklar bölümüne yeni dökümanlar yüklemeniz önerilir.")
        elif ortalama < 60:
            tavsiyeler.append("Sınıf performansı dengeli ilerliyor. Quiz Yönetimi kısmından yeni tarama testleri oluşturabilirsiniz.")
        else:
            tavsiyeler.append("Harika! Sınıf ortalaması mükemmel. Zor seviye YKS/LGS görevleri ekleyebilirsiniz.")
            
        return render_template('ogretmen_analiz.html', tavsiyeler=tavsiyeler, ortalama=int(ortalama), en_iyi=en_iyi, en_dusuk=en_dusuk, toplam_ogrenci=ogrenci_sayisi)
    except:
        return render_template('ogretmen_analiz.html', tavsiyeler=["Veritabanı hatası."], ortalama=0, en_iyi="Yok", en_dusuk="Yok", toplam_ogrenci=0)

# GÖREV YÖNETİMİ (TAKVİM İLE BİRLEŞİK)
@app.route('/gorev')
def gorev():
    if session.get('rol') != 'ogretmen': return redirect(url_for('index'))
    gorevler = []
    try:
        cevap = requests.get(FIREBASE_TASK_URL)
        if cevap.status_code == 200:
            for d in cevap.json().get('documents', []):
                f = d.get('fields', {})
                gorevler.append({
                    "sinav_turu": f.get('sinav_turu', {}).get('stringValue', ''),
                    "ders": f.get('ders', {}).get('stringValue', ''),
                    "baslik": f.get('baslik', {}).get('stringValue', ''),
                    "son_tarih": f.get('son_tarih', {}).get('stringValue', ''),
                    "oncelik": f.get('oncelik', {}).get('stringValue', '')
                })
        gorevler.reverse()
    except: pass
    return render_template('gorev.html', gorevler=gorevler)

@app.route('/quiz')
def quiz():
    if session.get('rol') != 'ogretmen': return redirect(url_for('index'))
    quizler, sorular = [], []
    try:
        res_q = requests.get(FIREBASE_QUIZ_URL)
        if res_q.status_code == 200:
            for d in res_q.json().get('documents', []):
                quizler.append({"id": d.get('name', '').split('/')[-1], "baslik": d.get('fields', {}).get('baslik', {}).get('stringValue', 'İsimsiz Quiz')})
    except: pass
    return render_template('quiz.html', quizler=quizler, sorular=sorular)

@app.route('/quiz_sonuclari/<quiz_id>')
def quiz_sonuclari(quiz_id):
    if session.get('rol') != 'ogretmen': return redirect(url_for('index'))
    quiz_baslik, sorular, ogrenciler = "Quiz Detayı", [], []
    try:
        res_q = requests.get(FIREBASE_QUIZ_URL)
        if res_q.status_code == 200:
            for d in res_q.json().get('documents', []):
                if d.get('name', '').split('/')[-1] == quiz_id:
                    quiz_baslik = d.get('fields', {}).get('baslik', {}).get('stringValue', 'İsimsiz Quiz')
        
        res_s = requests.get(FIREBASE_QUESTION_URL)
        if res_s.status_code == 200:
            for d in res_s.json().get('documents', []):
                f = d.get('fields', {})
                if f.get('quiz_id', {}).get('stringValue', '') == quiz_id:
                    sorular.append({"soru_metni": f.get('soru_metni', {}).get('stringValue', ''), "dogru": f.get('dogru', {}).get('stringValue', ''), "cozum": f.get('cozum', {}).get('stringValue', '')})
        
        res_u = requests.get(FIREBASE_USER_URL)
        if res_u.status_code == 200:
            for doc in res_u.json().get('documents', []):
                f = doc.get('fields', {})
                if f.get('rol', {}).get('stringValue') == 'ogrenci':
                    ogrenciler.append({"isim": f.get('isim', {}).get('stringValue', 'Öğrenci'), "puan": int(f.get('puan', {}).get('integerValue', f.get('puan', {}).get('stringValue', '0')))})
            ogrenciler = sorted(ogrenciler, key=lambda x: x['puan'], reverse=True)
    except: pass
    return render_template('quiz_sonuclari.html', quiz_id=quiz_id, quiz_baslik=quiz_baslik, sorular=sorular, ogrenciler=ogrenciler)

@app.route('/kaynaklar')
def kaynaklar():
    try:
        cevap = requests.get(FIREBASE_RESOURCE_URL)
        k_list = [{"baslik": d.get('fields', {}).get('baslik', {}).get('stringValue', ''), "aciklama": d.get('fields', {}).get('aciklama', {}).get('stringValue', ''), "tur": d.get('fields', {}).get('tur', {}).get('stringValue', ''), "url": d.get('fields', {}).get('url', {}).get('stringValue', '')} for d in cevap.json().get('documents', [])] if cevap.status_code == 200 else []
        k_list.reverse()
        return render_template('kaynaklar.html', kaynaklar=k_list)
    except: return render_template('kaynaklar.html', kaynaklar=[])

# --- ÖĞRETMEN POST İŞLEMLERİ ---
@app.route('/add-task', methods=['POST'])
def add_task(): 
    requests.post(FIREBASE_TASK_URL, json={"fields": {"sinav_turu": {"stringValue": request.form.get('sinav_turu')}, "ders": {"stringValue": request.form.get('ders')}, "baslik": {"stringValue": request.form.get('baslik')}, "aciklama": {"stringValue": request.form.get('aciklama', '')}, "son_tarih": {"stringValue": request.form.get('son_tarih')}, "oncelik": {"stringValue": request.form.get('oncelik')}}})
    return redirect(url_for('gorev'))

@app.route('/add-quiz', methods=['POST'])
def add_quiz(): requests.post(FIREBASE_QUIZ_URL, json={"fields": {"baslik": {"stringValue": request.form.get('baslik')}, "hafta": {"stringValue": request.form.get('hafta')}, "sinav_turu": {"stringValue": request.form.get('sinav_turu')}, "aciklama": {"stringValue": request.form.get('aciklama', '')}}}); return redirect(url_for('quiz'))

@app.route('/add-question', methods=['POST'])
def add_question(): requests.post(FIREBASE_QUESTION_URL, json={"fields": {"quiz_id": {"stringValue": request.form.get('quiz_id')}, "soru_metni": {"stringValue": request.form.get('soru_metni')}, "a": {"stringValue": request.form.get('a')}, "b": {"stringValue": request.form.get('b')}, "c": {"stringValue": request.form.get('c')}, "d": {"stringValue": request.form.get('d')}, "dogru": {"stringValue": request.form.get('dogru')}, "cozum": {"stringValue": request.form.get('cozum', '')}}}); return redirect(url_for('quiz'))

@app.route('/add-resource', methods=['POST'])
def add_resource(): requests.post(FIREBASE_RESOURCE_URL, json={"fields": {"baslik": {"stringValue": request.form.get('baslik')}, "aciklama": {"stringValue": request.form.get('aciklama', '')}, "tur": {"stringValue": request.form.get('tur')}, "url": {"stringValue": request.form.get('url')}}}); return redirect(url_for('kaynaklar'))

# =========================================================================
# ÖĞRENCİ PANELİ ROTALARI
# =========================================================================

@app.route('/ogrenci')
def ogrenci_dashboard(): 
    if session.get('rol') != 'ogrenci': return redirect(url_for('index'))
    return render_template('ogrenci_dashboard.html')

@app.route('/ogrenci_gorevler')
def ogrenci_gorevler():
    if session.get('rol') != 'ogrenci': return redirect(url_for('index'))
    try:
        cevap = requests.get(FIREBASE_TASK_URL)
        gorevler = [{"id": d.get('name', '').split('/')[-1], "sinav_turu": d.get('fields', {}).get('sinav_turu', {}).get('stringValue', ''), "ders": d.get('fields', {}).get('ders', {}).get('stringValue', ''), "baslik": d.get('fields', {}).get('baslik', {}).get('stringValue', ''), "son_tarih": d.get('fields', {}).get('son_tarih', {}).get('stringValue', ''), "oncelik": d.get('fields', {}).get('oncelik', {}).get('stringValue', '')} for d in cevap.json().get('documents', [])] if cevap.status_code == 200 else []
        gorevler.reverse()
        return render_template('ogrenci_gorevler.html', gorevler=gorevler)
    except: return render_template('ogrenci_gorevler.html', gorevler=[])

@app.route('/ogrenci_testler')
def ogrenci_testler():
    if session.get('rol') != 'ogrenci': return redirect(url_for('index'))
    quizler, sorular = [], []
    try:
        res_q = requests.get(FIREBASE_QUIZ_URL)
        if res_q.status_code == 200: quizler = [{"id": d.get('name', '').split('/')[-1], "baslik": d.get('fields', {}).get('baslik', {}).get('stringValue', '')} for d in res_q.json().get('documents', [])]
    except: pass
    return render_template('ogrenci_testler.html', quizler=quizler, sorular=sorular)

@app.route('/ogrenci_kaynaklar')
def ogrenci_kaynaklar():
    if session.get('rol') != 'ogrenci': return redirect(url_for('index'))
    try:
        cevap = requests.get(FIREBASE_RESOURCE_URL)
        k_list = [{"baslik": d.get('fields', {}).get('baslik', {}).get('stringValue', ''), "url": d.get('fields', {}).get('url', {}).get('stringValue', '')} for d in cevap.json().get('documents', [])] if cevap.status_code == 200 else []
        return render_template('ogrenci_kaynaklar.html', kaynaklar=k_list)
    except: return render_template('ogrenci_kaynaklar.html', kaynaklar=[])

@app.route('/ogrenci_siralama')
def ogrenci_siralama():
    if session.get('rol') != 'ogrenci': return redirect(url_for('index'))
    try:
        cevap = requests.get(FIREBASE_USER_URL)
        ogrenciler = [{"isim": d.get('fields', {}).get('isim', {}).get('stringValue', 'Öğrenci'), "puan": int(d.get('fields', {}).get('puan', {}).get('integerValue', d.get('fields', {}).get('puan', {}).get('stringValue', '0')))} for d in cevap.json().get('documents', []) if d.get('fields', {}).get('rol', {}).get('stringValue') == 'ogrenci'] if cevap.status_code == 200 else []
        return render_template('ogrenci_siralama.html', ogrenciler=sorted(ogrenciler, key=lambda x: x['puan'], reverse=True))
    except: return render_template('ogrenci_siralama.html', ogrenciler=[])

@app.route('/puan_ekle', methods=['POST'])
def puan_ekle():
    if session.get('rol') != 'ogrenci': return {"status": "error"}
    kazanilan_puan = int(request.json.get('puan', 0))
    kullanici_adi = session.get('kullanici_adi')
    try:
        res = requests.get(FIREBASE_USER_URL)
        if res.status_code == 200:
            for doc in res.json().get('documents', []):
                fields = doc.get('fields', {})
                if fields.get('kullanici_adi', {}).get('stringValue') == kullanici_adi:
                    doc_id = doc.get('name', '').split('/')[-1]
                    mevcut_puan = int(fields.get('puan', {}).get('integerValue', fields.get('puan', {}).get('stringValue', '0')))
                    requests.patch(f"{FIREBASE_USER_URL}/{doc_id}?updateMask.fieldPaths=puan", json={"fields": {"puan": {"integerValue": str(mevcut_puan + kazanilan_puan)}}})
                    return {"status": "success"}
    except: pass
    return {"status": "error"}

# =========================================================================
# YAPAY ZEKA ZAMANLAYICI (AI OTOMATİK QUİZ)
# =========================================================================
def yapay_zeka_quiz_hazirla():
    try:
        print("🤖 Yapay Zeka Devrede: Takvim analiz ediliyor...")
        takvim_konulari = []
        res = requests.get(FIREBASE_TASK_URL)
        if res.status_code == 200:
            for d in res.json().get('documents', []):
                f = d.get('fields', {})
                ders = f.get('ders', {}).get('stringValue', '')
                baslik = f.get('baslik', {}).get('stringValue', '')
                if ders and baslik: takvim_konulari.append(f"{ders} - {baslik}")
        
        haftanin_konulari = takvim_konulari[-3:] if takvim_konulari else ["Genel Kültür"]
        konu_metni = ", ".join(haftanin_konulari)
        
        yeni_quiz = requests.post(FIREBASE_QUIZ_URL, json={
            "fields": {
                "baslik": {"stringValue": f"🤖 AI Çarşamba Quizi: {datetime.datetime.now().strftime('%d.%m.%Y')}"},
                "sinav_turu": {"stringValue": "Yapay Zeka Üretimi"},
                "aciklama": {"stringValue": f"Bu haftanın konuları ({konu_metni}) baz alınarak otomatik hazırlanmıştır."}
            }
        })
        
        if yeni_quiz.status_code == 200:
            quiz_id = yeni_quiz.json().get('name').split('/')[-1]
            ai_sorular = [
                {"soru": f"'{haftanin_konulari[0]}' konusuyla ilgili temel kural nedir?", "a": "Kural A", "b": "Kural B", "c": "Kural C", "d": "Kural D", "dogru": "A", "cozum": "AI Notu: Takvimden çekildi."},
                {"soru": f"Aşağıdakilerden hangisi son işlenen konunun bir alt başlığıdır?", "a": "Başlık 1", "b": "Başlık 2", "c": "Başlık 3", "d": "Başlık 4", "dogru": "C", "cozum": "AI araştırmasına göre C şıkkı doğru."}
            ]
            for soru in ai_sorular:
                requests.post(FIREBASE_QUESTION_URL, json={"fields": {"quiz_id": {"stringValue": quiz_id}, "soru_metni": {"stringValue": soru['soru']}, "a": {"stringValue": soru['a']}, "b": {"stringValue": soru['b']}, "c": {"stringValue": soru['c']}, "d": {"stringValue": soru['d']}, "dogru": {"stringValue": soru['dogru']}, "cozum": {"stringValue": soru['cozum']}}})
            print("✅ Yapay Zeka Quizi Veritabanına Yüklendi!")
    except Exception as e: print(f"Yapay Zeka Quiz Üretim Hatası: {e}")

scheduler = BackgroundScheduler()
scheduler.add_job(func=yapay_zeka_quiz_hazirla, trigger="cron", day_of_week='wed', hour=9, minute=0)
scheduler.start()

if __name__ == '__main__':
    app.run(debug=True)
