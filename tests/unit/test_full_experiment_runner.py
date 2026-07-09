from pathlib import Path


def test_full_experiment_runner_exists():
    script_path = Path("scripts/run_full_sma_research_experiment.py")

    assert script_path.exists()
    assert script_path.read_text().count("run_step") >= 5
