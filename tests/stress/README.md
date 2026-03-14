# Stress Test — Locust

Simulates 100+ concurrent users against the Auction Engine API running behind Nginx.

## Requirements

```bash
pip install locust
```

> Make sure the stack is running first: `docker compose up -d`

## Run (headless)

```bash
locust -f tests/stress/locustfile.py \
  --host=http://localhost \
  --users=100 \
  --spawn-rate=10 \
  --run-time=60s \
  --headless
```

## Run (web UI — recommended for analysis)

```bash
locust -f tests/stress/locustfile.py --host=http://localhost
```

Then open **http://localhost:8089** and set:
- **Users**: 100
- **Spawn rate**: 10/s

## User classes

| Class | Weight | Behaviour |
|---|---|---|
| `AuctionUser` | 3 | Places bids (60%), reads auction (20%), lists products (20%) |
| `OwnerUser` | 1 | Creates products (50%), reads products (50%) |

## What to look for

- **RPS** — requests per second the system sustains
- **p95 / p99 latency** — tail latency for `place-bid` under concurrency
- **Failure rate** — 409s (bid too low / duplicate) are **expected and marked as success**; 5xx errors are failures
- **Nginx** acts as the load balancer — all traffic routes through port 80
