from flask import Flask, render_template, request, redirect, url_for
import requests

app = Flask(__name__)

# Firebase REST API Linklerimiz
FIREBASE_USER_URL = "https://firestore.googleapis.com/v1/projects/edaakedemi-a9543/databases/(default)/documents/kullanicilar"
FIREBASE_EVENT_URL = "https://firestore.googleapis.com/v1/projects/edaakedemi-a9543/databases/(default)/documents/etkinlikler"
FIREBASE_TASK_URL = "https://firestore.googleapis.com/v1/projects/edaakedemi-a9543/databases/(default)/documents/gorevler"

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
            return "<h1>Hata: Kullanıcı adı veya şifre yanlış! Lütfen tekrar deneyin.</h1>"
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
            veriler = cevap.json().get('documents', [])
            for doc in veriler:
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

# --- YENİ EKLENEN: GÖREVLERİ OKUMA ---
@app.route('/gorev')
def gorev():
    try:
        cevap = requests.get(FIREBASE_TASK_URL)
        gorevler = []
        if cevap.status_code == 200:
            veriler = cevap.json().get('documents', [])
            for doc in veriler:
                alanlar = doc.get('fields', {})
                gorevler.append({
                    "sinav_turu": alanlar.get('sinav_turu', {}).get('stringValue', ''),
                    "ders": alanlar.get('ders', {}).get('stringValue', ''),
                    "baslik": alanlar.get('baslik', {}).get('stringValue', ''),
                    "aciklama": alanlar.get('aciklama', {}).get('stringValue', ''),
                    "son_tarih": alanlar.get('son_tarih', {}).get('stringValue', ''),
                    "oncelik": alanlar.get('oncelik', {}).get('stringValue', '')
                })
        # Görevleri eklenme sırasına göre ters çevir (en yeni en üstte)
        gorevler.reverse()
        return render_template('gorev.html', gorevler=gorevler)
    except Exception:
        return render_template('gorev.html', gorevler=[])

@app.route('/kaynaklar')
def kaynaklar():
    return render_template('kaynaklar.html')

@app.route('/quiz')
def quiz():
    return render_template('quiz.html')

@app.route('/add-event', methods=['POST'])
def add_event():
    payload = {
        "fields": {
            "baslik": {"stringValue": request.form.get('baslik')},
            "aciklama": {"stringValue": request.form.get('aciklama', '')},
            "tarih": {"stringValue": request.form.get('tarih')},
            "tur": {"stringValue": request.form.get('tur')}
        }
    }
    requests.post(FIREBASE_EVENT_URL, json=payload)
    return redirect(url_for('takvim'))

# --- YENİ EKLENEN: GÖREV KAYDETME ROTASI ---
@app.route('/add-task', methods=['POST'])
def add_task():
    payload = {
        "fields": {
            "sinav_turu": {"stringValue": request.form.get('sinav_turu')},
            "ders": {"stringValue": request.form.get('ders')},
            "baslik": {"stringValue": request.form.get('baslik')},
            "aciklama": {"stringValue": request.form.get('aciklama', '')},
            "son_tarih": {"stringValue": request.form.get('son_tarih')},
            "oncelik": {"stringValue": request.form.get('oncelik')}
        }
    }
    requests.post(FIREBASE_TASK_URL, json=payload)
    return redirect(url_for('gorev'))

if __name__ == '__main__':
    app.run(debug=True)
