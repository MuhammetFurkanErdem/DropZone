"""
DropZone Upload Test
Dosya yükleme endpoint'ini test eder
"""

import requests
import os
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_upload_info():
    """Upload limitleri bilgisini al"""
    print("\n📊 Upload Limitleri:")
    response = requests.get(f"{BASE_URL}/upload/info")
    data = response.json()
    print(f"  Max Dosya Boyutu: {data['max_file_size_mb']:.1f} MB")
    print(f"  İzin Verilen Tipler: {', '.join(data['allowed_extensions'])}")
    return data

def create_test_file():
    """Test için basit bir text dosyası oluştur"""
    test_file = Path("test_file.txt")
    with open(test_file, "w", encoding="utf-8") as f:
        f.write("Bu bir test dosyasıdır.\nDropZone dosya yükleme testi için oluşturuldu.\n")
    return test_file

def test_file_upload():
    """Dosya yükleme testi"""
    print("\n📤 Dosya Yükleme Testi:")
    
    # Test dosyası oluştur
    test_file = create_test_file()
    
    try:
        # Dosyayı yükle
        with open(test_file, "rb") as f:
            files = {"file": (test_file.name, f, "text/plain")}
            data = {
                "room_id": "Test-Odasi",
                "username": "Test-User"
            }
            response = requests.post(f"{BASE_URL}/upload", files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"  ✅ Başarılı!")
            print(f"  📁 Dosya: {result['file_name']}")
            print(f"  📏 Boyut: {result['file_size']} bytes")
            print(f"  🔗 URL: {result['file_url']}")
            print(f"  📅 Tarih: {result['uploaded_at']}")
        else:
            print(f"  ❌ Hata: {response.status_code}")
            print(f"  Detay: {response.text}")
    
    finally:
        # Test dosyasını sil
        if test_file.exists():
            os.remove(test_file)
            print(f"  🗑️ Test dosyası temizlendi")

def test_health():
    """API health check"""
    print("\n🏥 Health Check:")
    response = requests.get(f"{BASE_URL}/")
    if response.status_code == 200:
        data = response.json()
        print(f"  ✅ {data['app']} v{data['version']}")
        print(f"  📊 Durum: {data['status']}")
        print(f"  💾 Database: {data['database']['type']} ({'Bağlı' if data['database']['connected'] else 'Bağlı Değil'})")
    else:
        print(f"  ❌ API erişilemiyor: {response.status_code}")

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 DropZone Upload Test Başlatılıyor...")
    print("=" * 60)
    
    try:
        test_health()
        test_upload_info()
        test_file_upload()
        
        print("\n" + "=" * 60)
        print("✅ Tüm testler tamamlandı!")
        print("=" * 60)
    
    except requests.exceptions.ConnectionError:
        print("\n❌ HATA: Sunucuya bağlanılamıyor!")
        print("Lütfen önce sunucuyu başlatın: python backend/main.py")
    except Exception as e:
        print(f"\n❌ HATA: {e}")
