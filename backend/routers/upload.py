"""
Upload Router - Dosya Yükleme Endpoint'leri
PDF ve resim dosyalarını güvenli bir şekilde yükler ve saklar.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from config import settings
from schemas import FileUploadResponse
import uuid
import os
from pathlib import Path
from datetime import datetime
import aiofiles
from typing import Optional

router = APIRouter(
    prefix="/upload",
    tags=["File Upload"],
    responses={404: {"description": "Not found"}},
)

# İzin verilen MIME tipleri
ALLOWED_MIME_TYPES = {
    "application/pdf": ".pdf",
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "application/msword": ".doc",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
}


def validate_file_size(file_size: int) -> bool:
    """
    Dosya boyutunu kontrol eder
    
    Args:
        file_size: Dosya boyutu (bytes)
        
    Returns:
        bool: Boyut uygunsa True
    """
    return file_size <= settings.MAX_FILE_SIZE


def validate_file_type(content_type: str) -> bool:
    """
    Dosya tipini kontrol eder
    
    Args:
        content_type: MIME type (örn: "application/pdf")
        
    Returns:
        bool: Tip uygunsa True
    """
    return content_type in ALLOWED_MIME_TYPES


def get_file_extension(content_type: str, original_filename: str) -> str:
    """
    Dosya uzantısını belirler
    
    Args:
        content_type: MIME type
        original_filename: Orijinal dosya adı
        
    Returns:
        str: Dosya uzantısı (örn: ".pdf")
    """
    # Önce MIME type'dan uzantı al
    if content_type in ALLOWED_MIME_TYPES:
        return ALLOWED_MIME_TYPES[content_type]
    
    # MIME type yoksa dosya adından al
    _, ext = os.path.splitext(original_filename)
    return ext.lower() if ext else ""


def generate_unique_filename(original_filename: str, content_type: str) -> str:
    """
    Benzersiz dosya adı oluşturur (UUID kullanarak)
    
    Args:
        original_filename: Orijinal dosya adı
        content_type: MIME type
        
    Returns:
        str: Benzersiz dosya adı (örn: "abc123-ders-notu.pdf")
    """
    # Dosya uzantısını al
    extension = get_file_extension(content_type, original_filename)
    
    # Orijinal dosya adını temizle (sadece alfanumerik karakterler)
    clean_name = "".join(c for c in original_filename if c.isalnum() or c in ['-', '_', '.'])
    name_without_ext = os.path.splitext(clean_name)[0][:50]  # İlk 50 karakter
    
    # UUID + temiz isim + uzantı
    unique_id = str(uuid.uuid4())[:8]
    return f"{unique_id}-{name_without_ext}{extension}"


async def save_upload_file(upload_file: UploadFile, destination: Path) -> int:
    """
    Yüklenen dosyayı diske kaydeder
    
    Args:
        upload_file: FastAPI UploadFile objesi
        destination: Hedef dosya yolu
        
    Returns:
        int: Kaydedilen dosya boyutu (bytes)
    """
    total_size = 0
    
    async with aiofiles.open(destination, 'wb') as out_file:
        while content := await upload_file.read(8192):  # 8KB chunks
            total_size += len(content)
            
            # Dosya boyutu limitini kontrol et
            if total_size > settings.MAX_FILE_SIZE:
                # Dosyayı sil ve hata fırlat
                await out_file.close()
                os.remove(destination)
                raise HTTPException(
                    status_code=413,
                    detail=f"Dosya boyutu {settings.MAX_FILE_SIZE / (1024*1024):.1f}MB limitini aşıyor"
                )
            
            await out_file.write(content)
    
    return total_size


@router.post("/", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    room_id: Optional[str] = Form(None),
    username: Optional[str] = Form(None)
):
    """
    Dosya yükleme endpoint'i
    
    Args:
        file: Yüklenecek dosya (PDF, JPG, PNG, GIF, DOC, DOCX)
        room_id: Dosyanın paylaşılacağı oda ID'si (opsiyonel)
        username: Dosyayı yükleyen kullanıcı (opsiyonel)
        
    Returns:
        FileUploadResponse: Yüklenen dosya bilgileri
        
    Raises:
        HTTPException 400: Dosya tipi veya boyutu uygun değil
        HTTPException 413: Dosya boyutu limiti aşıldı
        HTTPException 500: Dosya kaydetme hatası
    """
    
    # 1. Dosya tipi kontrolü
    if not validate_file_type(file.content_type):
        raise HTTPException(
            status_code=400,
            detail=f"Desteklenmeyen dosya tipi: {file.content_type}. "
                   f"İzin verilen tipler: {', '.join(ALLOWED_MIME_TYPES.keys())}"
        )
    
    # 2. Benzersiz dosya adı oluştur
    stored_filename = generate_unique_filename(file.filename, file.content_type)
    file_path = Path(settings.UPLOAD_DIR) / stored_filename
    
    # 3. Upload dizinini oluştur (yoksa)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # 4. Dosyayı kaydet
        file_size = await save_upload_file(file, file_path)
        
        # 5. Dosya URL'ini oluştur
        file_url = f"/static/uploads/{stored_filename}"
        
        # 6. Response döndür
        return FileUploadResponse(
            success=True,
            file_url=file_url,
            file_name=file.filename,
            file_size=file_size,
            file_type=file.content_type,
            uploaded_at=datetime.now()
        )
    
    except HTTPException:
        # HTTPException'ları olduğu gibi fırlat
        raise
    
    except Exception as e:
        # Genel hatalar
        # Eğer dosya oluşturulduysa sil
        if file_path.exists():
            os.remove(file_path)
        
        raise HTTPException(
            status_code=500,
            detail=f"Dosya yükleme hatası: {str(e)}"
        )


@router.get("/info")
async def get_upload_info():
    """
    Dosya yükleme ayarları ve limitleri hakkında bilgi döner
    """
    return {
        "max_file_size": settings.MAX_FILE_SIZE,
        "max_file_size_mb": settings.MAX_FILE_SIZE / (1024 * 1024),
        "allowed_types": list(ALLOWED_MIME_TYPES.keys()),
        "allowed_extensions": list(set(ALLOWED_MIME_TYPES.values())),
        "upload_directory": settings.UPLOAD_DIR
    }
