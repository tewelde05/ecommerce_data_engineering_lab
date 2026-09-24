from pathlib import Path

import pandas as pd

from src.data_pipeline import (
    add_transformations,
    clean_data,
    engineer_features,
    load_data,
    quality_counts,
)


ROOT = Path(__file__).resolve().parents[1]


def test_raw_file_has_exactly_500_rows_and_required_columns():
    frame = load_data(ROOT / "data" / "ecommerce_transactions_raw.csv")
    assert len(frame) == 500


def test_cleaning_resolves_all_counted_quality_problems():
    raw = load_data(ROOT / "data" / "ecommerce_transactions_raw.csv")
    cleaned = clean_data(raw)
    assert all(value == 0 for value in quality_counts(cleaned).values())
    assert len(cleaned) == 495


def test_features_are_valid():
    raw = load_data(ROOT / "data" / "ecommerce_transactions_raw.csv")
    metadata = pd.read_csv(ROOT / "data" / "city_metadata.csv")
    featured = engineer_features(add_transformations(clean_data(raw), metadata))
    assert featured["revenue"].ge(0).all()
    assert featured["days_since_purchase"].ge(0).all()
    assert featured["province"].notna().all()

