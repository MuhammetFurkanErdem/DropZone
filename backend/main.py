"""
DropZone - Ana Uygulama Giris Noktasi
FastAPI + WebSocket ile gercek zamanli not paylasim platformu
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from manager import manager
from config import settings
from database import init_db, get_db_info
from routers import upload, chat, rooms
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

# Router'ları ekle
app.include_router(upload.router)
app.include_router(chat.router)  # Chat router (WebSocket + history)
app.include_router(rooms.router)  # Rooms router (Oda yönetimi)

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
            "rooms": "/rooms",
            "chat_history": "/chat/{room_id}/history",
            "upload": "/upload",
            "upload_info": "/upload/info"
        }
    }

if __name__ == "__main__":
    import uvicorn
    print(f" {settings.APP_NAME} Backend baslatiliyor...")
    print(f" API: http://localhost:{settings.PORT}")
    print(f" WebSocket: ws://localhost:{settings.PORT}/ws/{{room_id}}?username={{username}}")
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=settings.RELOAD)
