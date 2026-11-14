"""Logging helper: every stage logs to console and to outputs/logs/<stage>.log."""
from __future__ import annotations

import logging

from . import config


def get_logger(stage: str) -> logging.Logger:
    """Return a logger writing to stdout and ``outputs/logs/<stage>.log``."""
    config.ensure_dirs()
    logger = logging.getLogger(f"batnet.{stage}")
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    fh = logging.FileHandler(config.LOGS_DIR / f"{stage}.log", mode="w", encoding="utf-8")
    fh.setFormatter(fmt)
    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    logger.addHandler(fh)
    logger.addHandler(sh)
    return logger
