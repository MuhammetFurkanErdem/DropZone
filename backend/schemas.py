"""
Pydantic Schemas - Veri Doğrulama ve Serileştirme
Tüm WebSocket mesajları ve API request/response'ları için tip güvenliği sağlar.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal
from datetime import datetime


# ==================== WebSocket Mesaj Şemaları ====================

class MessageBase(BaseModel):
    """WebSocket üzerinden gönderilen her mesajın temel yapısı"""
    type: Literal["join", "leave", "message", "file", "error", "system", "typing_start", "typing_stop"]
    timestamp: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "message",
                "timestamp": "2026-02-06T12:30:00"
            }
        }


class ChatMessage(MessageBase):
    """Kullanıcı mesajı şeması"""
    type: Literal["message"] = "message"
    username: str = Field(..., min_length=1, max_length=50)
    content: str = Field(..., min_length=1, max_length=5000)
    room_id: Optional[str] = None
    
    @field_validator('content')
    @classmethod
    def content_not_empty(cls, v: str) -> str:
        """Mesaj içeriğinin boş olmamasını sağla"""
        if not v.strip():
            raise ValueError("Mesaj içeriği boş olamaz")
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "message",
                "username": "Ahmet",
                "content": "Merhaba, bugünkü ders notu var mı?",
                "timestamp": "2026-02-06T12:30:00"
            }
        }


class JoinMessage(MessageBase):
    """Odaya katılma bildirimi şeması"""
    type: Literal["join"] = "join"
    username: str
    message: str
    room_users: list[str] = []
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "join",
                "username": "Mehmet",
                "message": "Mehmet odaya katıldı",
                "room_users": ["Ahmet", "Mehmet"],
                "timestamp": "2026-02-06T12:30:00"
            }
        }


class LeaveMessage(MessageBase):
    """Odadan ayrılma bildirimi şeması"""
    type: Literal["leave"] = "leave"
    username: str
    message: str
    room_users: list[str] = []
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "leave",
                "username": "Ahmet",
                "message": "Ahmet odadan ayrıldı",
                "room_users": ["Mehmet"],
                "timestamp": "2026-02-06T12:30:00"
            }
        }


class FileMessage(MessageBase):
    """Dosya paylaşım mesajı şeması (FAZ 2)"""
    type: Literal["file"] = "file"
    username: str
    file_url: str
    file_name: str
    file_size: int  # Bytes cinsinden
    file_type: str  # MIME type (application/pdf, image/jpeg, etc.)
    room_id: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "file",
                "username": "Ahmet",
                "file_url": "/static/uploads/abc123-ders-notu.pdf",
                "file_name": "Matematik-101-Ders-Notu.pdf",
                "file_size": 2048576,
                "file_type": "application/pdf",
                "timestamp": "2026-02-06T12:30:00"
            }
        }


class ErrorMessage(MessageBase):
    """Hata mesajı şeması"""
    type: Literal["error"] = "error"
    error_code: str
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "error",
                "error_code": "INVALID_MESSAGE",
                "message": "Mesaj formatı geçersiz",
                "timestamp": "2026-02-06T12:30:00"
            }
        }


class SystemMessage(MessageBase):
    """Sistem mesajı şeması (duyurular, bildirimler vb.)"""
    type: Literal["system"] = "system"
    message: str
    severity: Literal["info", "warning", "success"] = "info"
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "system",
                "message": "Sunucu bakıma alınacaktır",
                "severity": "warning",
                "timestamp": "2026-02-06T12:30:00"
            }
        }


class TypingStartMessage(MessageBase):
    """Yazma başlangıç sinyali"""
    type: Literal["typing_start"] = "typing_start"
    username: str = Field(..., min_length=1, max_length=50)
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "typing_start",
                "username": "Ahmet",
                "timestamp": "2026-02-06T12:30:00"
            }
        }


class TypingStopMessage(MessageBase):
    """Yazma durdurma sinyali"""
    type: Literal["typing_stop"] = "typing_stop"
    username: str = Field(..., min_length=1, max_length=50)
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "typing_stop",
                "username": "Ahmet",
                "timestamp": "2026-02-06T12:30:00"
            }
        }


# ==================== API Request/Response Şemaları ====================

class RoomCreate(BaseModel):
    """Oda oluşturma isteği (İleride kullanılacak)"""
    room_name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    max_users: int = Field(default=50, ge=2, le=500)
    
    @field_validator('room_name')
    @classmethod
    def room_name_valid(cls, v: str) -> str:
        """Oda adının geçerli olmasını sağla"""
        if not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError("Oda adı sadece harf, rakam, - ve _ içerebilir")
        return v.strip()


class RoomResponse(BaseModel):
    """Oda bilgisi response şeması"""
    room_id: str
    room_name: Optional[str] = None
    user_count: int
    users: list[str]
    created_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "room_id": "Bilgisayar-101",
                "room_name": "Bilgisayar Programlama 101",
                "user_count": 5,
                "users": ["Ahmet", "Mehmet", "Ayşe"],
                "created_at": "2026-02-06T10:00:00"
            }
        }


class UserJoinRequest(BaseModel):
    """Kullanıcı odaya katılma isteği"""
    username: str = Field(..., min_length=2, max_length=50)
    room_id: str = Field(..., min_length=1, max_length=100)
    
    @field_validator('username')
    @classmethod
    def username_valid(cls, v: str) -> str:
        """Kullanıcı adının geçerli olmasını sağla"""
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Kullanıcı adı en az 2 karakter olmalı")
        # Tehlikeli karakterleri engelle
        forbidden_chars = ['<', '>', '"', "'", '&', '/', '\\']
        if any(char in v for char in forbidden_chars):
            raise ValueError("Kullanıcı adı geçersiz karakter içeriyor")
        return v


class FileUploadResponse(BaseModel):
    """Dosya yükleme response şeması (FAZ 2)"""
    success: bool
    file_url: str
    file_name: str
    file_size: int
    file_type: str
    uploaded_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "file_url": "/static/uploads/abc123-ders-notu.pdf",
                "file_name": "Matematik-101-Ders-Notu.pdf",
                "file_size": 2048576,
                "file_type": "application/pdf",
                "uploaded_at": "2026-02-06T12:30:00"
            }
        }


# ==================== Veritabanı Şemaları (ORM'den API'ye) ====================

class MessageDB(BaseModel):
    """Veritabanından gelen mesaj response'u"""
    id: int
    room_id: str
    username: str
    message_type: str
    content: Optional[str] = None
    file_url: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True  # SQLAlchemy modellerinden otomatik dönüşüm
        json_schema_extra = {
            "example": {
                "id": 1,
                "room_id": "Bilgisayar-101",
                "username": "Ahmet",
                "message_type": "message",
                "content": "Merhaba!",
                "file_url": None,
                "created_at": "2026-02-06T12:30:00"
            }
        }


class RoomDB(BaseModel):
    """Veritabanından gelen oda response'u"""
    id: int
    room_id: str
    room_name: Optional[str] = None
    created_at: datetime
    last_activity: datetime
    
    class Config:
        from_attributes = True


# ==================== Helper Functions ====================

def validate_websocket_message(data: dict) -> MessageBase:
    """
    WebSocket'ten gelen mesajı doğrula ve uygun şemaya dönüştür
    
    Args:
        data: WebSocket'ten gelen JSON dict
        
    Returns:
        Doğrulanmış Pydantic model instance
        
    Raises:
        ValueError: Geçersiz mesaj formatı
    """
    message_type = data.get("type")
    
    if message_type == "message":
        return ChatMessage(**data)
    elif message_type == "join":
        return JoinMessage(**data)
    elif message_type == "leave":
        return LeaveMessage(**data)
    elif message_type == "file":
        return FileMessage(**data)
    elif message_type == "error":
        return ErrorMessage(**data)
    elif message_type == "system":
        return SystemMessage(**data)
    elif message_type == "typing_start":
        return TypingStartMessage(**data)
    elif message_type == "typing_stop":
        return TypingStopMessage(**data)
    else:
        raise ValueError(f"Bilinmeyen mesaj tipi: {message_type}")
