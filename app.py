from flask import Flask, render_template, request, redirect, url_for, session
import requests

app = Flask(__name__)
app.secret_key = "eda_akademi_super_gizli_anahtar"

# Firebase Bağlantıları
BASE_URL = "https://firestore.googleapis.com/v1/projects/edaakedemi-a9543/databases/(default)/documents"
FIREBASE_USER_URL = f"{BASE_URL}/kullanicilar"
FIREBASE_EVENT_URL = f"{BASE_URL}/etkinlikler"
FIREBASE_TASK_URL = f"{BASE_URL}/gorevler"
FIREBASE_QUIZ_URL = f"{BASE_URL}/quizler"
FIREBASE_QUESTION_URL = f"{BASE_URL}/sorular"
FIREBASE_RESOURCE_URL = f"{BASE_URL}/kaynaklar"

@app.route('/')
def index(): return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    try:
        cevap = requests.get(FIREBASE_USER_URL)
        for doc in cevap.json().get('documents', []):
            f = doc.get('fields', {})
            if f.get('kullanici_adi', {}).get('stringValue') == request.form.get('username') and f.get('sifre', {}).get('stringValue') == request.form.get('password'):
                session.update({'kullanici_adi': f.get('kullanici_adi', {}).get('stringValue'), 'rol': f.get('rol', {}).get('stringValue'), 'isim': f.get('isim', {}).get('stringValue', 'Öğrenci')})
                return redirect(url_for('ogretmen_paneli' if session['rol'] == 'ogretmen' else 'ogrenci_dashboard'))
        return "Hatalı Giriş"
    except: return "Sistem Hatası"

@app.route('/logout')
def logout(): session.clear(); return redirect(url_for('index'))

# ÖĞRETMEN ROTALARI
@app.route('/ogretmen')
def ogretmen_paneli(): return render_template('ogretmen.html')
@app.route('/ogrenciler')
def ogrenciler():
    cevap = requests.get(FIREBASE_USER_URL)
    ogrenciler = [{"isim": d.get('fields', {}).get('isim', {}).get('stringValue', 'Öğrenci'), "kullanici_adi": d.get('fields', {}).get('kullanici_adi', {}).get('stringValue', ''), "puan": int(d.get('fields', {}).get('puan', {}).get('integerValue', '0'))} for d in cevap.json().get('documents', []) if d.get('fields', {}).get('rol', {}).get('stringValue') == 'ogrenci']
    return render_template('ogrenciler.html', ogrenciler=sorted(ogrenciler, key=lambda x: x['puan'], reverse=True))

@app.route('/quiz')
def quiz():
    res_q = requests.get(FIREBASE_QUIZ_URL)
    quizler = [{"id": d.get('name', '').split('/')[-1], "baslik": d.get('fields', {}).get('baslik', {}).get('stringValue', '')} for d in res_q.json().get('documents', [])]
    return render_template('quiz.html', quizler=quizler)

@app.route('/quiz_sonuclari/<quiz_id>')
def quiz_sonuclari(quiz_id):
    res = requests.get(FIREBASE_USER_URL)
    ogrenciler = [{"isim": d.get('fields', {}).get('isim', {}).get('stringValue', 'Öğrenci'), "puan": int(d.get('fields', {}).get('puan', {}).get('integerValue', '0'))} for d in res.json().get('documents', []) if d.get('fields', {}).get('rol', {}).get('stringValue') == 'ogrenci']
    return render_template('quiz_sonuclari.html', ogrenciler=ogrenciler, quiz_id=quiz_id)

# ÖĞRENCİ ROTALARI
@app.route('/ogrenci')
def ogrenci_dashboard(): return render_template('ogrenci_dashboard.html')
@app.route('/ogrenci_testler')
def ogrenci_testler():
    res_q = requests.get(FIREBASE_QUIZ_URL)
    quizler = [{"id": d.get('name', '').split('/')[-1], "baslik": d.get('fields', {}).get('baslik', {}).get('stringValue', ''), "aciklama": d.get('fields', {}).get('aciklama', {}).get('stringValue', '')} for d in res_q.json().get('documents', [])]
    res_s = requests.get(FIREBASE_QUESTION_URL)
    sorular = [{"quiz_id": d.get('fields', {}).get('quiz_id', {}).get('stringValue', ''), "soru_metni": d.get('fields', {}).get('soru_metni', {}).get('stringValue', ''), "a": d.get('fields', {}).get('a', {}).get('stringValue', ''), "b": d.get('fields', {}).get('b', {}).get('stringValue', ''), "c": d.get('fields', {}).get('c', {}).get('stringValue', ''), "d": d.get('fields', {}).get('d', {}).get('stringValue', ''), "dogru": d.get('fields', {}).get('dogru', {}).get('stringValue', ''), "cozum": d.get('fields', {}).get('cozum', {}).get('stringValue', '')} for d in res_s.json().get('documents', [])]
    return render_template('ogrenci_testler.html', quizler=quizler, sorular=sorular)

@app.route('/puan_ekle', methods=['POST'])
def puan_ekle():
    kullanici_adi = session.get('kullanici_adi')
    kazanilan = int(request.json.get('puan', 0))
    res = requests.get(FIREBASE_USER_URL)
    for doc in res.json().get('documents', []):
        f = doc.get('fields', {})
        if f.get('kullanici_adi', {}).get('stringValue') == kullanici_adi:
            doc_id = doc.get('name', '').split('/')[-1]
            yeni_puan = int(f.get('puan', {}).get('integerValue', '0')) + kazanilan
            requests.patch(f"{FIREBASE_USER_URL}/{doc_id}?updateMask.fieldPaths=puan", json={"fields": {"puan": {"integerValue": str(yeni_puan)}}})
            return {"status": "success"}
    return {"status": "error"}

if __name__ == '__main__': app.run(debug=True)
