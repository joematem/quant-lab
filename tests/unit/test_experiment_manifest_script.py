from pathlib import Path


def test_experiment_manifest_script_exists():
    script_path = Path("scripts/create_experiment_manifest.py")

    assert script_path.exists()


def test_experiment_manifest_script_references_output():
    script_path = Path("scripts/create_experiment_manifest.py")
    text = script_path.read_text()

    assert "experiment_manifest.json" in text
    assert "sma_crossover_research_experiment" in text
