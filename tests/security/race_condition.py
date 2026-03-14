"""
Race condition exploit script for the auction-engine bid endpoint.

Targets: http://localhost (nginx on port 80)

Scenarios
---------
1. Concurrent duplicate bids  — 10 goroutines fire the same bid amount simultaneously.
   The distributed Redis lock must ensure exactly 1 succeeds (HTTP 201) and the
   rest fail (HTTP 422 – bid too low, or HTTP 409 – auction not active after the
   first winner closes the gap). PASS = exactly 1 x 201.

2. Rapid sequential overbids  — 20 bids sent one after another, each incrementing
   the amount by 1.  All 20 should succeed because every bid is strictly higher
   than the previous price.  PASS = exactly 20 x 201.

3. Idempotency-Key replay     — The same bid is sent twice with an identical
   Idempotency-Key header.  The second request must be rejected with HTTP 409.
   PASS = first 201, second 409.
"""

import asyncio
import sys
import uuid
from decimal import Decimal

import httpx

BASE_URL = "http://localhost"
HEADERS = {"Content-Type": "application/json"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def create_product(client: httpx.AsyncClient, owner_id: str, starting_price: str) -> str:
    resp = await client.post(
        f"{BASE_URL}/api/v1/products",
        json={
            "owner_id": owner_id,
            "title": "Test product",
            "description": "Created by race_condition.py",
            "starting_price": starting_price,
        },
    )
    print(f"  Create product response: {resp.status_code} {resp.text}")
    resp.raise_for_status()
    return resp.json()["id"]


async def create_auction(client: httpx.AsyncClient, product_id: str, owner_id: str) -> str:
    resp = await client.post(
        f"{BASE_URL}/api/v1/auctions",
        json={"product_id": product_id, "owner_id": owner_id},
    )
    print(f"  Create auction response: {resp.status_code} {resp.text}")
    resp.raise_for_status()
    auction_id = resp.json()["id"]
    print(f"  Auction ID: {auction_id}")
    return auction_id


async def place_bid(
    client: httpx.AsyncClient,
    auction_id: str,
    user_id: str,
    amount: str,
    idempotency_key: str | None = None,
) -> int:
    extra = {"Idempotency-Key": idempotency_key} if idempotency_key else {}
    resp = await client.post(
        f"{BASE_URL}/api/v1/place-bid",
        json={"auction_id": auction_id, "user_id": user_id, "amount": amount},
        headers={**HEADERS, **extra},
    )
    return resp.status_code


# ---------------------------------------------------------------------------
# Scenario 1 – Concurrent duplicate bids
# ---------------------------------------------------------------------------

async def scenario_1() -> bool:
    print("\n[Scenario 1] 10 concurrent bids with the same amount")
    owner_id = str(uuid.uuid4())
    starting_price = "100.00"
    bid_amount = "150.00"

    async with httpx.AsyncClient(timeout=30) as client:
        product_id = await create_product(client, owner_id, starting_price)
        auction_id = await create_auction(client, product_id, owner_id)

        tasks = [
            place_bid(client, auction_id, str(uuid.uuid4()), bid_amount)
            for _ in range(10)
        ]
        statuses = await asyncio.gather(*tasks)

    counts = {s: statuses.count(s) for s in set(statuses)}
    successes = counts.get(201, 0)
    print(f"  Status distribution: {dict(sorted(counts.items()))}")
    print(f"  Successful bids (201): {successes} — expected: 1")

    passed = successes == 1
    print(f"  {'PASS' if passed else 'FAIL'}: distributed lock {'held' if passed else 'FAILED — multiple bids accepted'}.")
    return passed


# ---------------------------------------------------------------------------
# Scenario 2 – Rapid sequential overbids
# ---------------------------------------------------------------------------

async def scenario_2() -> bool:
    print("\n[Scenario 2] 20 rapid sequential bids, each 1.00 higher than the last")
    owner_id = str(uuid.uuid4())
    starting_price = "100.00"

    async with httpx.AsyncClient(timeout=30) as client:
        product_id = await create_product(client, owner_id, starting_price)
        auction_id = await create_auction(client, product_id, owner_id)

        statuses = []
        for i in range(1, 21):
            amount = str(Decimal(starting_price) + Decimal(i))
            status = await place_bid(client, auction_id, str(uuid.uuid4()), amount)
            statuses.append(status)

    counts = {s: statuses.count(s) for s in set(statuses)}
    successes = counts.get(201, 0)
    print(f"  Status distribution: {dict(sorted(counts.items()))}")
    print(f"  Successful bids (201): {successes} — expected: 20")

    passed = successes == 20
    print(f"  {'PASS' if passed else 'FAIL'}: {'all bids accepted in order' if passed else 'some bids were incorrectly rejected'}.")
    return passed


# ---------------------------------------------------------------------------
# Scenario 3 – Idempotency-Key replay
# ---------------------------------------------------------------------------

async def scenario_3() -> bool:
    print("\n[Scenario 3] Same bid sent twice with identical Idempotency-Key")
    owner_id = str(uuid.uuid4())
    starting_price = "100.00"
    bid_amount = "150.00"
    key = str(uuid.uuid4())

    async with httpx.AsyncClient(timeout=30) as client:
        product_id = await create_product(client, owner_id, starting_price)
        auction_id = await create_auction(client, product_id, owner_id)
        user_id = str(uuid.uuid4())

        first = await place_bid(client, auction_id, user_id, bid_amount, idempotency_key=key)
        second = await place_bid(client, auction_id, user_id, bid_amount, idempotency_key=key)

    print(f"  First request:  HTTP {first} — expected: 201")
    print(f"  Second request: HTTP {second} — expected: 409")

    passed = first == 201 and second == 409
    print(f"  {'PASS' if passed else 'FAIL'}: idempotency {'enforced' if passed else 'NOT enforced — duplicate bid was accepted'}.")
    return passed


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

async def main() -> None:
    print("=" * 60)
    print("  Auction Engine — Race Condition & Idempotency Test Suite")
    print(f"  Target: {BASE_URL}")
    print("=" * 60)

    results = await asyncio.gather(
        scenario_1(),
        return_exceptions=True,
    )
    # Scenarios 2 and 3 run after scenario 1 to avoid shared state interference
    results += await asyncio.gather(
        scenario_2(),
        return_exceptions=True,
    )
    results += await asyncio.gather(
        scenario_3(),
        return_exceptions=True,
    )

    passed = 0
    for i, r in enumerate(results, start=1):
        if isinstance(r, Exception):
            print(f"\n[Scenario {i}] ERROR: {r}")
        elif r:
            passed += 1

    total = len(results)
    print("\n" + "=" * 60)
    print(f"  Result: {passed}/{total} scenarios passed")
    print("=" * 60)

    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    asyncio.run(main())
