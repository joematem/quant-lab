from pathlib import Path

import pandas as pd
import pytest

from quantlab.decision_gate import (
    DECISION_APPROVE_FOR_PAPER_TRADING,
    DECISION_CONTINUE_RESEARCH,
    DECISION_REJECT,
    build_strategy_decision,
    write_strategy_decision_json,
    write_strategy_decision_markdown,
)


def sample_walk_forward_summary() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ticker": ["AAPL", "MSFT"],
            "mean_test_sharpe_ratio": [0.8, 0.2],
            "positive_return_rate": [0.7, 0.4],
        }
    )


def sample_transaction_cost_stress() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ticker": ["AAPL", "MSFT", "AAPL", "MSFT"],
            "transaction_cost_bps": [5.0, 5.0, 50.0, 50.0],
            "sharpe_ratio": [0.8, 0.6, 0.4, 0.3],
        }
    )


def monte_carlo_summary(
    p05_sharpe: float = 0.1,
    p50_sharpe: float = 0.8,
    positive_probability: float = 0.8,
    negative_probability: float = 0.2,
    drawdown_probability: float = 0.2,
) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ticker": ["equal_weight_sma_monte_carlo"],
            "sharpe_ratio_p05": [p05_sharpe],
            "sharpe_ratio_p50": [p50_sharpe],
            "probability_positive_return": [positive_probability],
            "probability_negative_return": [negative_probability],
            "probability_drawdown_worse_than_30pct": [drawdown_probability],
        }
    )


def test_build_strategy_decision_approves_when_all_checks_pass():
    decision = build_strategy_decision(
        walk_forward_summary=sample_walk_forward_summary(),
        monte_carlo_summary=monte_carlo_summary(),
        transaction_cost_stress=sample_transaction_cost_stress(),
    )

    assert decision["decision"] == DECISION_APPROVE_FOR_PAPER_TRADING
    assert decision["paper_trading_allowed"] is True
    assert decision["live_trading_allowed"] is False


def test_build_strategy_decision_continues_research_when_drawdown_too_high():
    decision = build_strategy_decision(
        walk_forward_summary=sample_walk_forward_summary(),
        monte_carlo_summary=monte_carlo_summary(drawdown_probability=0.54),
        transaction_cost_stress=sample_transaction_cost_stress(),
    )

    assert decision["decision"] == DECISION_CONTINUE_RESEARCH
    assert decision["paper_trading_allowed"] is False
    assert "monte_carlo_drawdown_risk_ok" in decision["paper_trading_blockers"]


def test_build_strategy_decision_rejects_when_median_sharpe_not_positive():
    decision = build_strategy_decision(
        walk_forward_summary=sample_walk_forward_summary(),
        monte_carlo_summary=monte_carlo_summary(p50_sharpe=-0.1),
        transaction_cost_stress=sample_transaction_cost_stress(),
    )

    assert decision["decision"] == DECISION_REJECT
    assert decision["paper_trading_allowed"] is False
    assert decision["rejection_reasons"]


def test_build_strategy_decision_rejects_missing_columns():
    bad_data = pd.DataFrame({"ticker": ["AAPL"]})

    with pytest.raises(ValueError, match="Missing required columns"):
        build_strategy_decision(
            walk_forward_summary=bad_data,
            monte_carlo_summary=monte_carlo_summary(),
            transaction_cost_stress=sample_transaction_cost_stress(),
        )


def test_write_strategy_decision_outputs_files(tmp_path: Path):
    decision = build_strategy_decision(
        walk_forward_summary=sample_walk_forward_summary(),
        monte_carlo_summary=monte_carlo_summary(drawdown_probability=0.54),
        transaction_cost_stress=sample_transaction_cost_stress(),
    )

    json_path = write_strategy_decision_json(
        decision,
        tmp_path / "decision.json",
    )
    markdown_path = write_strategy_decision_markdown(
        decision,
        tmp_path / "decision.md",
    )

    assert json_path.exists()
    assert markdown_path.exists()
    assert "CONTINUE_RESEARCH" in markdown_path.read_text()
