from pathlib import Path


def test_full_experiment_runner_includes_portfolio_steps():
    script_path = Path("scripts/run_full_sma_research_experiment.py")
    text = script_path.read_text()

    assert "scripts/run_equal_weight_portfolio_backtest.py" in text
    assert "scripts/create_portfolio_charts.py" in text


def test_makefile_includes_portfolio_target():
    makefile = Path("Makefile")
    text = makefile.read_text()

    assert "portfolio:" in text
    assert "scripts/run_equal_weight_portfolio_backtest.py" in text
    assert "scripts/create_portfolio_charts.py" in text
