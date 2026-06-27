from flask import Flask, render_template, request, redirect, url_for
import requests

app = Flask(__name__)

# Firebase REST API Bağlantılarımız
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
        if cevap.status_code != 200:
            return "<h1>Hata: Veritabanına ulaşılamadı.</h1>"
            
        veriler = cevap.json().get('documents', [])
        giris_basarili = False
        bulunan_rol = ""
        
        for doc in veriler:
            alanlar = doc.get('fields', {})
            db_kullanici = alanlar.get('kullanici_adi', {}).get('stringValue', '')
            db_sifre = alanlar.get('sifre', {}).get('stringValue', '')
            db_rol = alanlar.get('rol', {}).get('stringValue', '')
            
            if db_kullanici == kullanici and db_sifre == sifre:
                giris_basarili = True
                bulunan_rol = db_rol
                break 
            
        if giris_basarili:
            if bulunan_rol == 'ogretmen':
                return redirect(url_for('ogretmen_paneli'))
            else:
                return "<h1>Öğrenci Paneli henüz yapım aşamasında...</h1>"
        else:
            return "<h1>Hata: Kullanıcı adı veya şifre yanlış!</h1>"
    except Exception as e:
        return f"Sistem Hatası: {e}"

@app.route('/ogretmen')
def ogretmen_paneli():
    return render_template('ogretmen.html')

@app.route('/ogrenciler')
def ogrenciler():
    return render_template('ogrenciler.html')

@app.route('/takvim')
def takvim():
    try:
        cevap = requests.get(FIREBASE_EVENT_URL)
        etkinlikler = []
        if cevap.status_code == 200:
            for doc in cevap.json().get('documents', []):
                alanlar = doc.get('fields', {})
                etkinlikler.append({
                    "baslik": alanlar.get('baslik', {}).get('stringValue', ''),
                    "aciklama": alanlar.get('aciklama', {}).get('stringValue', ''),
                    "tarih": alanlar.get('tarih', {}).get('stringValue', ''),
                    "tur": alanlar.get('tur', {}).get('stringValue', '')
                })
        return render_template('takvim.html', etkinlikler=etkinlikler)
    except Exception:
        return render_template('takvim.html', etkinlikler=[])

@app.route('/gorev')
def gorev():
    try:
        cevap = requests.get(FIREBASE_TASK_URL)
        gorevler = []
        if cevap.status_code == 200:
            for doc in cevap.json().get('documents', []):
                alanlar = doc.get('fields', {})
                gorevler.append({
                    "sinav_turu": alanlar.get('sinav_turu', {}).get('stringValue', ''),
                    "ders": alanlar.get('ders', {}).get('stringValue', ''),
                    "baslik": alanlar.get('baslik', {}).get('stringValue', ''),
                    "aciklama": alanlar.get('aciklama', {}).get('stringValue', ''),
                    "son_tarih": alanlar.get('son_tarih', {}).get('stringValue', ''),
                    "oncelik": alanlar.get('oncelik', {}).get('stringValue', '')
                })
        gorevler.reverse()
        return render_template('gorev.html', gorevler=gorevler)
    except Exception:
        return render_template('gorev.html', gorevler=[])

@app.route('/quiz')
def quiz():
    quizler = []
    sorular = []
    try:
        res_q = requests.get(FIREBASE_QUIZ_URL)
        if res_q.status_code == 200:
            for doc in res_q.json().get('documents', []):
                fields = doc.get('fields', {})
                q_id = doc.get('name', '').split('/')[-1] 
                quizler.append({"id": q_id, "baslik": fields.get('baslik', {}).get('stringValue', ''), "hafta": fields.get('hafta', {}).get('stringValue', ''), "sinav_turu": fields.get('sinav_turu', {}).get('stringValue', ''), "aciklama": fields.get('aciklama', {}).get('stringValue', '')})
        quizler.reverse()
        res_s = requests.get(FIREBASE_QUESTION_URL)
        if res_s.status_code == 200:
            for doc in res_s.json().get('documents', []):
                fields = doc.get('fields', {})
                sorular.append({"quiz_id": fields.get('quiz_id', {}).get('stringValue', ''), "soru_metni": fields.get('soru_metni', {}).get('stringValue', ''), "a": fields.get('a', {}).get('stringValue', ''), "b": fields.get('b', {}).get('stringValue', ''), "c": fields.get('c', {}).get('stringValue', ''), "d": fields.get('d', {}).get('stringValue', ''), "dogru": fields.get('dogru', {}).get('stringValue', ''), "cozum": fields.get('cozum', {}).get('stringValue', '')})
    except Exception:
        pass
    return render_template('quiz.html', quizler=quizler, sorular=sorular)

