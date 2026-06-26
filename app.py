from flask import Flask, render_template, request, redirect, url_for
import firebase_admin
from firebase_admin import credentials, firestore
# FIREBASE'İN İSTEDİĞİ YENİ GÜVENLİK FİLTRESİNİ İÇERİ AKTARIYORUZ
from google.cloud.firestore_v1.base_query import FieldFilter

app = Flask(__name__)

# --- FIREBASE DEPOSU BAĞLANTISI ---
firebase_sifre = {
  "type": "service_account",
  "project_id": "edaakedemi-a9543",
  "private_key_id": "a8bd4e586fd4359c5c6d88ffc65ffcb0ebea0d4b",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC4HsyHJXUs6mMu\nB8pa5GNEH/EA0yCqHCW+QosPF6C7/TiidIBEOAE5kTk6j2mr1fyviaongVT2X6Ra\ntrMOWH8T0ud+9fPIlELAkf//8KbqQT+Br12YdFDnMUE1lYFlVRt6cRhDu2996YgO\nSlaI3Sz8yCSr1k0z6ztkJm1kHHtitxoiqwuCoFypsJd9RCwALWcxmZrv3jtR+3Ct\n7kzJIfqe6MJA63mUXOxxzvsVmFut5jeUei4wFT2eTK2m79CRWzimi9QLb7A2shTR\nW4GU9ogfvCj6E3zCjBs+1MqMJL6OaZ15Vw/jeLd9M3f0EgEz/PCiS0v574ppS/Be\njPH47zFPAgMBAAECggEAGUGRoROTJGNN0eFxXBDKdGyvP1jhY67zFyCt+Owu+RU4\nq2wwsMA/8W4e0WNycDGtH5p83pNqnKss8ovvjuRhIM6EQScALFT4vSKp4P6utCEu\n0sgZSNGNIXw2VjaDu+s17DtO7pzro8l2Mi5MpX81bcK56Qpp/QO5BLloCwdZ04X6\nfc1o4OeTyP3dgv9yA5lN5OIJaOzVlVWwYVvcod7WAPt+231vFUNCG6RyiY7/wRW1\nbckPLaxRJdAPFrRXmQfPMSjzXkrbDlftk/B9CfNpZTG46vXZjuMokg1kAUlLWGto\nPAgGeqsXJBS4Ow2TIlAjQhMQSrorrU/3Kpl7FpEVRQKBgQDaLUx/5rUi/WaRFpwI\nPPiXop9VNUhcUz4cgM0QasJWnGTkxGMMbhMsLeQZHw/CYmQwmtLKcLGbBf38pP2T\ndod1gFo7wXk7KZ2y7uOEkepfJVDABPCXjO0HyuQyzaD8IrYoZ0qsU/gdTja7zsSt\nRn+3TGBtzJldmHOY1vWxybjjwwKBgQDYChCs9xe9AopglyAN63G1TW+Y4HxQJZaQ\n5rvGHh31S/c+JCgtlsLQRGoN2Z1TW9cepiCnUOU0Po/sty7QZ1i0KqffJppF9GBp\nk70MqpE8VG0RZDrt2GlI7QwV1Wa/XhxHsxOEasP6h38caaHqwxMy4mXM6+X/uTvh\n7JQ1Nv7fhQKBgQCVzfqz624+Sy3Mu3CBe5PZUjEC6aX4trN0EMA84ID1xUbFiU7V\nLxN9BzmSQjCo8LQIZ5YKqFxarD+b5JG0WfNiq7HJS+v4wndkcADKewIpOE78uaeU\n94+dBSOw+l3qIc9faKTuNG2teZG9XJjQvRJeglPHsG8xw8bDj/19iJupzwKBgFFX\n2NeHYeTE5B1iSat0DyhYs8A4JhZ3UK3WcrUx+c22gK1hJ8+iiE+qstPsMBSG7ASa\nQIk/KE33kHFst6+4eem8deDLxCK61OJrwi7WukCg+UAnIRkU9u+CcZ5272z2nmdQ\nwfSFzqyx/+ZOz6x5Lu1l2TbDS6JxuF5kmZk/z8+RAoGBALRthR2YYMzsieFoBqUP\ndWNURYQqTVNZFVr3Fc/sZ9caCNFMI0MZuoeSuLqm4y4yrqw6uT8BX7BR9kDKEpCW\nwANrjNliJVYSw3dHZQtXpZnZjm0abrLVrZztfJBltl1HsUO2KuyvtJ7W6Eoqlrai\nLgko4RvVq8RdI6wZLG3mNkH2\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-fbsvc@edaakedemi-a9543.iam.gserviceaccount.com",
  "client_id": "105035785708283503676",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40edaakedemi-a9543.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

try:
    if not firebase_admin._apps:
        cred = credentials.Certificate(firebase_sifre)
        firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("BAŞARILI: Firebase Deposuna Zırhlı Bağlantı Kuruldu!")
except Exception as e:
    print(f"Bağlantı Hatası: {e}")

# --- SAYFA ROTALARI ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    kullanici = request.form.get('username')
    sifre = request.form.get('password')

    try:
        kullanicilar_ref = db.collection('kullanicilar')
        # YENİ VE HATASIZ ARAMA YÖNTEMİ (FIELDFILTER İLE)
        sorgu = kullanicilar_ref.where(filter=FieldFilter('kullanici_adi', '==', kullanici)).where(filter=FieldFilter('sifre', '==', sifre)).stream()
        
        giris_basarili = False
        bulunan_rol = ""
        
        for doc in sorgu:
            giris_basarili = True
            kisi_bilgileri = doc.to_dict()
            bulunan_rol = kisi_bilgileri.get('rol', '')
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
