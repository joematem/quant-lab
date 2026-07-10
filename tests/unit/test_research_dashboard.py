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


def test_load_optional_json_returns_none_for_missing_file(tmp_path: Path):
    from quantlab.research_dashboard import load_optional_json

    assert load_optional_json(tmp_path / "missing.json") is None


def test_research_dashboard_includes_decision_and_risk_status(tmp_path: Path):
    manifest_path = tmp_path / "manifest.json"
    output_path = tmp_path / "research_dashboard.md"

    manifest_path.write_text(json.dumps(sample_manifest()))

    reports_dir = Path("reports/backtests")
    reports_dir.mkdir(parents=True, exist_ok=True)

    decision_path = reports_dir / "strategy_decision_gate.json"
    risk_path = reports_dir / "risk_limits_report.json"

    original_decision = decision_path.read_text() if decision_path.exists() else None
    original_risk = risk_path.read_text() if risk_path.exists() else None

    try:
        decision_path.write_text(
            json.dumps(
                {
                    "decision": "CONTINUE_RESEARCH",
                    "paper_trading_allowed": False,
                    "live_trading_allowed": False,
                }
            )
        )
        risk_path.write_text(
            json.dumps(
                {
                    "research_status": "RISK_LIMITS_FAIL_CONTINUE_RESEARCH",
                    "paper_trading_allowed": False,
                    "live_trading_allowed": False,
                }
            )
        )

        result = create_research_dashboard(
            output_path=output_path,
            manifest_path=manifest_path,
        )

        text = result.read_text()

        assert "CONTINUE_RESEARCH" in text
        assert "RISK_LIMITS_FAIL_CONTINUE_RESEARCH" in text
        assert "MT5 paper-trading prototype | blocked" in text
    finally:
        if original_decision is None:
            decision_path.unlink(missing_ok=True)
        else:
            decision_path.write_text(original_decision)

        if original_risk is None:
            risk_path.unlink(missing_ok=True)
        else:
            risk_path.write_text(original_risk)
