import json
from pathlib import Path

import pytest

from quantlab.research_dashboard import (
    create_research_dashboard,
    format_output_status,
    load_manifest,
)


def sample_manifest() -> dict:
    return {
        "experiment_name": "sma_crossover_research_experiment",
        "created_at_utc": "2026-07-10T00:00:00+00:00",
        "git_commit": "abc123",
        "git_status_short": "",
        "parameters": {
            "tickers": ["AAPL", "MSFT", "NVDA"],
            "short_window": 20,
            "long_window": 50,
        },
        "outputs": [],
    }


def test_load_manifest_reads_json(tmp_path: Path):
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(sample_manifest()))

    result = load_manifest(manifest_path)

    assert result["experiment_name"] == "sma_crossover_research_experiment"


def test_load_manifest_rejects_missing_file(tmp_path: Path):
    with pytest.raises(FileNotFoundError, match="Missing manifest file"):
        load_manifest(tmp_path / "missing.json")


def test_format_output_status_reports_available(tmp_path: Path):
    file_path = tmp_path / "output.csv"
    file_path.write_text("data")

    assert format_output_status(file_path) == "available"


def test_format_output_status_reports_missing(tmp_path: Path):
    assert format_output_status(tmp_path / "missing.csv") == "missing"


def test_create_research_dashboard_creates_markdown(tmp_path: Path):
    manifest_path = tmp_path / "manifest.json"
    output_path = tmp_path / "research_dashboard.md"
    manifest_path.write_text(json.dumps(sample_manifest()))

    result = create_research_dashboard(
        output_path=output_path,
        manifest_path=manifest_path,
    )

    text = result.read_text()

    assert result.exists()
    assert "Quant Lab Research Dashboard" in text
    assert "sma_crossover_research_experiment" in text
    assert "Strategy decision gate" in text
    assert "Live trading remains out of scope" in text
