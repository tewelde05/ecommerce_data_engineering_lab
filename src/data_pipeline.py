"""Reusable data structures and functions for the 12-step notebook."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


COUPON_DISCOUNTS = {
    "SAVE5": 5,
    "SAVE10": 10,
    "SAVE15": 15,
    "WELCOME20": 20,
}

REQUIRED_COLUMNS = {
    "transaction_id",
    "date",
    "customer_id",
    "product",
    "price",
    "quantity",
    "coupon_code",
    "shipping_city",
}


@dataclass
class Transaction:
    """A small data structure that stores and operates on one transaction."""

    transaction_id: str
    date: object
    customer_id: str
    product: str
    price: object
    quantity: object
    coupon_code: object
    shipping_city: object

    @classmethod
    def from_dict(cls, record: dict) -> "Transaction":
        """Create a Transaction from a row dictionary."""
        return cls(**{field: record.get(field) for field in REQUIRED_COLUMNS})

    def clean(self) -> "Transaction":
        """Apply safe text normalization to this one record."""
        self.product = str(self.product).strip()
        self.shipping_city = str(self.shipping_city).strip().title()
        self.coupon_code = "" if pd.isna(self.coupon_code) else str(self.coupon_code).strip().upper()
        return self

    def total(self) -> float:
        """Calculate this record's discounted line total."""
        discount = COUPON_DISCOUNTS.get(str(self.coupon_code), 0)
        return round(float(self.price) * int(self.quantity) * (1 - discount / 100), 2)


def load_data(path: str | Path, limit: int | None = None) -> pd.DataFrame:
    """Load the raw CSV and verify that the assignment columns exist."""
    frame = pd.read_csv(path, dtype={"transaction_id": "string", "customer_id": "string"})
    missing = REQUIRED_COLUMNS - set(frame.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    return frame.head(limit).copy() if limit else frame


def dataframe_to_records(frame: pd.DataFrame) -> list[dict]:
    """Map a DataFrame to a list of ordinary Python dictionaries."""
    return frame.to_dict(orient="records")


def profile_data(frame: pd.DataFrame) -> dict:
    """Return basic price and city profile values."""
    prices = pd.to_numeric(frame["price"], errors="coerce")
    cities = frame["shipping_city"].fillna("").astype(str).str.strip()
    return {
        "minimum_price": prices.min(),
        "mean_price": prices.mean(),
        "maximum_price": prices.max(),
        "unique_city_count": len(set(cities[cities.ne("")])),
    }


def quality_counts(frame: pd.DataFrame) -> dict[str, int]:
    """Count independent data-quality problems; categories may overlap."""
    dates = pd.to_datetime(frame["date"], errors="coerce")
    prices = pd.to_numeric(frame["price"], errors="coerce")
    quantities = pd.to_numeric(frame["quantity"], errors="coerce")
    cities = frame["shipping_city"].fillna("").astype(str)
    products = frame["product"].fillna("").astype(str)
    coupons = frame["coupon_code"].fillna("").astype(str).str.strip().str.upper()
    return {
        "invalid_date": int(dates.isna().sum()),
        "invalid_price": int((prices.isna() | prices.le(0)).sum()),
        "invalid_quantity": int((quantities.isna() | quantities.le(0) | quantities.mod(1).ne(0)).sum()),
        "missing_shipping_city": int(cities.str.strip().eq("").sum()),
        "unknown_coupon": int((coupons.ne("") & ~coupons.isin(COUPON_DISCOUNTS)).sum()),
        "duplicate_transaction_id": int(frame.duplicated("transaction_id").sum()),
        "unclean_text": int((cities.ne(cities.str.strip().str.title()) | products.ne(products.str.strip())).sum()),
    }


def clean_data(frame: pd.DataFrame) -> pd.DataFrame:
    """Clean a copy of the data while leaving the raw DataFrame unchanged."""
    cleaned = frame.copy()
    cleaned["date"] = pd.to_datetime(cleaned["date"], errors="coerce")
    cleaned["price"] = pd.to_numeric(cleaned["price"], errors="coerce")
    cleaned["quantity"] = pd.to_numeric(cleaned["quantity"], errors="coerce")
    cleaned["product"] = cleaned["product"].astype("string").str.strip()
    cleaned["shipping_city"] = cleaned["shipping_city"].astype("string").str.strip().str.title()
    cleaned["coupon_code"] = cleaned["coupon_code"].astype("string").fillna("").str.strip().str.upper()
    cleaned.loc[~cleaned["coupon_code"].isin(COUPON_DISCOUNTS), "coupon_code"] = ""

    valid = (
        cleaned["date"].notna()
        & cleaned["price"].gt(0)
        & cleaned["quantity"].gt(0)
        & cleaned["quantity"].mod(1).eq(0)
        & cleaned["product"].notna()
        & cleaned["product"].ne("")
        & cleaned["shipping_city"].notna()
        & cleaned["shipping_city"].ne("")
    )
    cleaned = cleaned.loc[valid].drop_duplicates("transaction_id", keep="first").copy()
    cleaned["quantity"] = cleaned["quantity"].astype(int)
    return cleaned.reset_index(drop=True)


def add_transformations(frame: pd.DataFrame, city_metadata: pd.DataFrame) -> pd.DataFrame:
    """Parse discounts and merge the secondary Statistics Canada metadata."""
    if city_metadata["shipping_city"].duplicated().any():
        raise ValueError("city metadata must contain one row per shipping_city")
    transformed = frame.copy()
    transformed["discount_pct"] = transformed["coupon_code"].map(COUPON_DISCOUNTS).fillna(0).astype(int)
    return transformed.merge(city_metadata, on="shipping_city", how="left", validate="many_to_one")


def engineer_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Add reproducible recency and discounted revenue features."""
    result = frame.copy()
    reference_date = result["date"].max()
    result["days_since_purchase"] = (reference_date - result["date"]).dt.days
    result["revenue"] = (
        result["price"] * result["quantity"] * (1 - result["discount_pct"] / 100)
    ).round(2)
    return result


def revenue_by_city(frame: pd.DataFrame) -> pd.DataFrame:
    """Aggregate transaction revenue by shipping city."""
    return (
        frame.groupby("shipping_city", as_index=False)["revenue"]
        .sum()
        .sort_values("revenue", ascending=False)
        .reset_index(drop=True)
    )


def serialize_data(frame: pd.DataFrame, output_dir: str | Path) -> tuple[Path, Path]:
    """Save cleaned data as CSV and JSON and return both paths."""
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    export = frame.copy()
    export["date"] = export["date"].dt.strftime("%Y-%m-%d")
    csv_path = destination / "cleaned_transactions.csv"
    json_path = destination / "cleaned_transactions.json"
    export.to_csv(csv_path, index=False)
    export.to_json(json_path, orient="records", indent=2)
    return csv_path, json_path

