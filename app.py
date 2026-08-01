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


# =========================================================================
# ÖĞRETMEN PANELİ ROTALARI
# =========================================================================

@app.route('/ogretmen')
def ogretmen_paneli():
    if session.get('rol') != 'ogretmen': return redirect(url_for('index'))
    toplam_gorev, aktif_puan, tamamlanma_orani = 0, 0, 0
    try:
        res_task = requests.get(FIREBASE_TASK_URL)
        if res_task.status_code == 200: toplam_gorev = len(res_task.json().get('documents', []))
        
        res_user = requests.get(FIREBASE_USER_URL)
        if res_user.status_code == 200:
            ogrenci_sayisi = 0
            for doc in res_user.json().get('documents', []):
                fields = doc.get('fields', {})
                if fields.get('rol', {}).get('stringValue') == 'ogrenci':
                    ogrenci_sayisi += 1
                    p_val = fields.get('puan', {})
                    aktif_puan += int(p_val.get('integerValue', p_val.get('stringValue', '0')))
            
            if toplam_gorev > 0 and ogrenci_sayisi > 0:
                beklenen_puan = toplam_gorev * 10 * ogrenci_sayisi
                tamamlanma_orani = int((aktif_puan / beklenen_puan) * 100) if beklenen_puan > 0 else 0
                if tamamlanma_orani > 100: tamamlanma_orani = 100
    except: pass
    return render_template('ogretmen.html', toplam_gorev=toplam_gorev, aktif_puan=aktif_puan, tamamlanma_orani=tamamlanma_orani)

@app.route('/ogrenciler')
def ogrenciler():
    if session.get('rol') != 'ogretmen': return redirect(url_for('index'))
    try:
        cevap = requests.get(FIREBASE_USER_URL)
        ogrenci_listesi = []
        if cevap.status_code == 200:
            for doc in cevap.json().get('documents', []):
                alanlar = doc.get('fields', {})
                if alanlar.get('rol', {}).get('stringValue') == 'ogrenci':
                    puan_val = alanlar.get('puan', {})
                    puan = int(puan_val.get('integerValue', puan_val.get('stringValue', '0')))
                    tamamlanan = puan // 10 
                    ogrenci_listesi.append({"isim": alanlar.get('isim', {}).get('stringValue', 'Öğrenci'), "kullanici_adi": alanlar.get('kullanici_adi', {}).get('stringValue', ''), "puan": puan, "tamamlanan": tamamlanan})
        
        ogrenci_listesi = sorted(ogrenci_listesi, key=lambda x: x['puan'], reverse=True)
        toplam_ogrenci = len(ogrenci_listesi)
        en_yuksek_puan = ogrenci_listesi[0]['puan'] if toplam_ogrenci > 0 else 0
        toplam_tamamlanan = sum(o['tamamlanan'] for o in ogrenci_listesi)
        return render_template('ogrenciler.html', ogrenciler=ogrenci_listesi, toplam_ogrenci=toplam_ogrenci, en_yuksek_puan=en_yuksek_puan, toplam_tamamlanan=toplam_tamamlanan)
    except: return render_template('ogrenciler.html', ogrenciler=[], toplam_ogrenci=0, en_yuksek_puan=0, toplam_tamamlanan=0)

