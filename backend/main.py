"""
DropZone - Ana Uygulama Giris Noktasi
FastAPI + WebSocket ile gercek zamanli not paylasim platformu
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from manager import manager
from config import settings
from database import init_db, get_db_info
from schemas import validate_websocket_message
import json
from datetime import datetime
from pathlib import Path

app = FastAPI(
    title=settings.APP_NAME,
    description="Universite ogrencileri icin gercek zamanli not paylasim platformu",
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path(settings.UPLOAD_DIR)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
Path("logs").mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup_event():
    print("=" * 60)
    print(f" {settings.APP_NAME} v{settings.APP_VERSION} Baslatiliyor...")
    print(f" Ortam: {settings.ENVIRONMENT}")
    print("=" * 60)
    init_db()
    db_info = get_db_info()
    db_type = db_info["database_type"]
    table_count = db_info["tables_count"]
    print(f" Veritabani: {db_type}")
    print(f" Tablo Sayisi: {table_count}")
    print("=" * 60)

@app.on_event("shutdown")
async def shutdown_event():
    print("\n" + "=" * 60)
    print(" DropZone kapatiliyor...")
    print("=" * 60)

@app.get("/")
async def root():
    db_info = get_db_info()
    return {
        "app": settings.APP_NAME,
        "status": "running",
        "version": settings.APP_VERSION,
        "database": {
            "connected": db_info["is_connected"],
            "type": db_info["database_type"]
        },
        "endpoints": {
            "websocket": "/ws/{room_id}?username={username}",
            "rooms": "/rooms"
        }
    }

@app.get("/rooms")
async def get_active_rooms():
    rooms = []
    for room_id in manager.active_connections.keys():
        rooms.append({
            "room_id": room_id,
            "user_count": manager.get_room_count(room_id),
            "users": manager.get_room_users(room_id)
        })
    return {"total_rooms": len(rooms), "rooms": rooms}

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, username: str):
    await manager.connect(websocket, room_id, username)
    join_message = {
        "type": "join",
        "username": username,
        "message": f"{username} odaya katildi",
        "timestamp": datetime.now().isoformat(),
        "room_users": manager.get_room_users(room_id)
    }
    await manager.broadcast(room_id, join_message)
    
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message_data = json.loads(data)
                if "type" in message_data:
                    try:
                        validated_message = validate_websocket_message(message_data)
                        enriched_message = validated_message.model_dump()
                        if not enriched_message.get("timestamp"):
                            enriched_message["timestamp"] = datetime.now().isoformat()
                    except ValueError as e:
                        error_message = {
                            "type": "error",
                            "error_code": "INVALID_MESSAGE_FORMAT",
                            "message": str(e),
                            "timestamp": datetime.now().isoformat()
                        }
                        await websocket.send_text(json.dumps(error_message))
                        continue
                else:
                    enriched_message = {
                        "type": "message",
                        "username": username,
                        "content": message_data.get("content", ""),
                        "timestamp": datetime.now().isoformat()
                    }
                await manager.broadcast(room_id, enriched_message, sender_username=username)
            except json.JSONDecodeError:
                enriched_message = {
                    "type": "message",
                    "username": username,
                    "content": data,
                    "timestamp": datetime.now().isoformat()
                }
                await manager.broadcast(room_id, enriched_message, sender_username=username)
    except WebSocketDisconnect:
        disconnected_user = manager.disconnect(websocket, room_id)
        leave_message = {
            "type": "leave",
            "username": disconnected_user or username,
            "message": f"{disconnected_user or username} odadan ayrildi",
            "timestamp": datetime.now().isoformat(),
            "room_users": manager.get_room_users(room_id)
        }
        await manager.broadcast(room_id, leave_message)

if __name__ == "__main__":
    import uvicorn
    print(f" {settings.APP_NAME} Backend baslatiliyor...")
    print(f" API: http://localhost:{settings.PORT}")
    print(f" WebSocket: ws://localhost:{settings.PORT}/ws/{{room_id}}?username={{username}}")
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=settings.RELOAD)
