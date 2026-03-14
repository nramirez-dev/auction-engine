"""
Locust stress test for the Auction Engine API.
Run with:
    locust -f tests/stress/locustfile.py --host=http://localhost --users=100 --spawn-rate=10
"""
import random
from uuid import uuid4

from locust import HttpUser, between, events, task

# ── Globals populated during test_start ────────────────────────────────────────
OWNER_ID = "550e8400-e29b-41d4-a716-446655440000"
auction_id: str = ""
product_id: str = ""


# ── One-time setup: create product + auction before users spawn ────────────────
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    global auction_id, product_id

    base_url = environment.host.rstrip("/")

    import requests  # sync request for setup only

    # 1. Create product
    product_resp = requests.post(
        f"{base_url}/api/v1/products",
        json={
            "owner_id": OWNER_ID,
            "title": "Stress Test Product",
            "description": "Auto-created for load testing",
            "starting_price": "1.00",
        },
        timeout=10,
    )
    if product_resp.status_code != 201:
        raise RuntimeError(
            f"[setup] Failed to create product: {product_resp.status_code} {product_resp.text}"
        )
    product_id = product_resp.json()["id"]
    print(f"[setup] Product created: {product_id}")

    # 2. Create auction for that product
    auction_resp = requests.post(
        f"{base_url}/api/v1/auctions",
        json={"product_id": product_id, "owner_id": OWNER_ID},
        timeout=10,
    )
    if auction_resp.status_code != 201:
        raise RuntimeError(
            f"[setup] Failed to create auction: {auction_resp.status_code} {auction_resp.text}"
        )
    auction_id = auction_resp.json()["id"]
    print(f"[setup] Auction created: {auction_id}")


# ── User class: Bidder (weight=3, high frequency) ─────────────────────────────
class AuctionUser(HttpUser):
    """Simulates a high-frequency bidder."""

    weight = 3
    wait_time = between(0.1, 0.5)

    @task(3)
    def place_bid(self):
        if not auction_id:
            return

        amount = round(random.uniform(100, 9999), 2)
        with self.client.post(
            "/api/v1/place-bid",
            json={
                "auction_id": auction_id,
                "user_id": str(uuid4()),
                "amount": amount,
            },
            headers={"Idempotency-Key": str(uuid4())},
            catch_response=True,
            name="/api/v1/place-bid",
        ) as response:
            # 409 (bid too low / duplicate) is expected under concurrency — not a failure
            if response.status_code in (201, 409):
                response.success()
            elif response.status_code >= 500:
                response.failure(f"Server error: {response.status_code}")

    @task(1)
    def get_auction(self):
        if not auction_id:
            return

        with self.client.get(
            f"/api/v1/auctions/{auction_id}",
            catch_response=True,
            name="/api/v1/auctions/{auction_id}",
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Unexpected status: {response.status_code}")

    @task(1)
    def list_products(self):
        with self.client.get(
            "/api/v1/products",
            catch_response=True,
            name="/api/v1/products",
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Unexpected status: {response.status_code}")


# ── User class: Owner (weight=1, low frequency) ───────────────────────────────
class OwnerUser(HttpUser):
    """Simulates a product owner creating and inspecting products."""

    weight = 1
    wait_time = between(1, 3)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._created_product_id: str = ""

    @task(1)
    def create_product(self):
        with self.client.post(
            "/api/v1/products",
            json={
                "owner_id": OWNER_ID,
                "title": f"Product {uuid4().hex[:8]}",
                "description": "Created during stress test",
                "starting_price": str(round(random.uniform(10, 500), 2)),
            },
            catch_response=True,
            name="/api/v1/products [POST]",
        ) as response:
            if response.status_code == 201:
                self._created_product_id = response.json().get("id", "")
                response.success()
            else:
                response.failure(f"Unexpected status: {response.status_code}")

    @task(1)
    def get_product(self):
        pid = self._created_product_id or product_id
        if not pid:
            return

        with self.client.get(
            f"/api/v1/products/{pid}",
            catch_response=True,
            name="/api/v1/products/{product_id}",
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Unexpected status: {response.status_code}")
