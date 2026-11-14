"""Single configuration location: paths, study window, format mapping, seeds."""
from __future__ import annotations

from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# --- raw data -------------------------------------------------------------
RAW_DIR = ROOT / "data" / "raw"
RAW_ZIP = RAW_DIR / "england_male_json.zip"
RAW_JSON_DIR = RAW_DIR / "england_male_json"
SOURCE_URL = "https://cricsheet.org/downloads/england_male_json.zip"

# --- derived data ---------------------------------------------------------
INTERIM_DIR = ROOT / "data" / "interim"
PROCESSED_DIR = ROOT / "data" / "processed"
TABLES_DIR = ROOT / "outputs" / "tables"
GRAPHML_DIR = ROOT / "outputs" / "graphml"
FIGURES_DIR = ROOT / "outputs" / "figures"
LOGS_DIR = ROOT / "outputs" / "logs"

# --- study definition -----------------------------------------------------
TEAM = "England"
GENDER = "male"
TEAM_TYPE = "international"
# A match qualifies when its *start* date (info.dates[0]) is in this closed
# interval.
DATE_START = date(2020, 1, 1)
DATE_END = date(2026, 10, 29)

# Cricsheet info.match_type -> canonical format label used everywhere else.
FORMAT_MAP: dict[str, str] = {"Test": "Test", "ODI": "ODI", "T20": "T20I", "IT20": "T20I"}
FORMATS: tuple[str, ...] = ("Test", "ODI", "T20I")
FORMAT_SLUG: dict[str, str] = {"Test": "test", "ODI": "odi", "T20I": "t20i"}

# --- reproducibility ------------------------------------------------------
RANDOM_SEED = 42
LOUVAIN_RESOLUTION = 1.0
N_RANDOM_GRAPHS = 200  # null-model graphs for the small-world comparison

# Dates in exported tables use DD-MM-YYYY (instructions section 12.1).
DATE_FMT = "%d-%m-%Y"


def ensure_dirs() -> None:
    """Create every output directory used by the pipeline."""
    for d in (INTERIM_DIR, PROCESSED_DIR, TABLES_DIR, GRAPHML_DIR, FIGURES_DIR, LOGS_DIR):
        d.mkdir(parents=True, exist_ok=True)
