from flask import Flask, render_template, request, redirect, url_for, session
import requests

app = Flask(__name__)
app.secret_key = "eda_akademi_super_gizli_anahtar"

FIREBASE_USER_URL = "https://firestore.googleapis.com/v1/projects/edaakedemi-a9543/databases/(default)/documents/kullanicilar"
FIREBASE_EVENT_URL = "https://firestore.googleapis.com/v1/projects/edaakedemi-a9543/databases/(default)/documents/etkinlikler"
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

# ==================== ÖĞRETMEN ROTALARI ====================
@app.route('/ogretmen')
def ogretmen_paneli(): return render_template('ogretmen.html')
@app.route('/ogrenciler')
def ogrenciler():
    try:
        cevap = requests.get(FIREBASE_USER_URL)
        ogrenci_listesi = [{"isim": d.get('fields', {}).get('isim', {}).get('stringValue', 'Öğrenci'), "kullanici_adi": d.get('fields', {}).get('kullanici_adi', {}).get('stringValue', ''), "puan": int(d.get('fields', {}).get('puan', {}).get('integerValue', d.get('fields', {}).get('puan', {}).get('stringValue', '0')))} for d in cevap.json().get('documents', []) if d.get('fields', {}).get('rol', {}).get('stringValue') == 'ogrenci'] if cevap.status_code == 200 else []
        return render_template('ogrenciler.html', ogrenciler=sorted(ogrenci_listesi, key=lambda x: x['puan'], reverse=True))
    except: return render_template('ogrenciler.html', ogrenciler=[])
@app.route('/takvim')
def takvim():
    try:
        cevap = requests.get(FIREBASE_EVENT_URL)
        etkinlikler = [{"baslik": d.get('fields', {}).get('baslik', {}).get('stringValue', ''), "aciklama": d.get('fields', {}).get('aciklama', {}).get('stringValue', ''), "tarih": d.get('fields', {}).get('tarih', {}).get('stringValue', ''), "tur": d.get('fields', {}).get('tur', {}).get('stringValue', '')} for d in cevap.json().get('documents', [])] if cevap.status_code == 200 else []
        return render_template('takvim.html', etkinlikler=etkinlikler)
    except: return render_template('takvim.html', etkinlikler=[])
@app.route('/gorev')
def gorev():
    try:
        cevap = requests.get(FIREBASE_TASK_URL)
        gorevler = [{"sinav_turu": d.get('fields', {}).get('sinav_turu', {}).get('stringValue', ''), "ders": d.get('fields', {}).get('ders', {}).get('stringValue', ''), "baslik": d.get('fields', {}).get('baslik', {}).get('stringValue', ''), "aciklama": d.get('fields', {}).get('aciklama', {}).get('stringValue', ''), "son_tarih": d.get('fields', {}).get('son_tarih', {}).get('stringValue', ''), "oncelik": d.get('fields', {}).get('oncelik', {}).get('stringValue', '')} for d in cevap.json().get('documents', [])] if cevap.status_code == 200 else []
        gorevler.reverse(); return render_template('gorev.html', gorevler=gorevler)
    except: return render_template('gorev.html', gorevler=[])
@app.route('/quiz')
def quiz():
    quizler, sorular = [], []
    try:
        res_q = requests.get(FIREBASE_QUIZ_URL)
        if res_q.status_code == 200: quizler = [{"id": d.get('name', '').split('/')[-1], "baslik": d.get('fields', {}).get('baslik', {}).get('stringValue', ''), "hafta": d.get('fields', {}).get('hafta', {}).get('stringValue', ''), "sinav_turu": d.get('fields', {}).get('sinav_turu', {}).get('stringValue', ''), "aciklama": d.get('fields', {}).get('aciklama', {}).get('stringValue', '')} for d in res_q.json().get('documents', [])]
        quizler.reverse()
        res_s = requests.get(FIREBASE_QUESTION_URL)
        if res_s.status_code == 200: sorular = [{"quiz_id": d.get('fields', {}).get('quiz_id', {}).get('stringValue', ''), "soru_metni": d.get('fields', {}).get('soru_metni', {}).get('stringValue', ''), "a": d.get('fields', {}).get('a', {}).get('stringValue', ''), "b": d.get('fields', {}).get('b', {}).get('stringValue', ''), "c": d.get('fields', {}).get('c', {}).get('stringValue', ''), "d": d.get('fields', {}).get('d', {}).get('stringValue', ''), "dogru": d.get('fields', {}).get('dogru', {}).get('stringValue', ''), "cozum": d.get('fields', {}).get('cozum', {}).get('stringValue', '')} for d in res_s.json().get('documents', [])]
    except: pass
    return render_template('quiz.html', quizler=quizler, sorular=sorular)
