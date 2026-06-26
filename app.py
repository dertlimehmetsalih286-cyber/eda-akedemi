@app.route('/login', methods=['POST'])
def login():
    kullanici = request.form.get('username')
    sifre = request.form.get('password')

    try:
        # Firebase deposundaki 'kullanicilar' koleksiyonunda sadece isim ve şifreyi ara
        kullanicilar_ref = db.collection('kullanicilar')
        sorgu = kullanicilar_ref.where('kullanici_adi', '==', kullanici).where('sifre', '==', sifre).stream()
        
        giris_basarili = False
        bulunan_rol = ""
        
        for doc in sorgu:
            giris_basarili = True
            kisi_bilgileri = doc.to_dict()
            bulunan_rol = kisi_bilgileri.get('rol', '') # Rolü veritabanından öğreniyoruz
            break 
            
        if giris_basarili:
            # Sistem kişinin rolünü kendi buldu, şimdi doğru yere yönlendiriyor
            if bulunan_rol == 'ogretmen':
                return redirect(url_for('ogretmen_paneli'))
            else:
                return "<h1>Öğrenci Paneli henüz yapım aşamasında...</h1>"
        else:
            return "<h1>Hata: Kullanıcı adı veya şifre yanlış! Lütfen tekrar deneyin.</h1>"
            
    except Exception as e:
        return f"Sistem Hatası: {e}"
