from pathlib import Path

from quantlab.experiment_manifest import (
    build_experiment_manifest,
    file_sha256,
    write_experiment_manifest,
)


def test_file_sha256_returns_hash(tmp_path: Path):
    test_file = tmp_path / "sample.txt"
    test_file.write_text("hello")

    result = file_sha256(test_file)

    assert len(result) == 64


def test_build_experiment_manifest_includes_outputs(tmp_path: Path):
    output_file = tmp_path / "output.csv"
    output_file.write_text("ticker,total_return\nAAPL,0.1\n")

    manifest = build_experiment_manifest(
        experiment_name="test_experiment",
        parameters={"ticker": "AAPL"},
        output_files=[output_file],
    )

    assert manifest["experiment_name"] == "test_experiment"
    assert manifest["parameters"]["ticker"] == "AAPL"
    assert manifest["outputs"][0]["path"] == str(output_file)
    assert "sha256" in manifest["outputs"][0]
    assert "git_commit" in manifest


def test_build_experiment_manifest_marks_missing_outputs(tmp_path: Path):
    missing_file = tmp_path / "missing.csv"

    manifest = build_experiment_manifest(
        experiment_name="test_experiment",
        parameters={},
        output_files=[missing_file],
    )

    assert manifest["outputs"][0]["missing"] is True


def test_write_experiment_manifest_creates_json_file(tmp_path: Path):
    output_path = tmp_path / "manifest.json"
    manifest = {
        "experiment_name": "test",
        "parameters": {},
        "outputs": [],
    }

    result = write_experiment_manifest(manifest, output_path)

    assert result.exists()
    assert '"experiment_name": "test"' in result.read_text()