@app.route('/kaynaklar')
def kaynaklar():
    try:
        cevap = requests.get(FIREBASE_RESOURCE_URL)
        k_list = [{"baslik": d.get('fields', {}).get('baslik', {}).get('stringValue', ''), "aciklama": d.get('fields', {}).get('aciklama', {}).get('stringValue', ''), "tur": d.get('fields', {}).get('tur', {}).get('stringValue', ''), "url": d.get('fields', {}).get('url', {}).get('stringValue', '')} for d in cevap.json().get('documents', [])] if cevap.status_code == 200 else []
        k_list.reverse(); return render_template('kaynaklar.html', kaynaklar=k_list)
    except: return render_template('kaynaklar.html', kaynaklar=[])

@app.route('/add-event', methods=['POST'])
def add_event(): requests.post(FIREBASE_EVENT_URL, json={"fields": {"baslik": {"stringValue": request.form.get('baslik')}, "aciklama": {"stringValue": request.form.get('aciklama', '')}, "tarih": {"stringValue": request.form.get('tarih')}, "tur": {"stringValue": request.form.get('tur')}}}); return redirect(url_for('takvim'))
@app.route('/add-task', methods=['POST'])
def add_task(): requests.post(FIREBASE_TASK_URL, json={"fields": {"sinav_turu": {"stringValue": request.form.get('sinav_turu')}, "ders": {"stringValue": request.form.get('ders')}, "baslik": {"stringValue": request.form.get('baslik')}, "aciklama": {"stringValue": request.form.get('aciklama', '')}, "son_tarih": {"stringValue": request.form.get('son_tarih')}, "oncelik": {"stringValue": request.form.get('oncelik')}}}); return redirect(url_for('gorev'))
@app.route('/add-quiz', methods=['POST'])
def add_quiz(): requests.post(FIREBASE_QUIZ_URL, json={"fields": {"baslik": {"stringValue": request.form.get('baslik')}, "hafta": {"stringValue": request.form.get('hafta')}, "sinav_turu": {"stringValue": request.form.get('sinav_turu')}, "aciklama": {"stringValue": request.form.get('aciklama', '')}}}); return redirect(url_for('quiz'))
@app.route('/add-question', methods=['POST'])
def add_question(): requests.post(FIREBASE_QUESTION_URL, json={"fields": {"quiz_id": {"stringValue": request.form.get('quiz_id')}, "soru_metni": {"stringValue": request.form.get('soru_metni')}, "a": {"stringValue": request.form.get('a')}, "b": {"stringValue": request.form.get('b')}, "c": {"stringValue": request.form.get('c')}, "d": {"stringValue": request.form.get('d')}, "dogru": {"stringValue": request.form.get('dogru')}, "cozum": {"stringValue": request.form.get('cozum', '')}}}); return redirect(url_for('quiz'))
@app.route('/add-resource', methods=['POST'])
def add_resource(): requests.post(FIREBASE_RESOURCE_URL, json={"fields": {"baslik": {"stringValue": request.form.get('baslik')}, "aciklama": {"stringValue": request.form.get('aciklama', '')}, "tur": {"stringValue": request.form.get('tur')}, "url": {"stringValue": request.form.get('url')}}}); return redirect(url_for('kaynaklar'))


# ==================== ÖĞRENCİ ROTALARI ====================
@app.route('/ogrenci')
def ogrenci_dashboard(): return render_template('ogrenci_dashboard.html') if session.get('rol') == 'ogrenci' else redirect(url_for('index'))
@app.route('/ogrenci_takvim')
def ogrenci_takvim():
    try:
        cevap = requests.get(FIREBASE_EVENT_URL)
        etkinlikler = [{"baslik": d.get('fields', {}).get('baslik', {}).get('stringValue', ''), "aciklama": d.get('fields', {}).get('aciklama', {}).get('stringValue', ''), "tarih": d.get('fields', {}).get('tarih', {}).get('stringValue', ''), "tur": d.get('fields', {}).get('tur', {}).get('stringValue', '')} for d in cevap.json().get('documents', [])] if cevap.status_code == 200 else []
        return render_template('ogrenci_takvim.html', etkinlikler=etkinlikler)
    except: return render_template('ogrenci_takvim.html', etkinlikler=[])