# --- YENİ EKLENEN: KAYNAKLARI ÇEKME ROTASI ---
@app.route('/kaynaklar')
def kaynaklar():
    try:
        cevap = requests.get(FIREBASE_RESOURCE_URL)
        kaynak_listesi = []
        if cevap.status_code == 200:
            for doc in cevap.json().get('documents', []):
                alanlar = doc.get('fields', {})
                kaynak_listesi.append({
                    "baslik": alanlar.get('baslik', {}).get('stringValue', ''),
                    "aciklama": alanlar.get('aciklama', {}).get('stringValue', ''),
                    "tur": alanlar.get('tur', {}).get('stringValue', ''),
                    "url": alanlar.get('url', {}).get('stringValue', '')
                })
        kaynak_listesi.reverse()
        return render_template('kaynaklar.html', kaynaklar=kaynak_listesi)
    except Exception:
        return render_template('kaynaklar.html', kaynaklar=[])

# --- VERİTABANI KAYIT ROTALARI ---
@app.route('/add-event', methods=['POST'])
def add_event():
    payload = {"fields": {"baslik": {"stringValue": request.form.get('baslik')}, "aciklama": {"stringValue": request.form.get('aciklama', '')}, "tarih": {"stringValue": request.form.get('tarih')}, "tur": {"stringValue": request.form.get('tur')}}}
    requests.post(FIREBASE_EVENT_URL, json=payload)
    return redirect(url_for('takvim'))

@app.route('/add-task', methods=['POST'])
def add_task():
    payload = {"fields": {"sinav_turu": {"stringValue": request.form.get('sinav_turu')}, "ders": {"stringValue": request.form.get('ders')}, "baslik": {"stringValue": request.form.get('baslik')}, "aciklama": {"stringValue": request.form.get('aciklama', '')}, "son_tarih": {"stringValue": request.form.get('son_tarih')}, "oncelik": {"stringValue": request.form.get('oncelik')}}}
    requests.post(FIREBASE_TASK_URL, json=payload)
    return redirect(url_for('gorev'))

@app.route('/add-quiz', methods=['POST'])
def add_quiz():
    payload = {"fields": {"baslik": {"stringValue": request.form.get('baslik')}, "hafta": {"stringValue": request.form.get('hafta')}, "sinav_turu": {"stringValue": request.form.get('sinav_turu')}, "aciklama": {"stringValue": request.form.get('aciklama', '')}}}
    requests.post(FIREBASE_QUIZ_URL, json=payload)
    return redirect(url_for('quiz'))

@app.route('/add-question', methods=['POST'])
def add_question():
    payload = {"fields": {"quiz_id": {"stringValue": request.form.get('quiz_id')}, "soru_metni": {"stringValue": request.form.get('soru_metni')}, "a": {"stringValue": request.form.get('a')}, "b": {"stringValue": request.form.get('b')}, "c": {"stringValue": request.form.get('c')}, "d": {"stringValue": request.form.get('d')}, "dogru": {"stringValue": request.form.get('dogru')}, "cozum": {"stringValue": request.form.get('cozum', '')}}}
    requests.post(FIREBASE_QUESTION_URL, json=payload)
    return redirect(url_for('quiz'))

# --- YENİ EKLENEN: KAYNAK EKLEME ROTASI ---
@app.route('/add-resource', methods=['POST'])
def add_resource():
    payload = {
        "fields": {
            "baslik": {"stringValue": request.form.get('baslik')},
            "aciklama": {"stringValue": request.form.get('aciklama', '')},
            "tur": {"stringValue": request.form.get('tur')},
            "url": {"stringValue": request.form.get('url')}
        }
    }
    requests.post(FIREBASE_RESOURCE_URL, json=payload)
    return redirect(url_for('kaynaklar'))

if __name__ == '__main__':
    app.run(debug=True)
