from flask import Flask, render_template, request, redirect, url_for, session
import requests

app = Flask(__name__)
app.secret_key = "eda_akademi_super_gizli_anahtar"

# --- FİREBASE BAĞLANTILARI ---
FIREBASE_USER_URL = "https://firestore.googleapis.com/v1/projects/edaakedemi-a9543/databases/(default)/documents/kullanicilar"
FIREBASE_EVENT_URL = "https://firestore.googleapis.com/v1/projects/edaakedemi-a9543/databases/(default)/documents/etkinlikler"
FIREBASE_TASK_URL = "https://firestore.googleapis.com/v1/projects/edaakedemi-a9543/databases/(default)/documents/gorevler"
FIREBASE_QUIZ_URL = "https://firestore.googleapis.com/v1/projects/edaakedemi-a9543/databases/(default)/documents/quizler"
FIREBASE_QUESTION_URL = "https://firestore.googleapis.com/v1/projects/edaakedemi-a9543/databases/(default)/documents/sorular"
FIREBASE_RESOURCE_URL = "https://firestore.googleapis.com/v1/projects/edaakedemi-a9543/databases/(default)/documents/kaynaklar"

@app.route('/')
def index(): return render_template('index.html')

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
            if db_kullanici == kullanici and db_sifre == sifre:
                session['kullanici_adi'] = db_kullanici
                session['rol'] = alanlar.get('rol', {}).get('stringValue', '')
                session['isim'] = alanlar.get('isim', {}).get('stringValue', db_kullanici.capitalize())
                return redirect(url_for('ogretmen_paneli') if session['rol'] == 'ogretmen' else url_for('ogrenci_dashboard'))
        return "<h1>Hata: Kullanıcı adı veya şifre yanlış!</h1>"
    except Exception as e: return f"Sistem Hatası: {e}"

@app.route('/logout')
def logout(): session.clear(); return redirect(url_for('index'))

# --- ÖĞRETMEN ROTALARI ---
@app.route('/ogretmen')
def ogretmen_paneli(): return render_template('ogretmen.html')

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
    return render_template('quiz.html', quizler=quizler)

# HATA BURADAYDI: Bu rota artık dışarıda ve doğru hizada
@app.route('/quiz_sonuclari/<quiz_id>')
def quiz_sonuclari(quiz_id):
    if session.get('rol') != 'ogretmen': return redirect(url_for('index'))
    cevap = requests.get(FIREBASE_USER_URL)
    ogrenciler = []
    if cevap.status_code == 200:
        for doc in cevap.json().get('documents', []):
            alanlar = doc.get('fields', {})
            if alanlar.get('rol', {}).get('stringValue') == 'ogrenci':
                p_val = alanlar.get('puan', {})
                ogrenciler.append({
                    "isim": alanlar.get('isim', {}).get('stringValue', 'Öğrenci'),
                    "puan": int(p_val.get('integerValue', p_val.get('stringValue', '0')))
                })
    return render_template('quiz_sonuclari.html', ogrenciler=ogrenciler, quiz_id=quiz_id)

# --- DİĞER ROTALAR AYNI ŞEKİLDE KALABİLİR ---
@app.route('/ogrenciler')
def ogrenciler():
    # Buraya ogrenciler fonksiyonunu aynen yapıştır
    return render_template('ogrenciler.html') # Örnek dönüş

@app.route('/puan_ekle', methods=['POST'])
def puan_ekle():
    # Buraya puan_ekle fonksiyonunu aynen yapıştır
    return {"status": "success"}

if __name__ == '__main__':
    app.run(debug=True)
