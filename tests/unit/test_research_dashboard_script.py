from pathlib import Path


def test_research_dashboard_script_exists():
    script_path = Path("scripts/create_research_dashboard.py")

    assert script_path.exists()


def test_research_dashboard_script_references_dashboard_output():
    script_path = Path("scripts/create_research_dashboard.py")
    text = script_path.read_text()

    assert "research_dashboard.md" in text
    assert "experiment_manifest.json" in text
