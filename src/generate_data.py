"""Generate the reproducible 500-row raw transaction dataset used by the lab."""

from __future__ import annotations

import random
from datetime import date, timedelta
from pathlib import Path

import pandas as pd


PRODUCTS = {
    "Wireless Mouse": 29.99,
    "Mechanical Keyboard": 89.99,
    "USB-C Hub": 54.50,
    "Laptop Stand": 47.25,
    "Webcam": 72.00,
    "Noise-Cancelling Headphones": 159.99,
    "Portable SSD": 119.50,
    "Smartphone Case": 24.00,
    "Fitness Tracker": 84.75,
    "Desk Lamp": 39.95,
}

CITIES = [
    "Toronto",
    "Montreal",
    "Vancouver",
    "Ottawa-Gatineau",
    "Calgary",
    "Edmonton",
    "Quebec City",
    "Winnipeg",
    "Hamilton",
    "Kitchener-Cambridge-Waterloo",
]

COUPONS = ["", "", "", "SAVE5", "SAVE10", "SAVE15", "WELCOME20"]


def generate_transactions(rows: int = 500, seed: int = 42) -> pd.DataFrame:
    """Return reproducible synthetic transactions with deliberate quality issues."""
    if rows < 10:
        raise ValueError("rows must be at least 10 so the quality examples can be inserted")

    rng = random.Random(seed)
    start = date(2024, 1, 1)
    records: list[dict] = []

    for number in range(1, rows + 1):
        product = rng.choice(list(PRODUCTS))
        base_price = PRODUCTS[product]
        records.append(
            {
                "transaction_id": f"TXN{number:05d}",
                "date": (start + timedelta(days=rng.randrange(365))).isoformat(),
                "customer_id": f"CUST{rng.randrange(1, 181):04d}",
                "product": product,
                "price": round(base_price * rng.uniform(0.90, 1.10), 2),
                "quantity": rng.randrange(1, 6),
                "coupon_code": rng.choice(COUPONS),
                "shipping_city": rng.choice(CITIES),
            }
        )

    # Known dirty cases support honest before/after cleaning evidence.
    records[7]["date"] = "2024-13-40"              # impossible date
    records[18]["quantity"] = -2                   # invalid quantity
    records[31]["price"] = "unknown"               # invalid numeric value
    records[44]["shipping_city"] = ""              # missing destination
    records[55]["coupon_code"] = "NOTREAL"         # unknown coupon
    records[73]["shipping_city"] = " toronto "     # inconsistent whitespace/case
    records[91]["product"] = "  Webcam "            # inconsistent whitespace
    records[120] = records[119].copy()               # duplicate transaction ID
    return pd.DataFrame(records)


def save_transactions(path: str | Path, rows: int = 500, seed: int = 42) -> Path:
    """Generate and save the raw CSV without cleaning it."""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    generate_transactions(rows=rows, seed=seed).to_csv(destination, index=False)
    return destination


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[1]
    output = save_transactions(project_root / "data" / "ecommerce_transactions_raw.csv")
    print(f"Saved {output}")

