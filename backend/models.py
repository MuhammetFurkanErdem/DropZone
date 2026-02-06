"""
SQLAlchemy Database Models
Veritabanı tablolarının ORM tanımları
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Room(Base):
    """
    Oda (Room) Tablosu
    Her oda bir ders veya grup için ayrı sohbet odası temsil eder.
    """
    __tablename__ = "rooms"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    room_id = Column(String(100), unique=True, nullable=False, index=True)  # Kullanıcı tarafından belirlenen ID (örn: "Bilgisayar-101")
    room_name = Column(String(200), nullable=True)  # Oda başlığı (örn: "Bilgisayar Programlama 101")
    description = Column(Text, nullable=True)  # Oda açıklaması
    max_users = Column(Integer, default=50)  # Maksimum kullanıcı sayısı
    is_active = Column(Boolean, default=True)  # Oda aktif mi?
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_activity = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    messages = relationship("Message", back_populates="room", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Room(room_id='{self.room_id}', name='{self.room_name}')>"


class User(Base):
    """
    Kullanıcı (User) Tablosu
    Şu an için anonim giriş, ileride authentication eklenecek
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    display_name = Column(String(100), nullable=True)  # Görünen isim
    email = Column(String(255), unique=True, nullable=True, index=True)  # İleride kullanılacak
    password_hash = Column(String(255), nullable=True)  # İleride kullanılacak
    is_active = Column(Boolean, default=True)
    is_anonymous = Column(Boolean, default=True)  # Anonim kullanıcı mı?
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_seen = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    messages = relationship("Message", back_populates="user", cascade="all, delete-orphan")
    uploaded_files = relationship("File", back_populates="uploader", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(username='{self.username}', anonymous={self.is_anonymous})>"


class Message(Base):
    """
    Mesaj (Message) Tablosu
    Tüm sohbet mesajlarını ve dosya paylaşımlarını kaydeder
    """
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    room_id = Column(String(100), ForeignKey("rooms.room_id", ondelete="CASCADE"), nullable=False, index=True)
    username = Column(String(50), ForeignKey("users.username", ondelete="SET NULL"), nullable=True, index=True)
    
    # Mesaj tipi: "message", "join", "leave", "file", "system"
    message_type = Column(String(20), default="message", nullable=False)
    
    # İçerik
    content = Column(Text, nullable=True)  # Metin mesajı
    file_id = Column(Integer, ForeignKey("files.id", ondelete="SET NULL"), nullable=True)  # Dosya mesajı için
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    is_deleted = Column(Boolean, default=False)  # Soft delete
    
    # İlişkiler
    room = relationship("Room", back_populates="messages")
    user = relationship("User", back_populates="messages")
    file = relationship("File", back_populates="message")
    
    def __repr__(self):
        return f"<Message(id={self.id}, room='{self.room_id}', user='{self.username}', type='{self.message_type}')>"


class File(Base):
    """
    Dosya (File) Tablosu
    Yüklenen tüm dosyaların metadata'sını tutar
    """
    __tablename__ = "files"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    room_id = Column(String(100), ForeignKey("rooms.room_id", ondelete="CASCADE"), nullable=False, index=True)
    uploader_username = Column(String(50), ForeignKey("users.username", ondelete="SET NULL"), nullable=True)
    
    # Dosya bilgileri
    original_filename = Column(String(255), nullable=False)  # Kullanıcının verdiği isim
    stored_filename = Column(String(255), unique=True, nullable=False)  # Sunucuda saklanan isim (UUID)
    file_path = Column(String(500), nullable=False)  # Disk üzerindeki tam yol
    file_url = Column(String(500), nullable=False)  # Erişim URL'i
    
    # Dosya metadata
    file_size = Column(Integer, nullable=False)  # Bytes cinsinden
    file_type = Column(String(100), nullable=False)  # MIME type (application/pdf, image/jpeg, etc.)
    file_extension = Column(String(10), nullable=False)  # .pdf, .jpg, etc.
    
    # Zaman bilgisi
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    is_deleted = Column(Boolean, default=False)  # Soft delete
    
    # İlişkiler
    uploader = relationship("User", back_populates="uploaded_files")
    message = relationship("Message", back_populates="file", uselist=False)
    
    def __repr__(self):
        return f"<File(id={self.id}, name='{self.original_filename}', type='{self.file_type}')>"


class RoomSession(Base):
    """
    Oda Oturum (RoomSession) Tablosu
    Kullanıcıların odalardaki oturum geçmişini tutar (kim ne zaman hangi odada)
    """
    __tablename__ = "room_sessions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    room_id = Column(String(100), ForeignKey("rooms.room_id", ondelete="CASCADE"), nullable=False, index=True)
    username = Column(String(50), ForeignKey("users.username", ondelete="CASCADE"), nullable=False, index=True)
    
    joined_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    left_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)  # Oturum süresi (saniye)
    
    is_active = Column(Boolean, default=True)  # Hala odada mı?
    
    def __repr__(self):
        return f"<RoomSession(room='{self.room_id}', user='{self.username}', active={self.is_active})>"


# ==================== Helper Functions ====================

def create_all_tables(engine):
    """Tüm tabloları oluşturur"""
    Base.metadata.create_all(bind=engine)


def drop_all_tables(engine):
    """Tüm tabloları siler (DİKKAT: Sadece development için!)"""
    Base.metadata.drop_all(bind=engine)
