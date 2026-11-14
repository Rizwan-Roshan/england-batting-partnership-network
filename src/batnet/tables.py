"""CSV input/output with one date convention (DD-MM-YYYY, UTF-8)."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from . import config

DATE_COLUMNS = ("match_date", "start_date", "end_date", "first_date", "last_date")
ID_COLUMNS = ("match_id", "player_id", "player_1_id", "player_2_id", "start_delivery_id",
              "end_delivery_id", "delivery_id")


def write_csv(df: pd.DataFrame, path: Path) -> None:
    """Write a table; date columns are formatted DD-MM-YYYY."""
    out = df.copy()
    for col in DATE_COLUMNS:
        if col in out.columns:
            out[col] = pd.to_datetime(out[col]).dt.strftime(config.DATE_FMT)
    path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(path, index=False, encoding="utf-8")


def read_csv(path: Path) -> pd.DataFrame:
    """Read a table written by :func:`write_csv`; dates become ``datetime.date``."""
    head = pd.read_csv(path, nrows=0).columns
    df = pd.read_csv(path, dtype={c: str for c in ID_COLUMNS if c in head}, keep_default_na=True)
    for col in DATE_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], format=config.DATE_FMT).dt.date
    return df
