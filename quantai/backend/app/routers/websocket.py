# backend/app/routers/websocket.py
from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(tags=["websocket"])


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    user_id = websocket.query_params.get("user_id", "public")
    manager = websocket.app.state.ws_manager
    await manager.connect(user_id=user_id, websocket=websocket)
    try:
        while True:
            data = await websocket.receive_json()
            if data.get("type") == "ping":
                await websocket.send_json({"type": "pong", "ts": datetime.now(UTC).isoformat()})
            elif data.get("type") == "replay_request":
                since_iso = str(data.get("since", datetime.now(UTC).isoformat()))
                events = await manager.replay(user_id=user_id, since_iso=since_iso)
                await websocket.send_json({"type": "replay", "events": events})
            else:
                await websocket.send_json({"type": "echo", "payload": data})
    except WebSocketDisconnect:
        manager.disconnect(user_id=user_id, websocket=websocket)
        return
