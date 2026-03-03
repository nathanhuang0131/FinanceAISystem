from pathlib import Path


def test_requirements_and_readme_exist() -> None:
    assert Path("requirements.txt").exists()
    assert Path("README.md").exists()
