from pathlib import Path

import yaml


def test_pre_commit_config_exists():
    config_path = Path(".pre-commit-config.yaml")

    assert config_path.exists()


def test_pre_commit_config_runs_make_check():
    config_path = Path(".pre-commit-config.yaml")
    config = yaml.safe_load(config_path.read_text())

    hooks = config["repos"][0]["hooks"]

    assert hooks[0]["id"] == "quantlab-check"
    assert hooks[0]["entry"] == "make check"
    assert hooks[0]["pass_filenames"] is False