# YENİ: YAPAY ZEKA DESTEKLİ ANALİZ ROTASI
@app.route('/ogretmen_analiz')
def ogretmen_analiz():
    if session.get('rol') != 'ogretmen': return redirect(url_for('index'))
    try:
        cevap = requests.get(FIREBASE_USER_URL)
        ogrenciler = []
        toplam_puan = 0
        if cevap.status_code == 200:
            for doc in cevap.json().get('documents', []):
                alanlar = doc.get('fields', {})
                if alanlar.get('rol', {}).get('stringValue') == 'ogrenci':
                    p_val = alanlar.get('puan', {})
                    puan = int(p_val.get('integerValue', p_val.get('stringValue', '0')))
                    toplam_puan += puan
                    ogrenciler.append({"isim": alanlar.get('isim', {}).get('stringValue', 'Öğrenci'), "puan": puan})
        
        ogrenci_sayisi = len(ogrenciler)
        ortalama = (toplam_puan / ogrenci_sayisi) if ogrenci_sayisi > 0 else 0
        sirali = sorted(ogrenciler, key=lambda x: x['puan'], reverse=True)
        
        en_iyi = sirali[0]['isim'] if ogrenci_sayisi > 0 else "Yok"
        en_dusuk = sirali[-1]['isim'] if ogrenci_sayisi > 0 else "Yok"
        
        # Akıllı İçgörü Üretme Algoritması
        tavsiyeler = []
        if ortalama < 30:
            tavsiyeler.append("Sınıfın genel başarı ortalaması zayıf görünüyor. Konu anlatımlarını pekiştirmek amacıyla <b>Kaynaklar</b> bölümüne yeni dökümanlar yüklemeniz ve kolay seviye görevler vermeniz önerilir.")
        elif ortalama < 60:
            tavsiyeler.append("Sınıf performansı dengeli ve orta düzeyde ilerliyor. Öğrencilerin eksik konularını kapatmak için <b>Quiz Yönetimi</b> kısmından yeni tarama testleri oluşturabilirsiniz.")
        else:
            tavsiyeler.append("Harika! Sınıf ortalaması mükemmel durumda. Öğrencilerin rekabet duygusunu ve ilgisini canlı tutmak için yeni nesil zor seviye YKS/LGS görevleri ekleyebilirsiniz.")
        
        if ogrenci_sayisi > 0:
            tavsiyeler.append(f"🔥 Haftanın en yüksek performans gösteren parlayan yıldızı: <b>{en_iyi}</b>. Sınıf önünde tebrik edilerek motivasyonu artırılabilir.")
            tavsiyeler.append(f"⚠️ Yakın takip gerektiren öğrenci: <b>{en_dusuk}</b>. Bu öğrencinin çözemediği akıllı testleri ve boş bıraktığı ödevleri inceleyerek özel rehberlik yapılması tavsiye edilir.")
            
        return render_template('ogretmen_analiz.html', tavsiyeler=tavsiyeler, ortalama=int(ortalama), en_iyi=en_iyi, en_dusuk=en_dusuk, toplam_ogrenci=ogrenci_sayisi)
    except:
        return render_template('ogretmen_analiz.html', tavsiyeler=["Veritabanı hatası nedeniyle analiz yapılamadı."], ortalama=0, en_iyi="Yok", en_dusuk="Yok", toplam_ogrenci=0)

@app.route('/takvim')
def takvim():
    if session.get('rol') != 'ogretmen': return redirect(url_for('index'))
    gorevler = []
    try:
        # Takvim sayfasında listelemek için görevleri çekiyoruz
        cevap = requests.get(FIREBASE_TASK_URL)
        if cevap.status_code == 200:
            for d in cevap.json().get('documents', []):
                f = d.get('fields', {})
                gorevler.append({
                    "sinav_turu": f.get('sinav_turu', {}).get('stringValue', ''),
                    "ders": f.get('ders', {}).get('stringValue', ''),
                    "baslik": f.get('baslik', {}).get('stringValue', ''),
                    "son_tarih": f.get('son_tarih', {}).get('stringValue', ''),
                    "oncelik": f.get('oncelik', {}).get('stringValue', '')
                })
        gorevler.reverse()
    except: pass
    
    return render_template('takvim.html', gorevler=gorevler)

# =========================================================================
# QUİZ YÖNETİMİ VE SONUÇLAR
# =========================================================================

