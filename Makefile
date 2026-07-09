.PHONY: test lint format check experiment report charts sync-check clean-pyc

test:
	uv run pytest

lint:
	uv run ruff check .

format:
	uv run ruff check . --fix
	uv run black .

check:
	uv run pytest
	uv run ruff check .
	uv run black --check .

experiment:
	uv run python scripts/run_configured_sma_experiment.py configs/sma_experiment.yaml

report:
	uv run python scripts/create_sma_research_report.py AAPL MSFT NVDA --train-years 3 --test-years 1 --transaction-cost-bps 5

charts:
	uv run python scripts/create_walk_forward_charts.py AAPL MSFT NVDA --train-years 3 --test-years 1 --transaction-cost-bps 5

portfolio:
	uv run python scripts/run_equal_weight_portfolio_backtest.py
	uv run python scripts/create_portfolio_charts.py

risk:
	uv run python scripts/run_portfolio_volatility_targeting.py --target-annual-volatility 0.15 --lookback-days 63 --max-leverage 1.0
	uv run python scripts/create_volatility_targeting_charts.py

portfolio-comparison:
	uv run python scripts/create_portfolio_strategy_comparison.py

sync-check:
	git status
	git branch -vv
	git log --oneline --decorate -5

clean-pyc:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -prune -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -prune -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -prune -exec rm -rf {} +
