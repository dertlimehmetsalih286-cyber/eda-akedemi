from flask import Flask, render_template, request, redirect, url_for
import requests

app = Flask(__name__)

# --- HAFİF VE HIZLI FIREBASE BAĞLANTISI (REST API) ---
# Ağır kütüphaneler yok, şifreler yok. Veriyi direkt senin projene ait bu linkten saniyesinde çekeceğiz.
FIREBASE_URL = "https://firestore.googleapis.com/v1/projects/edaakedemi-a9543/databases/(default)/documents/kullanicilar"

@app.route('/')
def index():
    # O sadeleştirdiğimiz temiz giriş ekranını gösterir
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    kullanici = request.form.get('username')
    sifre = request.form.get('password')

    try:
        # Firebase'e gidip kullanıcı listesini alıyoruz
        cevap = requests.get(FIREBASE_URL)
        
        if cevap.status_code != 200:
            return "<h1>Hata: Veritabanına ulaşılamadı.</h1>"
            
        veriler = cevap.json().get('documents', [])
        
        giris_basarili = False
        bulunan_rol = ""
        
        for doc in veriler:
            alanlar = doc.get('fields', {})
            
            # Veritabanındaki kutuları okuyoruz
            db_kullanici = alanlar.get('kullanici_adi', {}).get('stringValue', '')
            db_sifre = alanlar.get('sifre', {}).get('stringValue', '')
            db_rol = alanlar.get('rol', {}).get('stringValue', '')
            
            # Formdaki bilgilerle eşleşiyor mu kontrol ediyoruz
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

if __name__ == '__main__':
    app.run(debug=True)
