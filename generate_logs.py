"""Generate realistic distributed logs with injected anomalies."""
from __future__ import annotations
import argparse
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path

SERVICES = ["auth", "api", "payments", "orders", "inventory", "database"]
NORMAL = [
    ("INFO", "Request completed user_id={num} status=200 response_ms={ms}"),
    ("INFO", "Fetched order order_id={uuid} status=200 response_ms={ms}"),
    ("INFO", "Cache hit key=product:{num} status=200 response_ms={ms}"),
    ("INFO", "Login successful user_id={num} status=200 response_ms={ms}"),
    ("INFO", "Database query completed rows={num} status=200 response_ms={ms}"),
    ("DEBUG", "Health check passed status=200 response_ms={ms}"),
]
ANOMALIES = [
    ("ERROR", "Database timeout host=db-primary status=504 response_ms=4900"),
    ("ERROR", "Authentication failed user_id={num} status=401 response_ms=1800"),
    ("ERROR", "Connection refused host=cache-prod status=503 response_ms=3200"),
    ("CRITICAL", "Payment processor unavailable status=503 response_ms=7100"),
    ("ERROR", "Unhandled exception NullPointerException status=500 response_ms=2800"),
    ("WARN", "Unexpected request path=/internal/debug status=404 response_ms=950"),
]

def make_logs(rows=1000, seed=42):
    random.seed(seed)
    start = datetime(2026, 8, 31, 9, 0, 0)
    output = []
    anomaly_indices = set(random.sample(range(rows), max(1, rows // 20)))
    for i in range(rows):
        timestamp = start + timedelta(seconds=i * random.randint(2, 5))
        service = random.choice(SERVICES)
        if i in anomaly_indices:
            level, template = random.choice(ANOMALIES)
            message = template.format(num=random.randint(1000, 9999))
        else:
            level, template = random.choice(NORMAL)
            message = template.format(num=random.randint(1000, 9999), ms=random.randint(8, 180), uuid=str(uuid.uuid4()))
        request_id = str(uuid.uuid4())
        ip = f"10.24.{random.randint(1, 30)}.{random.randint(1, 254)}"
        output.append(f"{timestamp:%Y-%m-%d %H:%M:%S} {level} {service} {message} request_id={request_id} ip={ip}")
    return "\n".join(output) + "\n"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=1000)
    parser.add_argument("--output", default="data/sample_logs.log")
    args = parser.parse_args()
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(make_logs(args.rows), encoding="utf-8")
    print(f"Wrote {args.rows} logs to {path}")