@app.route('/quiz')
def quiz():
    if session.get('rol') != 'ogretmen': return redirect(url_for('index'))
    
    quizler = []
    sorular = []
    
    try:
        # Quizleri Çek
        res_q = requests.get(FIREBASE_QUIZ_URL)
        if res_q.status_code == 200:
            for d in res_q.json().get('documents', []):
                quizler.append({
                    "id": d.get('name', '').split('/')[-1], 
                    "baslik": d.get('fields', {}).get('baslik', {}).get('stringValue', 'İsimsiz Quiz')
                })
        
        # Soruları Çek
        res_s = requests.get(FIREBASE_QUESTION_URL)
        if res_s.status_code == 200:
            for d in res_s.json().get('documents', []):
                f = d.get('fields', {})
                sorular.append({
                    "quiz_id": f.get('quiz_id', {}).get('stringValue', ''),
                    "soru_metni": f.get('soru_metni', {}).get('stringValue', 'Soru metni yok')
                })
    except: pass
    
    return render_template('quiz.html', quizler=quizler, sorular=sorular)

@app.route('/quiz_sonuclari/<quiz_id>')
def quiz_sonuclari(quiz_id):
    if session.get('rol') != 'ogretmen': 
        return redirect(url_for('index'))
    
    quiz_baslik = "Quiz Detayı"
    sorular = []
    ogrenciler = []
    
    try:
        # Quiz Başlığını Bul
        res_q = requests.get(FIREBASE_QUIZ_URL)
        if res_q.status_code == 200:
            for d in res_q.json().get('documents', []):
                if d.get('name', '').split('/')[-1] == quiz_id:
                    quiz_baslik = d.get('fields', {}).get('baslik', {}).get('stringValue', 'İsimsiz Quiz')
        
        # Soruları Çek (Cevap Anahtarı için)
        res_s = requests.get(FIREBASE_QUESTION_URL)
        if res_s.status_code == 200:
            for d in res_s.json().get('documents', []):
                f = d.get('fields', {})
                if f.get('quiz_id', {}).get('stringValue', '') == quiz_id:
                    sorular.append({
                        "soru_metni": f.get('soru_metni', {}).get('stringValue', ''),
                        "dogru": f.get('dogru', {}).get('stringValue', ''),
                        "cozum": f.get('cozum', {}).get('stringValue', '')
                    })
        
        # Öğrencileri Çek
        res_u = requests.get(FIREBASE_USER_URL)
        if res_u.status_code == 200:
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

@app.route('/kaynaklar')
def kaynaklar():
    try:
        cevap = requests.get(FIREBASE_RESOURCE_URL)
        k_list = [{"baslik": d.get('fields', {}).get('baslik', {}).get('stringValue', ''), "aciklama": d.get('fields', {}).get('aciklama', {}).get('stringValue', ''), "tur": d.get('fields', {}).get('tur', {}).get('stringValue', ''), "url": d.get('fields', {}).get('url', {}).get('stringValue', '')} for d in cevap.json().get('documents', [])] if cevap.status_code == 200 else []
        k_list.reverse()
        return render_template('kaynaklar.html', kaynaklar=k_list)
    except: return render_template('kaynaklar.html', kaynaklar=[])

# --- ÖĞRETMEN VERİ EKLEME POST İŞLEMLERİ ---
@app.route('/add-task', methods=['POST'])
def add_task(): 
    requests.post(FIREBASE_TASK_URL, json={
        "fields": {
            "sinav_turu": {"stringValue": request.form.get('sinav_turu')}, 
            "ders": {"stringValue": request.form.get('ders')}, 
            "baslik": {"stringValue": request.form.get('baslik')}, 
            "aciklama": {"stringValue": request.form.get('aciklama', '')}, 
            "son_tarih": {"stringValue": request.form.get('son_tarih')}, 
            "oncelik": {"stringValue": request.form.get('oncelik')}
        }
    })
    # YÖNLENDİRME BURADA TAKVİME ÇEVRİLDİ:
    return redirect(url_for('takvim'))
