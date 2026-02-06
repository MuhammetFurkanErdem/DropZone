"""
Database Connection ve Session Yönetimi
SQLAlchemy Engine, SessionLocal ve bağlantı yönetimi
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator
from config import settings
import os

# Veritabanı dizinini oluştur (SQLite için)
if settings.DATABASE_URL.startswith("sqlite"):
    db_dir = os.path.dirname(settings.DATABASE_URL.replace("sqlite:///", ""))
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

# SQLAlchemy Engine oluştur
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite için özel ayarlar
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},  # SQLite multi-threading desteği
        poolclass=StaticPool,  # Geliştirme için basit pool
        echo=settings.DEBUG  # SQL sorgularını loga yaz (debug modda)
    )
else:
    # PostgreSQL veya diğer veritabanları için
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,  # Bağlantı kontrolü
        echo=settings.DEBUG
    )

# Session Factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# ==================== Dependency Injection ====================

def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency.
    FastAPI endpoint'lerinde kullanılır:
    
    @app.get("/messages")
    def get_messages(db: Session = Depends(get_db)):
        messages = db.query(Message).all()
        return messages
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==================== Database Initialization ====================

def init_db():
    """
    Veritabanını başlat - tabloları oluştur
    Uygulama başlatılırken bir kez çalıştırılır
    """
    from models import Base, create_all_tables
    
    print("📦 Veritabanı başlatılıyor...")
    create_all_tables(engine)
    print("✅ Veritabanı tabloları oluşturuldu!")


def reset_db():
    """
    Veritabanını sıfırla - tüm tabloları sil ve yeniden oluştur
    ⚠️ DİKKAT: Tüm veriler silinir! Sadece development için!
    """
    from models import Base, drop_all_tables, create_all_tables
    
    if not settings.is_development:
        raise Exception("❌ reset_db() sadece development ortamında çalışır!")
    
    print("🗑️ Tüm tablolar siliniyor...")
    drop_all_tables(engine)
    
    print("📦 Tablolar yeniden oluşturuluyor...")
    create_all_tables(engine)
    
    print("✅ Veritabanı sıfırlandı!")


# ==================== Utility Functions ====================

def check_db_connection() -> bool:
    """
    Veritabanı bağlantısını kontrol et
    
    Returns:
        bool: Bağlantı başarılı ise True
    """
    try:
        from sqlalchemy import text
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"❌ Veritabanı bağlantı hatası: {e}")
        return False


def get_db_info() -> dict:
    """
    Veritabanı bilgilerini döner
    
    Returns:
        dict: DB tipi, URL, tablo sayısı vb.
    """
    from sqlalchemy import inspect
    
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    return {
        "database_url": settings.DATABASE_URL.split("@")[-1] if "@" in settings.DATABASE_URL else settings.DATABASE_URL,
        "database_type": settings.DATABASE_URL.split(":")[0],
        "tables_count": len(tables),
        "tables": tables,
        "is_connected": check_db_connection()
    }


# ==================== Context Manager (Advanced Usage) ====================

class DatabaseSession:
    """
    Context manager olarak database session kullanımı
    
    Örnek kullanım:
    with DatabaseSession() as db:
        user = db.query(User).first()
        print(user)
    """
    
    def __enter__(self) -> Session:
        self.db = SessionLocal()
        return self.db
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.db.rollback()
        self.db.close()
