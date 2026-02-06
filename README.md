# 🚀 DropZone - Gerçek Zamanlı Not Paylaşım Platformu

Üniversite öğrencileri için WebSocket tabanlı canlı sohbet ve dosya paylaşım uygulaması.

## 📋 Proje Durumu

**✅ FAZ 1: WebSocket Altyapısı (TAMAMLANDI)**
- ConnectionManager sınıfı
- Oda bazlı mesajlaşma
- Kullanıcı katılma/ayrılma bildirimleri

**⏳ FAZ 2: Dosya Yükleme Servisi (HAZIRLANACAK)**
**⏳ FAZ 3: Frontend Entegrasyonu (HAZIRLANACAK)**

## 🛠️ Teknoloji Yığını

### Backend
- Python 3.10+
- FastAPI
- WebSockets
- SQLAlchemy + SQLite

### Frontend (FAZ 3'te)
- React + TypeScript
- Vite
- Tailwind CSS

## 🚀 Kurulum ve Çalıştırma

### Backend (FAZ 1)

```bash
# 1. Backend klasörüne git
cd backend

# 2. Virtual environment oluştur (opsiyonel ama önerilir)
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 3. Bağımlılıkları yükle
pip install -r requirements.txt

# 4. Sunucuyu başlat
python main.py
```

Sunucu başladığında:
- 🌐 API: http://localhost:8000
- 📚 Swagger Docs: http://localhost:8000/docs
- 🔌 WebSocket: ws://localhost:8000/ws/{room_id}?username={username}

## 🧪 WebSocket Test Etme

### Tarayıcı Console ile Test:

```javascript
// WebSocket bağlantısı oluştur
const ws = new WebSocket("ws://localhost:8000/ws/Test-Odasi?username=Ahmet");

// Mesaj dinle
ws.onmessage = (event) => {
    console.log("Gelen mesaj:", JSON.parse(event.data));
};

// Mesaj gönder
ws.send(JSON.stringify({
    content: "Merhaba dünya!"
}));
```

### Postman/Insomnia ile Test:
1. Yeni WebSocket request oluştur
2. URL: `ws://localhost:8000/ws/Test-Odasi?username=Mehmet`
3. Connect'e tıkla
4. Mesaj gönder: `{"content": "Selam!"}`

## 📁 Proje Yapısı

```
DropZone/
├── backend/
│   ├── main.py              # FastAPI uygulaması
│   ├── manager.py           # WebSocket yöneticisi
│   ├── routers/
│   │   ├── chat.py          # Chat endpoint'leri
│   │   └── upload.py        # Dosya yükleme (FAZ 2)
│   ├── static/uploads/      # Yüklenen dosyalar
│   └── requirements.txt
└── frontend/                # React app (FAZ 3)
```

## 🎯 Özellikler

### Şu Anki Özellikler (FAZ 1):
- ✅ Oda bazlı mesajlaşma
- ✅ Gerçek zamanlı mesaj broadcast'i
- ✅ Kullanıcı katılma/ayrılma bildirimleri
- ✅ Aktif oda listesi API'si

### Gelecek Özellikler:
- ⏳ PDF/Resim yükleme (FAZ 2)
- ⏳ React + TypeScript frontend (FAZ 3)
- ⏳ Dosya önizleme
- ⏳ Kullanıcı authentication

## 📝 API Endpoint'leri

| Method | Endpoint | Açıklama |
|--------|----------|----------|
| GET | `/` | Health check |
| GET | `/rooms` | Aktif odalar listesi |
| WebSocket | `/ws/{room_id}` | Chat bağlantısı |

## 🧑‍💻 Geliştirici

Bu proje, Kampüs SuperApp'inin MVP prototipidir.

---
**Son Güncelleme:** FAZ 1 Tamamlandı - WebSocket Core