@app.route('/add-task', methods=['POST'])
def add_task(): requests.post(FIREBASE_TASK_URL, json={"fields": {"sinav_turu": {"stringValue": request.form.get('sinav_turu')}, "ders": {"stringValue": request.form.get('ders')}, "baslik": {"stringValue": request.form.get('baslik')}, "aciklama": {"stringValue": request.form.get('aciklama', '')}, "son_tarih": {"stringValue": request.form.get('son_tarih')}, "oncelik": {"stringValue": request.form.get('oncelik')}}}); return redirect(url_for('gorev'))
@app.route('/add-quiz', methods=['POST'])
def add_quiz(): requests.post(FIREBASE_QUIZ_URL, json={"fields": {"baslik": {"stringValue": request.form.get('baslik')}, "hafta": {"stringValue": request.form.get('hafta')}, "sinav_turu": {"stringValue": request.form.get('sinav_turu')}, "aciklama": {"stringValue": request.form.get('aciklama', '')}}}); return redirect(url_for('quiz'))
@app.route('/add-question', methods=['POST'])
def add_question(): requests.post(FIREBASE_QUESTION_URL, json={"fields": {"quiz_id": {"stringValue": request.form.get('quiz_id')}, "soru_metni": {"stringValue": request.form.get('soru_metni')}, "a": {"stringValue": request.form.get('a')}, "b": {"stringValue": request.form.get('b')}, "c": {"stringValue": request.form.get('c')}, "d": {"stringValue": request.form.get('d')}, "dogru": {"stringValue": request.form.get('dogru')}, "cozum": {"stringValue": request.form.get('cozum', '')}}}); return redirect(url_for('quiz'))
@app.route('/add-resource', methods=['POST'])
def add_resource(): requests.post(FIREBASE_RESOURCE_URL, json={"fields": {"baslik": {"stringValue": request.form.get('baslik')}, "aciklama": {"stringValue": request.form.get('aciklama', '')}, "tur": {"stringValue": request.form.get('tur')}, "url": {"stringValue": request.form.get('url')}}}); return redirect(url_for('kaynaklar'))


# =========================================================================
# ÖĞRENCİ PANELİ ROTALARI
# =========================================================================

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
        gorevler.reverse();
        return render_template('ogrenci_gorevler.html', gorevler=gorevler)
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
        k_list.reverse();
        return render_template('ogrenci_kaynaklar.html', kaynaklar=k_list)
    except: return render_template('ogrenci_kaynaklar.html', kaynaklar=[])
@app.route('/ogrenci_siralama')
def ogrenci_siralama():
    try:
        cevap = requests.get(FIREBASE_USER_URL)
        ogrenciler = [{"isim": d.get('fields', {}).get('isim', {}).get('stringValue', 'Öğrenci'), "puan": int(d.get('fields', {}).get('puan', {}).get('integerValue', d.get('fields', {}).get('puan', {}).get('stringValue', '0')))} for d in cevap.json().get('documents', []) if d.get('fields', {}).get('rol', {}).get('stringValue') == 'ogrenci'] if cevap.status_code == 200 else []
        return render_template('ogrenci_siralama.html', ogrenciler=sorted(ogrenciler, key=lambda x: x['puan'], reverse=True))
    except: return render_template('ogrenci_siralama.html', ogrenciler=[])

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
                    doc_id = doc.get('name', '').split('/')[-1]
                    puan_val = fields.get('puan', {})
                    mevcut_puan = int(puan_val.get('integerValue', puan_val.get('stringValue', '0')))
                    yeni_puan = mevcut_puan + kazanilan_puan
                    requests.patch(f"{FIREBASE_USER_URL}/{doc_id}?updateMask.fieldPaths=puan", json={"fields": {"puan": {"integerValue": str(yeni_puan)}}})
                    return {"status": "success", "yeni_puan": yeni_puan}
    except: pass
    return {"status": "error"}

if __name__ == '__main__':
    app.run(debug=True)
