from flask import Flask, render_template, request, redirect, url_for, session
import requests

app = Flask(__name__)
app.secret_key = "eda_akademi_super_gizli_anahtar"

# Firebase Bağlantı Adresleri
BASE_URL = "https://firestore.googleapis.com/v1/projects/edaakedemi-a9543/databases/(default)/documents"

@app.route('/')
def index(): return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    k = request.form.get('username')
    s = request.form.get('password')
    try:
        cevap = requests.get(f"{BASE_URL}/kullanicilar")
        for doc in cevap.json().get('documents', []):
            f = doc.get('fields', {})
            if f.get('kullanici_adi', {}).get('stringValue') == k and f.get('sifre', {}).get('stringValue') == s:
                session.update({'kullanici_adi': k, 'rol': f.get('rol', {}).get('stringValue'), 'isim': f.get('isim', {}).get('stringValue', 'Öğrenci')})
                return redirect(url_for('ogretmen_paneli') if session['rol'] == 'ogretmen' else url_for('ogrenci_dashboard'))
        return "Hatalı Giriş"
    except: return "Sunucu Hatası"

@app.route('/logout')
def logout(): session.clear(); return redirect(url_for('index'))

# --- ÖĞRETMEN ROTALARI ---
@app.route('/ogretmen')
def ogretmen_paneli(): return render_template('ogretmen.html')

@app.route('/quiz')
def quiz():
    if session.get('rol') != 'ogretmen': return redirect(url_for('index'))
    quizler = []
    try:
        res = requests.get(f"{BASE_URL}/quizler")
        if res.status_code == 200:
            for d in res.json().get('documents', []):
                quizler.append({"id": d.get('name', '').split('/')[-1], "baslik": d.get('fields', {}).get('baslik', {}).get('stringValue', 'İsimsiz')})
    except: pass
    return render_template('quiz.html', quizler=quizler)

# GÜNCELLENEN KISIM: Cevap Anahtarını ve Öğrencileri Çekiyor
@app.route('/quiz_sonuclari/<quiz_id>')
def quiz_sonuclari(quiz_id):
    if session.get('rol') != 'ogretmen': return redirect(url_for('index'))
    
    quiz_baslik = "Quiz Detayı"
    sorular = []
    ogrenciler = []
    
    try:
        # Quiz Başlığını Bul
        res_q = requests.get(f"{BASE_URL}/quizler")
        for d in res_q.json().get('documents', []):
            if d.get('name', '').split('/')[-1] == quiz_id:
                quiz_baslik = d.get('fields', {}).get('baslik', {}).get('stringValue', 'İsimsiz Quiz')
        
        # Soruları Çek (Cevap Anahtarı için)
        res_s = requests.get(f"{BASE_URL}/sorular")
        for d in res_s.json().get('documents', []):
            f = d.get('fields', {})
            if f.get('quiz_id', {}).get('stringValue', '') == quiz_id:
                sorular.append({
                    "soru_metni": f.get('soru_metni', {}).get('stringValue', ''),
                    "dogru": f.get('dogru', {}).get('stringValue', ''),
                    "cozum": f.get('cozum', {}).get('stringValue', '')
                })
        
        # Öğrencileri Çek
        res_u = requests.get(f"{BASE_URL}/kullanicilar")
        for doc in res_u.json().get('documents', []):
            f = doc.get('fields', {})
            if f.get('rol', {}).get('stringValue') == 'ogrenci':
                ogrenciler.append({
                    "isim": f.get('isim', {}).get('stringValue', 'Öğrenci'),
                    "puan": int(f.get('puan', {}).get('integerValue', f.get('puan', {}).get('stringValue', '0')))
                })
        ogrenciler = sorted(ogrenciler, key=lambda x: x['puan'], reverse=True)
    except: pass
    
    return render_template('quiz_sonuclari.html', quiz_id=quiz_id, quiz_baslik=quiz_baslik, sorular=sorular, ogrenciler=ogrenciler)

@app.route('/ogrenciler')
def ogrenciler(): return render_template('ogrenciler.html')
@app.route('/takvim')
def takvim(): return render_template('takvim.html')
@app.route('/gorev')
def gorev(): return render_template('gorev.html')
@app.route('/kaynaklar')
def kaynaklar(): return render_template('kaynaklar.html')
@app.route('/ogretmen_analiz')
def ogretmen_analiz(): return render_template('ogretmen_analiz.html')

# --- ÖĞRENCİ ROTALARI ---
@app.route('/ogrenci')
def ogrenci_dashboard(): return render_template('ogrenci_dashboard.html')
@app.route('/ogrenci_testler')
def ogrenci_testler(): return render_template('ogrenci_testler.html')
@app.route('/puan_ekle', methods=['POST'])
def puan_ekle(): return {"status": "success"}

if __name__ == '__main__':
    app.run(debug=True)
