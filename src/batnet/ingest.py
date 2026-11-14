"""Stage 1 - source inspection: archive extraction, manifest, JSON loading.

Raw data are never modified. The zip archive is the immutable source; the
extracted folder is a disposable cache that is re-created from the zip.
"""
from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path
from typing import Any, Iterator

import pandas as pd

from . import config


def sha256_of(path: Path, chunk: int = 1 << 20) -> str:
    """SHA-256 hex digest of a file."""
    h = hashlib.sha256()
    with path.open("rb") as fh:
        while block := fh.read(chunk):
            h.update(block)
    return h.hexdigest()


def ensure_extracted(zip_path: Path = config.RAW_ZIP, out_dir: Path = config.RAW_JSON_DIR) -> Path:
    """Extract the archive if the extracted folder is missing; return the folder."""
    if not out_dir.exists() or not any(out_dir.glob("*.json")):
        if not zip_path.exists():
            raise FileNotFoundError(
                f"{zip_path} not found. Download it from {config.SOURCE_URL} into data/raw/."
            )
        out_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(out_dir)
    return out_dir


def iter_match_files(json_dir: Path = config.RAW_JSON_DIR) -> Iterator[Path]:
    """Yield match JSON files in a stable (sorted) order."""
    yield from sorted(json_dir.glob("*.json"))


def load_match(path: Path) -> dict[str, Any]:
    """Load one Cricsheet match file."""
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def build_manifest(json_dir: Path = config.RAW_JSON_DIR) -> pd.DataFrame:
    """One row per source file: name, size, checksum and schema metadata.

    Unreadable files are kept in the manifest with ``readable = False`` so that
    nothing is skipped silently.
    """
    rows = []
    for path in iter_match_files(json_dir):
        row: dict[str, Any] = {
            "filename": path.name,
            "bytes": path.stat().st_size,
            "sha256": sha256_of(path),
            "readable": True,
            "data_version": "",
            "created": "",
            "revision": -1,
        }
        try:
            meta = load_match(path).get("meta", {})
            row["data_version"] = str(meta.get("data_version", ""))
            row["created"] = str(meta.get("created", ""))
            row["revision"] = int(meta.get("revision", -1))
        except (json.JSONDecodeError, OSError, ValueError):
            row["readable"] = False
        rows.append(row)
    return pd.DataFrame(rows)
