"""
WebSocket Connection Manager
Tüm aktif bağlantıları yöneten merkezi sınıf.
Her oda (room) için ayrı kullanıcı listesi tutar.
"""

from fastapi import WebSocket
from typing import Dict, List
import json


class ConnectionManager:
    """
    WebSocket bağlantılarını oda (room) bazlı yöneten sınıf.
    
    Yapısı:
    active_connections = {
        "room_id_1": [
            {"websocket": ws1, "username": "Ahmet"},
            {"websocket": ws2, "username": "Mehmet"}
        ],
        "room_id_2": [...]
    }
    """
    
    def __init__(self):
        # Oda ID'sine göre WebSocket bağlantılarını tutan dict
        self.active_connections: Dict[str, List[Dict]] = {}
    
    async def connect(self, websocket: WebSocket, room_id: str, username: str):
        """
        Yeni bir kullanıcıyı odaya bağlar.
        
        Args:
            websocket: FastAPI WebSocket nesnesi
            room_id: Oda ID'si (örn: "Bilgisayar-101")
            username: Kullanıcının adı
        """
        await websocket.accept()
        
        # Oda yoksa oluştur
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        
        # Kullanıcıyı odaya ekle
        self.active_connections[room_id].append({
            "websocket": websocket,
            "username": username
        })
        
        print(f"✅ {username} -> {room_id} odasına katıldı. Toplam: {len(self.active_connections[room_id])}")
    
    def disconnect(self, websocket: WebSocket, room_id: str):
        """
        Kullanıcıyı odadan çıkarır.
        
        Args:
            websocket: Çıkacak WebSocket bağlantısı
            room_id: Oda ID'si
            
        Returns:
            str: Çıkan kullanıcının adı (varsa)
        """
        if room_id not in self.active_connections:
            return None
        
        # Kullanıcıyı bul ve çıkar
        username = None
        for connection in self.active_connections[room_id]:
            if connection["websocket"] == websocket:
                username = connection["username"]
                self.active_connections[room_id].remove(connection)
                break
        
        # Oda boşaldıysa sil
        if not self.active_connections[room_id]:
            del self.active_connections[room_id]
            print(f"🗑️ {room_id} odası boşaldı ve silindi.")
        
        if username:
            print(f"❌ {username} <- {room_id} odasından ayrıldı.")
        
        return username
    
    async def broadcast(self, room_id: str, message: dict, sender_username: str = None, exclude_sender: bool = False):
        """
        Odadaki tüm kullanıcılara mesaj gönderir.
        
        Args:
            room_id: Hedef oda
            message: Gönderilecek mesaj (dict -> JSON'a dönüştürülür)
            sender_username: Gönderen kullanıcı adı (opsiyonel, sistem mesajları için None olabilir)
            exclude_sender: True ise göndericiye mesaj gönderilmez (typing indicator için)
        """
        if room_id not in self.active_connections:
            return
        
        # Mesajı JSON string'e çevir
        message_json = json.dumps(message, ensure_ascii=False)
        
        # Tüm kullanıcılara gönder (exclude_sender True ise göndericiye hariç)
        disconnected = []
        for connection in self.active_connections[room_id]:
            # Eğer exclude_sender True ve bu kullanıcı gönderici ise atla
            if exclude_sender and sender_username and connection["username"] == sender_username:
                continue
                
            try:
                await connection["websocket"].send_text(message_json)
            except Exception as e:
                print(f"⚠️ {connection['username']} kullanıcısına mesaj gönderilemedi: {e}")
                disconnected.append(connection["websocket"])
        
        # Bağlantısı kopanları temizle
        for ws in disconnected:
            self.disconnect(ws, room_id)
    
    def get_room_users(self, room_id: str) -> List[str]:
        """
        Odadaki kullanıcı isimlerini döner.
        
        Args:
            room_id: Oda ID'si
            
        Returns:
            List[str]: Kullanıcı isimleri listesi
        """
        if room_id not in self.active_connections:
            return []
        
        return [conn["username"] for conn in self.active_connections[room_id]]
    
    def get_room_count(self, room_id: str) -> int:
        """
        Odadaki kullanıcı sayısını döner.
        
        Args:
            room_id: Oda ID'si
            
        Returns:
            int: Kullanıcı sayısı
        """
        if room_id not in self.active_connections:
            return 0
        return len(self.active_connections[room_id])


# Global singleton instance
manager = ConnectionManager()
