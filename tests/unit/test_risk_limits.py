from pathlib import Path

import pandas as pd
import pytest

from quantlab.risk_limits import (
    evaluate_research_risk_limits,
    write_risk_limits_json,
    write_risk_limits_markdown,
)


def sample_portfolio_summary() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ticker": ["equal_weight_buy_hold", "equal_weight_sma"],
            "max_drawdown": [-0.50, -0.20],
            "sharpe_ratio": [1.20, 0.80],
        }
    )


def sample_monte_carlo_summary(
    drawdown_probability: float = 0.20,
    median_drawdown: float = -0.20,
    tail_drawdown: float = -0.35,
) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ticker": ["equal_weight_sma_monte_carlo"],
            "max_drawdown_p50": [median_drawdown],
            "max_drawdown_p05": [tail_drawdown],
            "probability_drawdown_worse_than_30pct": [drawdown_probability],
        }
    )


def sample_decision_gate(
    paper_trading_allowed: bool = True,
    live_trading_allowed: bool = False,
) -> dict:
    return {
        "decision": (
            "APPROVE_FOR_PAPER_TRADING"
            if paper_trading_allowed
            else "CONTINUE_RESEARCH"
        ),
        "paper_trading_allowed": paper_trading_allowed,
        "live_trading_allowed": live_trading_allowed,
    }


def test_evaluate_research_risk_limits_passes_when_all_checks_pass():
    report = evaluate_research_risk_limits(
        portfolio_summary=sample_portfolio_summary(),
        monte_carlo_summary=sample_monte_carlo_summary(),
        decision_gate=sample_decision_gate(),
    )

    assert report["research_status"] == "RISK_LIMITS_PASS_FOR_PAPER_REVIEW"
    assert report["paper_trading_allowed"] is True
    assert report["live_trading_allowed"] is False
    assert report["observed"]["portfolio_ticker"] == "equal_weight_sma"


def test_evaluate_research_risk_limits_fails_when_decision_gate_blocks_paper():
    report = evaluate_research_risk_limits(
        portfolio_summary=sample_portfolio_summary(),
        monte_carlo_summary=sample_monte_carlo_summary(drawdown_probability=0.54),
        decision_gate=sample_decision_gate(paper_trading_allowed=False),
    )

    assert report["research_status"] == "RISK_LIMITS_FAIL_CONTINUE_RESEARCH"
    assert report["paper_trading_allowed"] is False
    assert "decision_gate_allows_paper_trading" in report["failed_checks"]


def test_evaluate_research_risk_limits_rejects_missing_columns():
    bad_data = pd.DataFrame({"ticker": ["equal_weight_sma"]})

    with pytest.raises(ValueError, match="Missing required columns"):
        evaluate_research_risk_limits(
            portfolio_summary=bad_data,
            monte_carlo_summary=sample_monte_carlo_summary(),
            decision_gate=sample_decision_gate(),
        )


def test_write_risk_limits_outputs_files(tmp_path: Path):
    report = evaluate_research_risk_limits(
        portfolio_summary=sample_portfolio_summary(),
        monte_carlo_summary=sample_monte_carlo_summary(),
        decision_gate=sample_decision_gate(),
    )

    json_path = write_risk_limits_json(report, tmp_path / "risk.json")
    markdown_path = write_risk_limits_markdown(report, tmp_path / "risk.md")

    assert json_path.exists()
    assert markdown_path.exists()
    assert "Research Risk Limits Report" in markdown_path.read_text()


def test_evaluate_research_risk_limits_rejects_missing_strategy_ticker():
    with pytest.raises(ValueError, match="Strategy ticker not found"):
        evaluate_research_risk_limits(
            portfolio_summary=sample_portfolio_summary(),
            monte_carlo_summary=sample_monte_carlo_summary(),
            decision_gate=sample_decision_gate(),
            strategy_ticker="missing_strategy",
        )
