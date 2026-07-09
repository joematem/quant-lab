from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from quantlab.utils.paths import project_path


@dataclass(frozen=True)
class SMAExperimentConfig:
    tickers: list[str]
    start: str
    short_window: int
    long_window: int
    train_years: int
    test_years: int
    transaction_cost_bps: float


def _resolve_config_path(config_path: str | Path) -> Path:
    path = Path(config_path)

    if path.is_absolute():
        return path

    return project_path(str(path))


def load_sma_experiment_config(config_path: str | Path) -> SMAExperimentConfig:
    """Load SMA experiment settings from YAML."""
    resolved_path = _resolve_config_path(config_path)

    if not resolved_path.exists():
        raise FileNotFoundError(f"Config file not found: {resolved_path}")

    with resolved_path.open("r", encoding="utf-8") as file:
        raw_config: dict[str, Any] = yaml.safe_load(file) or {}

    experiment = raw_config.get("sma_experiment")
    if not isinstance(experiment, dict):
        raise ValueError("Missing 'sma_experiment' section in config file.")

    tickers = experiment.get("tickers")
    if not tickers:
        raise ValueError("Config must contain at least one ticker.")

    data = experiment.get("data", {})
    strategy = experiment.get("strategy", {})
    validation = experiment.get("validation", {})

    return SMAExperimentConfig(
        tickers=[str(ticker).upper() for ticker in tickers],
        start=str(data.get("start", "2015-01-01")),
        short_window=int(strategy.get("short_window", 20)),
        long_window=int(strategy.get("long_window", 50)),
        transaction_cost_bps=float(strategy.get("transaction_cost_bps", 5.0)),
        train_years=int(validation.get("train_years", 3)),
        test_years=int(validation.get("test_years", 1)),
    )
