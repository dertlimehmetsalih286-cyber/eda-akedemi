from flask import Flask, render_template, request, redirect, url_for, session
import requests

app = Flask(__name__)
app.secret_key = "eda_akademi_super_gizli_anahtar"

# Firebase REST API Bağlantıları
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
            
        veriler = cevap.json().get('documents', [])
        giris_basarili = False
        bulunan_rol = ""
        
        for doc in veriler:
            alanlar = doc.get('fields', {})
            db_kullanici = alanlar.get('kullanici_adi', {}).get('stringValue', '')
            db_sifre = alanlar.get('sifre', {}).get('stringValue', '')
            db_rol = alanlar.get('rol', {}).get('stringValue', '')
            db_isim = alanlar.get('isim', {}).get('stringValue', db_kullanici.capitalize())
            
            if db_kullanici == kullanici and db_sifre == sifre:
                giris_basarili = True
                bulunan_rol = db_rol
                session['kullanici_adi'] = db_kullanici
                session['rol'] = db_rol
                session['isim'] = db_isim
                break 
            
        if giris_basarili:
            if bulunan_rol == 'ogretmen': return redirect(url_for('ogretmen_paneli'))
            elif bulunan_rol == 'ogrenci': return redirect(url_for('ogrenci_dashboard'))
        else:
            return "<h1>Hata: Kullanıcı adı veya şifre yanlış!</h1>"
    except Exception as e:
        return f"Sistem Hatası: {e}"

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# --- ÖĞRETMEN ROTALARI ---
@app.route('/ogretmen')
def ogretmen_paneli(): return render_template('ogretmen.html')
@app.route('/ogrenciler')
def ogrenciler(): return render_template('ogrenciler.html')
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
        gorevler.reverse()
        return render_template('gorev.html', gorevler=gorevler)
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
        k_list.reverse()
        return render_template('kaynaklar.html', kaynaklar=k_list)
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

# --- ÖĞRENCİ ROTALARI ---
@app.route('/ogrenci')
def ogrenci_dashboard():
    if session.get('rol') != 'ogrenci': return redirect(url_for('index'))
    return render_template('ogrenci_dashboard.html')

@app.route('/ogrenci_takvim')
def ogrenci_takvim():
    if session.get('rol') != 'ogrenci': return redirect(url_for('index'))
    try:
        cevap = requests.get(FIREBASE_EVENT_URL)
        etkinlikler = [{"baslik": d.get('fields', {}).get('baslik', {}).get('stringValue', ''), "aciklama": d.get('fields', {}).get('aciklama', {}).get('stringValue', ''), "tarih": d.get('fields', {}).get('tarih', {}).get('stringValue', ''), "tur": d.get('fields', {}).get('tur', {}).get('stringValue', '')} for d in cevap.json().get('documents', [])] if cevap.status_code == 200 else []
        return render_template('ogrenci_takvim.html', etkinlikler=etkinlikler)
    except: return render_template('ogrenci_takvim.html', etkinlikler=[])

# ... diğer kodların ...

# Senin kodunu buraya yapıştırıyoruz:
@app.route('/ogrenci_gorevler')
def ogrenci_gorevler():
    if session.get('rol') != 'ogrenci': return redirect(url_for('index'))
    try:
        cevap = requests.get(FIREBASE_TASK_URL)
        gorevler = []
        if cevap.status_code == 200:
            for doc in cevap.json().get('documents', []):
                alanlar = doc.get('fields', {})
                g_id = doc.get('name', '').split('/')[-1] 
                gorevler.append({
                    "id": g_id,
                    "sinav_turu": alanlar.get('sinav_turu', {}).get('stringValue', ''),
                    "ders": alanlar.get('ders', {}).get('stringValue', ''),
                    "baslik": alanlar.get('baslik', {}).get('stringValue', ''),
                    "aciklama": alanlar.get('aciklama', {}).get('stringValue', ''),
                    "son_tarih": alanlar.get('son_tarih', {}).get('stringValue', ''),
                    "oncelik": alanlar.get('oncelik', {}).get('stringValue', '')
                })
        gorevler.reverse()
        return render_template('ogrenci_gorevler.html', gorevler=gorevler)
    except Exception:
        return render_template('ogrenci_gorevler.html', gorevler=[])

# En sonda bu satır olmalı:
if __name__ == '__main__':
    app.run(debug=True)

@app.route('/ogrenci_testler')
def ogrenci_testler():
    if session.get('rol') != 'ogrenci': return redirect(url_for('index'))
    quizler, sorular = [], []
    try:
        # Firebase'den öğretmen tarafından oluşturulan quizleri ve soruları çekiyoruz
        res_q = requests.get(FIREBASE_QUIZ_URL)
        if res_q.status_code == 200:
            for doc in res_q.json().get('documents', []):
                fields = doc.get('fields', {})
                quizler.append({
                    "id": doc.get('name', '').split('/')[-1],
                    "baslik": fields.get('baslik', {}).get('stringValue', ''),
                    "hafta": fields.get('hafta', {}).get('stringValue', ''),
                    "sinav_turu": fields.get('sinav_turu', {}).get('stringValue', ''),
                    "aciklama": fields.get('aciklama', {}).get('stringValue', '')
                })
        
        res_s = requests.get(FIREBASE_QUESTION_URL)
        if res_s.status_code == 200:
            sorular = [{"quiz_id": d.get('fields', {}).get('quiz_id', {}).get('stringValue', ''), 
                        "soru_metni": d.get('fields', {}).get('soru_metni', {}).get('stringValue', ''), 
                        "a": d.get('fields', {}).get('a', {}).get('stringValue', ''), 
                        "b": d.get('fields', {}).get('b', {}).get('stringValue', ''), 
                        "c": d.get('fields', {}).get('c', {}).get('stringValue', ''), 
                        "d": d.get('fields', {}).get('d', {}).get('stringValue', ''), 
                        "dogru": d.get('fields', {}).get('dogru', {}).get('stringValue', ''), 
                        "cozum": d.get('fields', {}).get('cozum', {}).get('stringValue', '')} for d in res_s.json().get('documents', [])]
    except: pass
    return render_template('ogrenci_testler.html', quizler=quizler, sorular=sorular)
@app.route('/ogrenci_kaynaklar')
def ogrenci_kaynaklar(): return "<h1 style='padding:50px; font-family:sans-serif;'>Kaynaklar Bir Sonraki Adımda Eklenecek...</h1>"

@app.route('/ogrenci_siralama')
def ogrenci_siralama(): return "<h1 style='padding:50px; font-family:sans-serif;'>Sıralama Bir Sonraki Adımda Eklenecek...</h1>"

if __name__ == '__main__':
    app.run(debug=True)
