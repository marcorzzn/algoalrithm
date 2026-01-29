from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from backend.api.websocket.manager import manager
from backend.auth.security import get_current_user_ws  # Versione async per WS
from backend.auth.models import User
import json
import asyncio

router = APIRouter()

@router.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Ricevi messaggi dal client (subscribe a specifici match, etc)
            data = await websocket.receive_json()
            
            if data.get("action") == "subscribe_match":
                match_id = data.get("match_id")
                # Logica per subscription specifica
                await websocket.send_json({
                    "type": "subscribed",
                    "match_id": match_id
                })
            
            elif data.get("action") == "ping":
                await websocket.send_json({"type": "pong"})
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)

# Endpoint protetto per utenti autenticati
@router.websocket("/ws/user")
async def user_websocket(websocket: WebSocket, token: str):
    # Validazione token (semplificata)
    user = await validate_token(token)  # Da implementare
    if not user:
        await websocket.close(code=4001)
        return
    
    await manager.connect(websocket, user_id=str(user.id))
    try:
        while True:
            data = await websocket.receive_json()
            # Gestisci messaggi personalizzati per l'utente
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id=str(user.id))