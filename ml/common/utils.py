"""Shared utilities for Credix ML subsystem."""

import json
import logging
from pathlib import Path
from typing import Any, Dict
import numpy as np


def setup_logger(name: str = "credix_ml", level: int = logging.INFO) -> logging.Logger:
    """Configures and returns a standardized logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(level)
    return logger


class NumpyEncoder(json.JSONEncoder):
    """Custom JSON encoder converting NumPy types into native Python types."""

    def default(self, obj: Any) -> Any:
        if isinstance(obj, (np.integer, np.int64, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.bool_, bool)):
            return bool(obj)
        return super().default(obj)


def save_json(data: Dict[str, Any], filepath: Path) -> None:
    """Saves a dictionary as formatted JSON using the NumpyEncoder."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, cls=NumpyEncoder)


def load_json(filepath: Path) -> Dict[str, Any]:
    """Loads a JSON file as a dictionary."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