@app.route('/ogrenci_gorevler')
def ogrenci_gorevler():
    try:
        cevap = requests.get(FIREBASE_TASK_URL)
        gorevler = [{"id": d.get('name', '').split('/')[-1], "sinav_turu": d.get('fields', {}).get('sinav_turu', {}).get('stringValue', ''), "ders": d.get('fields', {}).get('ders', {}).get('stringValue', ''), "baslik": d.get('fields', {}).get('baslik', {}).get('stringValue', ''), "aciklama": d.get('fields', {}).get('aciklama', {}).get('stringValue', ''), "son_tarih": d.get('fields', {}).get('son_tarih', {}).get('stringValue', ''), "oncelik": d.get('fields', {}).get('oncelik', {}).get('stringValue', '')} for d in cevap.json().get('documents', [])] if cevap.status_code == 200 else []
        gorevler.reverse(); return render_template('ogrenci_gorevler.html', gorevler=gorevler)
    except: return render_template('ogrenci_gorevler.html', gorevler=[])
@app.route('/ogrenci_testler')
def ogrenci_testler():
    quizler, sorular = [], []
    try:
        res_q = requests.get(FIREBASE_QUIZ_URL)
        if res_q.status_code == 200: quizler = [{"id": d.get('name', '').split('/')[-1], "baslik": d.get('fields', {}).get('baslik', {}).get('stringValue', ''), "hafta": d.get('fields', {}).get('hafta', {}).get('stringValue', ''), "sinav_turu": d.get('fields', {}).get('sinav_turu', {}).get('stringValue', ''), "aciklama": d.get('fields', {}).get('aciklama', {}).get('stringValue', '')} for d in res_q.json().get('documents', [])]
        res_s = requests.get(FIREBASE_QUESTION_URL)
        if res_s.status_code == 200: sorular = [{"quiz_id": d.get('fields', {}).get('quiz_id', {}).get('stringValue', ''), "soru_metni": d.get('fields', {}).get('soru_metni', {}).get('stringValue', ''), "a": d.get('fields', {}).get('a', {}).get('stringValue', ''), "b": d.get('fields', {}).get('b', {}).get('stringValue', ''), "c": d.get('fields', {}).get('c', {}).get('stringValue', ''), "d": d.get('fields', {}).get('d', {}).get('stringValue', ''), "dogru": d.get('fields', {}).get('dogru', {}).get('stringValue', ''), "cozum": d.get('fields', {}).get('cozum', {}).get('stringValue', '')} for d in res_s.json().get('documents', [])]
    except: pass
    return render_template('ogrenci_testler.html', quizler=quizler, sorular=sorular)
@app.route('/ogrenci_kaynaklar')
def ogrenci_kaynaklar():
    try:
        cevap = requests.get(FIREBASE_RESOURCE_URL)
        k_list = [{"baslik": d.get('fields', {}).get('baslik', {}).get('stringValue', ''), "aciklama": d.get('fields', {}).get('aciklama', {}).get('stringValue', ''), "tur": d.get('fields', {}).get('tur', {}).get('stringValue', ''), "url": d.get('fields', {}).get('url', {}).get('stringValue', '')} for d in cevap.json().get('documents', [])] if cevap.status_code == 200 else []
        k_list.reverse(); return render_template('ogrenci_kaynaklar.html', kaynaklar=k_list)
    except: return render_template('ogrenci_kaynaklar.html', kaynaklar=[])
@app.route('/ogrenci_siralama')
def ogrenci_siralama():
    try:
        cevap = requests.get(FIREBASE_USER_URL)
        ogrenciler = [{"isim": d.get('fields', {}).get('isim', {}).get('stringValue', 'Öğrenci'), "puan": int(d.get('fields', {}).get('puan', {}).get('integerValue', d.get('fields', {}).get('puan', {}).get('stringValue', '0')))} for d in cevap.json().get('documents', []) if d.get('fields', {}).get('rol', {}).get('stringValue') == 'ogrenci'] if cevap.status_code == 200 else []
        return render_template('ogrenci_siralama.html', ogrenciler=sorted(ogrenciler, key=lambda x: x['puan'], reverse=True))
    except: return render_template('ogrenci_siralama.html', ogrenciler=[])


# --- YENİ: ANLIK PUAN EKLEME ROTASI ---
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
                    # Öğrencinin ID'sini ve Mevcut Puanını bul
                    doc_id = doc.get('name', '').split('/')[-1]
                    puan_val = fields.get('puan', {})
                    mevcut_puan = int(puan_val.get('integerValue', puan_val.get('stringValue', '0')))
                    
                    yeni_puan = mevcut_puan + kazanilan_puan
                    
                    # Veritabanında SADECE Puan hücresini güncelle (Diğer bilgiler silinmez)
                    update_url = f"{FIREBASE_USER_URL}/{doc_id}?updateMask.fieldPaths=puan"
                    payload = {"fields": {"puan": {"integerValue": str(yeni_puan)}}}
                    requests.patch(update_url, json=payload)
                    return {"status": "success", "yeni_puan": yeni_puan}
    except Exception as e:
        print("Puan Hatasi:", e)
        
    return {"status": "error"}

if __name__ == '__main__':
    app.run(debug=True)
