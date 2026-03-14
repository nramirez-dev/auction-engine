# Security / Race Condition Tests

These scripts verify that the auction engine correctly handles concurrent
requests through its distributed lock and idempotency mechanisms.

## Prerequisites

- Docker Desktop running
- The full stack started: `docker compose up -d`
- `httpx` available in the environment running the script

## Run

```bash
# From the project root — uses the httpx already in requirements.txt
docker compose run --rm api python tests/security/race_condition.py
```

Or directly on the host if you have Python + httpx installed:

```bash
python tests/security/race_condition.py
```

The script targets `http://localhost` (nginx on port 80).

## Scenarios

| # | Name | What it proves |
|---|------|----------------|
| 1 | Concurrent duplicate bids | 10 goroutines fire the same amount simultaneously — the Redis distributed lock must allow **exactly 1** to succeed. |
| 2 | Rapid sequential overbids | 20 bids sent one after another, each +1.00 higher — all 20 must be accepted, proving normal flow is unaffected. |
| 3 | Idempotency-Key replay | The same bid is sent twice with an identical `Idempotency-Key` header — the second request must be rejected with **HTTP 409**. |

## Expected output

```
============================================================
  Auction Engine — Race Condition & Idempotency Test Suite
  Target: http://localhost
============================================================

[Scenario 1] 10 concurrent bids with the same amount
  Status distribution: {201: 1, 422: 9}
  Successful bids (201): 1 — expected: 1
  PASS: distributed lock held.

[Scenario 2] 20 rapid sequential bids, each 1.00 higher than the last
  Status distribution: {201: 20}
  Successful bids (201): 20 — expected: 20
  PASS: all bids accepted in order.

[Scenario 3] Same bid sent twice with identical Idempotency-Key
  First request:  HTTP 201 — expected: 201
  Second request: HTTP 409 — expected: 409
  PASS: idempotency enforced.

============================================================
  Result: 3/3 scenarios passed
============================================================
```

## Exit codes

- `0` — all scenarios passed
- `1` — one or more scenarios failed or errored
