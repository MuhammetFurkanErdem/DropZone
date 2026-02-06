"""
Rooms Router - Oda Yönetimi
Oda oluşturma, kontrol etme ve listeleme endpoint'leri
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from database import get_db
from models import Room
from utils import generate_unique_room_code

router = APIRouter(prefix="/rooms", tags=["rooms"])


# ==================== Schemas ====================

class RoomCreateRequest(BaseModel):
    """Oda oluşturma request"""
    room_name: str


class RoomCreateResponse(BaseModel):
    """Oda oluşturma response"""
    success: bool
    code: str
    room_name: str
    message: str
    created_at: str


class RoomCheckResponse(BaseModel):
    """Oda kontrolü response"""
    exists: bool
    code: str
    room_name: str | None = None
    user_count: int = 0


# ==================== Endpoints ====================

@router.post("/create", response_model=RoomCreateResponse)
async def create_room(request: RoomCreateRequest, db: Session = Depends(get_db)):
    """
    Yeni bir oda oluşturur ve benzersiz kod döner.
    
    Args:
        request: Oda ismi içeren request
    
    Returns:
        RoomCreateResponse: Oda kodu ve bilgileri
    """
    try:
        # Benzersiz kod üret
        code = generate_unique_room_code(db)
        
        # Yeni oda oluştur
        new_room = Room(
            room_id=code,
            room_name=request.room_name or f"Oda {code}",
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        db.add(new_room)
        db.commit()
        db.refresh(new_room)
        
        return RoomCreateResponse(
            success=True,
            code=code,
            room_name=new_room.room_name,
            message=f"Oda başarıyla oluşturuldu: {code}",
            created_at=new_room.created_at.isoformat()
        )
        
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Oda oluşturulurken hata: {str(e)}")


@router.get("/{code}/check", response_model=RoomCheckResponse)
async def check_room(code: str, db: Session = Depends(get_db)):
    """
    Odanın var olup olmadığını kontrol eder.
    
    Args:
        code: Oda kodu
    
    Returns:
        RoomCheckResponse: Oda bilgileri
    """
    # Oda kodunu büyük harfe çevir (case-insensitive)
    code = code.upper()
    
    # Odayı veritabanında ara
    room = db.query(Room).filter(Room.room_id == code, Room.is_active == True).first()
    
    if room:
        # Aktif kullanıcı sayısını manager'dan al (eğer import edilebilirse)
        try:
            from manager import manager
            user_count = len(manager.get_room_users(code))
        except:
            user_count = 0
        
        return RoomCheckResponse(
            exists=True,
            code=code,
            room_name=room.room_name,
            user_count=user_count
        )
    else:
        return RoomCheckResponse(
            exists=False,
            code=code
        )


@router.get("/list")
async def list_active_rooms(db: Session = Depends(get_db)):
    """
    Aktif odaları listeler.
    
    Returns:
        dict: Aktif oda listesi
    """
    rooms = db.query(Room).filter(Room.is_active == True).order_by(Room.created_at.desc()).limit(50).all()
    
    room_list = []
    for room in rooms:
        try:
            from manager import manager
            user_count = len(manager.get_room_users(room.room_id))
        except:
            user_count = 0
        
        room_list.append({
            "code": room.room_id,
            "name": room.room_name,
            "created_at": room.created_at.isoformat(),
            "user_count": user_count
        })
    
    return {
        "total": len(room_list),
        "rooms": room_list
    }
