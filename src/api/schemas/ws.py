from pydantic import BaseModel


class WsTicketResponse(BaseModel):
    ticket: str
    expires_in: int = 30
