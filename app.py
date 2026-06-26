from flask import Flask, render_template, request, redirect, url_for
import requests

app = Flask(__name__)

# Firebase REST API Linki (En hafif ve en hızlı bağlantı)
FIREBASE_URL = "https://firestore.googleapis.com/v1/projects/edaakedemi-a9543/databases/(default)/documents/kullanicilar"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    kullanici = request.form.get('username')
    sifre = request.form.get('password')

    try:
        cevap = requests.get(FIREBASE_URL)
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

# --- YENİ EKLENEN SAYFA ADRESLERİ ---
@app.route('/ogretmen')
def ogretmen_paneli():
    return render_template('ogretmen.html')

@app.route('/ogrenciler')
def ogrenciler():
    return render_template('ogrenciler.html')

@app.route('/kaynaklar')
def kaynaklar():
    return render_template('kaynaklar.html')

@app.route('/quiz')
def quiz():
    return render_template('quiz.html')

@app.route('/gorev')
def gorev():
    return render_template('gorev.html')

@app.route('/takvim')
def takvim():
    return render_template('takvim.html')
if __name__ == '__main__':
    app.run(debug=True)
