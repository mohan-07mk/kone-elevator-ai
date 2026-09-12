"""Dataset loader — downloads and caches the AI4I 2020 Predictive Maintenance Dataset."""

from __future__ import annotations

import csv
import io
import logging
import os
import zipfile
from pathlib import Path
from typing import Any

import httpx

logger = logging.getLogger("elevator_ai.dataset")

DATASET_URL = "https://archive.ics.uci.edu/static/public/601/ai4i+2020+predictive+maintenance+dataset.zip"
CACHE_DIR = Path(__file__).resolve().parent.parent.parent / "datasets" / "cache"
CSV_FILENAME = "ai4i2020.csv"

# Column names from the dataset
COLUMNS = [
    "UDI", "Product ID", "Type",
    "Air temperature [K]", "Process temperature [K]",
    "Rotational speed [rpm]", "Torque [Nm]", "Tool wear [min]",
    "Machine failure", "TWF", "HDF", "PWF", "OSF", "RNF",
]


class DatasetLoadError(Exception):
    """Raised when dataset cannot be loaded."""


def _ensure_cache_dir() -> Path:
    """Create cache directory if it does not exist."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR


def _download_dataset() -> Path:
    """Download the AI4I dataset ZIP and extract the CSV."""
    cache = _ensure_cache_dir()
    csv_path = cache / CSV_FILENAME

    if csv_path.exists():
        logger.info("Dataset already cached at %s", csv_path)
        return csv_path

    logger.info("Downloading AI4I 2020 dataset from UCI...")
    try:
        with httpx.Client(timeout=60.0, follow_redirects=True) as client:
            resp = client.get(DATASET_URL)
            resp.raise_for_status()
    except Exception as exc:
        raise DatasetLoadError(f"Failed to download dataset: {exc}") from exc

    # Extract CSV from ZIP
    try:
        with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
            # Find the CSV file inside the ZIP
            csv_names = [n for n in zf.namelist() if n.endswith(".csv")]
            if not csv_names:
                raise DatasetLoadError("No CSV file found in dataset ZIP")

            csv_name = csv_names[0]
            logger.info("Extracting %s from ZIP", csv_name)
            content = zf.read(csv_name)
            csv_path.write_bytes(content)
    except zipfile.BadZipFile as exc:
        raise DatasetLoadError(f"Invalid ZIP file: {exc}") from exc

    logger.info("Dataset cached at %s (%d bytes)", csv_path, csv_path.stat().st_size)
    return csv_path


def load_raw_dataset() -> list[dict[str, Any]]:
    """Load the raw dataset as a list of dictionaries.

    Returns a list of dicts with original column names as keys.
    """
    csv_path = _download_dataset()

    records: list[dict[str, Any]] = []
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            record = {}
            for key, value in row.items():
                key = key.strip().lstrip("\ufeff")
                # Parse numeric fields
                if key in ("UDI", "Machine failure", "TWF", "HDF", "PWF", "OSF", "RNF"):
                    record[key] = int(value)
                elif key in ("Air temperature [K]", "Process temperature [K]",
                             "Rotational speed [rpm]", "Torque [Nm]", "Tool wear [min]"):
                    record[key] = float(value)
                else:
                    record[key] = value
            records.append(record)

    logger.info("Loaded %d raw records from dataset", len(records))
    return records


def validate_dataset(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Validate dataset records — check types, ranges, missing values.

    Returns only valid records. Logs warnings for dropped records.
    """
    valid = []
    dropped = 0

    for i, rec in enumerate(records):
        try:
            # Required fields present
            assert "Air temperature [K]" in rec, "Missing air temperature"
            assert "Process temperature [K]" in rec, "Missing process temperature"
            assert "Rotational speed [rpm]" in rec, "Missing rotational speed"
            assert "Torque [Nm]" in rec, "Missing torque"
            assert "Tool wear [min]" in rec, "Missing tool wear"

            # Range checks
            air_t = rec["Air temperature [K]"]
            assert 280 <= air_t <= 320, f"Air temp out of range: {air_t}"

            proc_t = rec["Process temperature [K]"]
            assert 290 <= proc_t <= 330, f"Process temp out of range: {proc_t}"

            rpm = rec["Rotational speed [rpm]"]
            assert 500 <= rpm <= 3000, f"RPM out of range: {rpm}"

            torque = rec["Torque [Nm]"]
            assert 0 <= torque <= 100, f"Torque out of range: {torque}"

            valid.append(rec)
        except Exception as e:
            dropped += 1
            if dropped <= 5:
                logger.warning("Record %d dropped: %s", i, e)

    if dropped > 5:
        logger.warning("... and %d more records dropped", dropped - 5)

    logger.info("Validation: %d valid / %d dropped / %d total",
                len(valid), dropped, len(records))
    return valid
