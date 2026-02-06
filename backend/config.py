"""
Uygulama Konfigürasyon Yönetimi
.env dosyasından ayarları okur ve merkezi bir yerden erişim sağlar.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    """
    Uygulama ayarları - .env dosyasından otomatik yüklenir
    """
    
    # Uygulama Bilgileri
    APP_NAME: str = "DropZone"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # Sunucu Ayarları
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True
    
    # Veritabanı
    DATABASE_URL: str = "sqlite:///./dropzone.db"
    
    # Dosya Yükleme
    UPLOAD_DIR: str = "static/uploads"
    MAX_FILE_SIZE: int = 10485760  # 10MB
    ALLOWED_FILE_TYPES: str = ".pdf,.jpg,.jpeg,.png,.gif,.doc,.docx"
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    
    # Güvenlik (İleride JWT için)
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # WebSocket
    WS_MESSAGE_QUEUE_SIZE: int = 100
    WS_MAX_CONNECTIONS_PER_ROOM: int = 50
    
    # Loglama
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/dropzone.log"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    @property
    def cors_origins_list(self) -> List[str]:
        """CORS origins'i liste olarak döner"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    @property
    def allowed_file_types_list(self) -> List[str]:
        """İzin verilen dosya tiplerini liste olarak döner"""
        return [ext.strip() for ext in self.ALLOWED_FILE_TYPES.split(",")]
    
    @property
    def is_production(self) -> bool:
        """Production ortamında mı çalışıyoruz?"""
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Development ortamında mı çalışıyoruz?"""
        return self.ENVIRONMENT.lower() == "development"


@lru_cache()
def get_settings() -> Settings:
    """
    Settings singleton instance döner (cache'li)
    Uygulama boyunca tek bir Settings instance kullanılır
    """
    return Settings()


# Kolayca kullanılabilir global instance
settings = get_settings()
