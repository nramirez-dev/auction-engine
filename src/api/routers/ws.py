import uuid
from uuid import UUID

from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from redis.asyncio import Redis

from src.api.deps import get_broadcast_service, get_redis_client
from src.api.schemas.ws import WsTicketResponse
from src.domain.interfaces import IBroadcastService

_TICKET_TTL = 30

# WebSocket endpoints — included in main.py without an extra prefix
router = APIRouter(prefix="/ws", tags=["websocket"])

# HTTP ticket endpoint — included in main.py under /api/v1
http_router = APIRouter(tags=["websocket"])


@http_router.get("/ws-ticket", response_model=WsTicketResponse)
async def get_ws_ticket(
    user_id: UUID,
    redis: Redis = Depends(get_redis_client),
):
    ticket = str(uuid.uuid4())
    await redis.set(f"ws_ticket:{ticket}", str(user_id), ex=_TICKET_TTL)
    return WsTicketResponse(ticket=ticket)


@router.websocket("/auction/{auction_id}")
async def auction_websocket(
    websocket: WebSocket,
    auction_id: UUID,
    ticket: str | None = Query(default=None),
    redis: Redis = Depends(get_redis_client),
    broadcast_service: IBroadcastService = Depends(get_broadcast_service),
):
    if not ticket or not await redis.getdel(f"ws_ticket:{ticket}"):
        await websocket.close(code=4001, reason="Invalid or expired ticket")
        return

    await websocket.accept()

    try:
        async for message in broadcast_service.subscribe(auction_id):
            await websocket.send_json(message)
    except WebSocketDisconnect:
        pass
