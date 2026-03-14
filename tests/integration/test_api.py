import uuid
from httpx import AsyncClient


async def test_create_product(client: AsyncClient):
    """POST /products creates a product and returns 201."""
    response = await client.post(
        "/api/v1/products",
        json={
            "owner_id": str(uuid.uuid4()),
            "title": "Test Widget",
            "description": "A product for testing",
            "starting_price": "100.00",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Widget"
    assert "id" in data


async def test_create_auction(client: AsyncClient):
    """POST /auctions creates an active auction for an existing product and returns 201."""
    owner_id = str(uuid.uuid4())

    product_resp = await client.post(
        "/api/v1/products",
        json={
            "owner_id": owner_id,
            "title": "Auction Product",
            "starting_price": "200.00",
        },
    )
    assert product_resp.status_code == 201
    product_id = product_resp.json()["id"]

    response = await client.post(
        "/api/v1/auctions",
        json={"product_id": product_id, "owner_id": owner_id},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "ACTIVE"
    assert data["product_id"] == product_id
    assert "id" in data


async def test_place_bid(client: AsyncClient):
    """POST /place-bid with a valid amount (> starting price) returns 201."""
    owner_id = str(uuid.uuid4())
    bidder_id = str(uuid.uuid4())

    product_resp = await client.post(
        "/api/v1/products",
        json={"owner_id": owner_id, "title": "Bid Product", "starting_price": "100.00"},
    )
    assert product_resp.status_code == 201
    product_id = product_resp.json()["id"]

    auction_resp = await client.post(
        "/api/v1/auctions",
        json={"product_id": product_id, "owner_id": owner_id},
    )
    assert auction_resp.status_code == 201
    auction_id = auction_resp.json()["id"]

    response = await client.post(
        "/api/v1/place-bid",
        json={"auction_id": auction_id, "user_id": bidder_id, "amount": "150.00"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["auction_id"] == auction_id
    assert data["user_id"] == bidder_id
    assert float(data["amount"]) == 150.00


async def test_place_bid_lower_amount(client: AsyncClient):
    """POST /place-bid with amount <= current price returns 422."""
    owner_id = str(uuid.uuid4())
    bidder_id = str(uuid.uuid4())

    product_resp = await client.post(
        "/api/v1/products",
        json={"owner_id": owner_id, "title": "Low Bid Product", "starting_price": "100.00"},
    )
    assert product_resp.status_code == 201
    product_id = product_resp.json()["id"]

    auction_resp = await client.post(
        "/api/v1/auctions",
        json={"product_id": product_id, "owner_id": owner_id},
    )
    assert auction_resp.status_code == 201
    auction_id = auction_resp.json()["id"]

    # Bid at exactly the starting price — must be strictly greater to succeed
    response = await client.post(
        "/api/v1/place-bid",
        json={"auction_id": auction_id, "user_id": bidder_id, "amount": "100.00"},
    )
    assert response.status_code == 422
