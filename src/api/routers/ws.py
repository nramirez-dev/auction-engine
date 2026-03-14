from uuid import UUID
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from src.api.deps import get_broadcast_service
from src.domain.interfaces import IBroadcastService

router = APIRouter(prefix="/ws", tags=["websocket"])

@router.websocket("/auction/{auction_id}")
async def auction_websocket(
    websocket: WebSocket,
    auction_id: UUID,
    broadcast_service: IBroadcastService = Depends(get_broadcast_service),
):
    await websocket.accept()

    try:
        async for message in broadcast_service.subscribe(auction_id):
            await websocket.send_json(message)
    except WebSocketDisconnect:
        pass
