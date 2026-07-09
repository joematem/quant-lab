from pathlib import Path

import pytest

from quantlab.config import load_sma_experiment_config


def test_load_sma_experiment_config(tmp_path: Path):
    config_path = tmp_path / "sma_experiment.yaml"

    config_path.write_text(
        """
sma_experiment:
  tickers:
    - AAPL
    - MSFT
  data:
    start: "2015-01-01"
  strategy:
    short_window: 20
    long_window: 50
    transaction_cost_bps: 5.0
  validation:
    train_years: 3
    test_years: 1
""",
        encoding="utf-8",
    )

    config = load_sma_experiment_config(config_path)

    assert config.tickers == ["AAPL", "MSFT"]
    assert config.start == "2015-01-01"
    assert config.short_window == 20
    assert config.long_window == 50
    assert config.transaction_cost_bps == 5.0
    assert config.train_years == 3
    assert config.test_years == 1


def test_load_sma_experiment_config_rejects_missing_section(tmp_path: Path):
    config_path = tmp_path / "bad.yaml"
    config_path.write_text("bad: true", encoding="utf-8")

    with pytest.raises(ValueError, match="Missing 'sma_experiment'"):
        load_sma_experiment_config(config_path)


def test_load_sma_experiment_config_rejects_missing_file():
    with pytest.raises(FileNotFoundError):
        load_sma_experiment_config("configs/does_not_exist.yaml")
