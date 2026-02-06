"""
Chat Router - WebSocket ve Mesaj Geçmişi
Mesaj kalıcılığı ile WebSocket endpoint ve history API
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
import json
from datetime import datetime

from database import get_db
from models import Message, Room, User
from manager import manager
from schemas import validate_websocket_message

router = APIRouter()


# ==================== Helper Functions ====================

async def save_message_to_db(
    db: Session,
    room_id: str,
    username: str,
    message_type: str,
    content: str = None,
    file_id: int = None
) -> Message:
    """Mesajı veritabanına kaydet"""
    # Room var mı kontrol et, yoksa oluştur
    room = db.query(Room).filter(Room.room_id == room_id).first()
    if not room:
        room = Room(room_id=room_id, room_name=room_id)
        db.add(room)
        db.commit()
        db.refresh(room)
    
    # User var mı kontrol et, yoksa oluştur (anonim kullanıcı)
    user = db.query(User).filter(User.username == username).first()
    if not user:
        user = User(username=username, display_name=username, is_anonymous=True)
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Mesajı kaydet
    message = Message(
        room_id=room_id,
        username=username,
        message_type=message_type,
        content=content,
        file_id=file_id,
        created_at=datetime.utcnow()
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    
    return message


def message_to_dict(message: Message) -> dict:
    """Message modelini dict'e çevir"""
    result = {
        "type": message.message_type,
        "username": message.username,
        "timestamp": message.created_at.isoformat(),
    }
    
    if message.content:
        result["content"] = message.content
        result["message"] = message.content
    
    if message.file_id and message.file:
        result["file_url"] = message.file.file_url
        result["file_name"] = message.file.original_filename
        result["file_size"] = message.file.file_size
        result["file_type"] = message.file.file_type
    
    return result


# ==================== WebSocket Endpoint ====================

@router.websocket("/ws/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: str,
    username: str,
    db: Session = Depends(get_db)
):
    """WebSocket bağlantısı - mesaj kalıcılığı ile"""
    await manager.connect(websocket, room_id, username)
    
    # Join mesajını kaydet ve broadcast et
    await save_message_to_db(
        db=db,
        room_id=room_id,
        username=username,
        message_type='join',
        content=f"{username} odaya katıldı"
    )
    
    join_message = {
        "type": "join",
        "username": username,
        "message": f"{username} odaya katıldı",
        "timestamp": datetime.utcnow().isoformat(),
        "room_users": manager.get_room_users(room_id)
    }
    await manager.broadcast(room_id, join_message)
    
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message_data = json.loads(data)
                
                # Mesaj tipine göre işle
                if "type" in message_data:
                    try:
                        validated_message = validate_websocket_message(message_data)
                        enriched_message = validated_message.model_dump()
                        if not enriched_message.get("timestamp"):
                            enriched_message["timestamp"] = datetime.utcnow().isoformat()
                        
                        # Mesajı veritabanına kaydet (join/leave hariç)
                        msg_type = enriched_message.get("type", "message")
                        if msg_type == "message" and enriched_message.get("content"):
                            await save_message_to_db(
                                db=db,
                                room_id=room_id,
                                username=username,
                                message_type='message',
                                content=enriched_message["content"]
                            )
                        elif msg_type == "file":
                            file_info = f"Dosya: {enriched_message.get('file_name', 'dosya')}"
                            await save_message_to_db(
                                db=db,
                                room_id=room_id,
                                username=username,
                                message_type='file',
                                content=file_info
                            )
                        
                    except ValueError as e:
                        error_message = {
                            "type": "error",
                            "error_code": "INVALID_MESSAGE_FORMAT",
                            "message": str(e),
                            "timestamp": datetime.utcnow().isoformat()
                        }
                        await websocket.send_text(json.dumps(error_message))
                        continue
                else:
                    # Type belirtilmemişse normal mesaj
                    enriched_message = {
                        "type": "message",
                        "username": username,
                        "content": message_data.get("content", ""),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
                    # Veritabanına kaydet
                    await save_message_to_db(
                        db=db,
                        room_id=room_id,
                        username=username,
                        message_type='message',
                        content=enriched_message["content"]
                    )
                
                # Broadcast yap
                await manager.broadcast(room_id, enriched_message, sender_username=username)
                
            except json.JSONDecodeError:
                # JSON değilse düz metin olarak işle
                enriched_message = {
                    "type": "message",
                    "username": username,
                    "content": data,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                # Veritabanına kaydet
                await save_message_to_db(
                    db=db,
                    room_id=room_id,
                    username=username,
                    message_type='message',
                    content=data
                )
                
                await manager.broadcast(room_id, enriched_message, sender_username=username)
                
    except WebSocketDisconnect:
        disconnected_user = manager.disconnect(websocket, room_id)
        
        # Leave mesajını kaydet
        await save_message_to_db(
            db=db,
            room_id=room_id,
            username=disconnected_user or username,
            message_type='leave',
            content=f"{disconnected_user or username} odadan ayrıldı"
        )
        
        leave_message = {
            "type": "leave",
            "username": disconnected_user or username,
            "message": f"{disconnected_user or username} odadan ayrıldı",
            "timestamp": datetime.utcnow().isoformat(),
            "room_users": manager.get_room_users(room_id)
        }
        await manager.broadcast(room_id, leave_message)


# ==================== REST Endpoints ====================

@router.get("/chat/{room_id}/history")
async def get_chat_history(
    room_id: str,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Oda geçmişini getir (son N mesaj)
    
    Args:
        room_id: Oda ID
        limit: Maksimum mesaj sayısı (varsayılan: 50)
    
    Returns:
        dict: Mesaj listesi
    """
    # Room var mı kontrol et
    room = db.query(Room).filter(Room.room_id == room_id).first()
    if not room:
        return {"room_id": room_id, "messages": [], "count": 0}
    
    # Son N mesajı çek (silinen mesajları hariç tut)
    messages = db.query(Message)\
        .filter(Message.room_id == room_id, Message.is_deleted == False)\
        .order_by(Message.created_at.desc())\
        .limit(limit)\
        .all()
    
    # Ters çevir (en eski mesaj üstte olsun)
    messages.reverse()
    
    # Dict'e çevir
    message_list = [message_to_dict(msg) for msg in messages]
    
    return {
        "room_id": room_id,
        "messages": message_list,
        "count": len(message_list)
    }


@router.get("/rooms")
async def get_active_rooms(db: Session = Depends(get_db)):
    """Aktif odaları listele"""
    # Veritabanındaki tüm odalar
    rooms = db.query(Room).filter(Room.is_active == True).all()
    
    room_list = []
    for room in rooms:
        # Manager'daki aktif kullanıcılarla birleştir
        active_users = manager.get_room_users(room.room_id)
        room_list.append({
            "room_id": room.room_id,
            "room_name": room.room_name or room.room_id,
            "description": room.description,
            "last_activity": room.last_activity.isoformat() if room.last_activity else None,
            "message_count": len(room.messages),
            "active_users": active_users,
            "user_count": len(active_users)
        })
    
    return {"total_rooms": len(room_list), "rooms": room_list}
