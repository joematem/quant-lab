from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def project_path(*parts: str) -> Path:
    """Return an absolute path inside the project."""
    return PROJECT_ROOT.joinpath(*parts)
