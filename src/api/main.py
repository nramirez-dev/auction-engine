from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from src.infrastructure.redis.client import redis_manager
from src.api.routers import bids, products, ws, auctions
from src.domain.exceptions import (
    BidTooLowException,
    AuctionNotActiveException,
    AuctionNotFoundException,
    ProductNotFoundException,
    DuplicateBidException,
    UnauthorizedProductAccessException
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_manager.connect()
    yield
    await redis_manager.disconnect()

app = FastAPI(
    title="Auction Engine",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error = exc.errors()[0]
    field = error.get("loc", ["unknown"])[-1]
    msg = error.get("msg", "invalid")
    return JSONResponse(
        status_code=422,
        content={"error": f"Invalid request: {field} - {msg}"}
    )

@app.exception_handler(BidTooLowException)
async def bid_too_low_handler(request: Request, exc: BidTooLowException):
    return JSONResponse(
        status_code=422,
        content={"error": f"Bid amount must be higher than current price of {exc.current_price}"}
    )

@app.exception_handler(AuctionNotActiveException)
async def auction_not_active_handler(request: Request, exc: AuctionNotActiveException):
    return JSONResponse(
        status_code=409,
        content={"error": "This auction is no longer active"}
    )

@app.exception_handler(AuctionNotFoundException)
async def auction_not_found_handler(request: Request, exc: AuctionNotFoundException):
    return JSONResponse(
        status_code=404,
        content={"error": "Auction not found"}
    )

@app.exception_handler(ProductNotFoundException)
async def product_not_found_handler(request: Request, exc: ProductNotFoundException):
    return JSONResponse(
        status_code=404,
        content={"error": "Product not found"}
    )

@app.exception_handler(DuplicateBidException)
async def duplicate_bid_handler(request: Request, exc: DuplicateBidException):
    return JSONResponse(
        status_code=409,
        content={"error": "This bid was already processed"}
    )

@app.exception_handler(UnauthorizedProductAccessException)
async def unauthorized_product_access_handler(request: Request, exc: UnauthorizedProductAccessException):
    return JSONResponse(
        status_code=403,
        content={"error": "You don't have permission to perform this action"}
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "An unexpected error occurred. Please try again later."},
    )

app.include_router(bids.router, prefix="/api/v1")
app.include_router(products.router, prefix="/api/v1")
app.include_router(auctions.router, prefix="/api/v1")
app.include_router(ws.http_router, prefix="/api/v1")
app.include_router(ws.router)
