from __future__ import annotations

from pathlib import Path

import yaml
from typer.testing import CliRunner

from helixscope.cli import cli_app
from helixscope.skill.install import install_local_skill


def test_install_local_skill_creates_symlink_and_config(tmp_path: Path) -> None:
    repo = Path(__file__).resolve().parents[2]
    codex_home = tmp_path / "codex"

    result = install_local_skill(
        codex_home=codex_home,
        repo_root=repo,
        env_name="HelixScope_env",
    )

    assert result.status == "created"
    assert result.target.is_symlink()
    assert result.target.resolve() == (repo / "skills" / "helixscope").resolve()

    config = yaml.safe_load(result.config_path.read_text(encoding="utf-8"))
    assert config["repo_root"] == str(repo)
    assert config["bootstrap_env_name"] == "HelixScope_env"
    assert config["python_env"] == ".venv"
    assert config["helixscope_cli"] == ".venv/bin/helixscope"

    second = install_local_skill(
        codex_home=codex_home,
        repo_root=repo,
        env_name="HelixScope_env",
    )
    assert second.status == "already_linked"


def test_cli_skill_install_local_uses_symlink(tmp_path: Path) -> None:
    repo = Path(__file__).resolve().parents[2]
    codex_home = tmp_path / "codex"

    result = CliRunner().invoke(
        cli_app,
        [
            "skill",
            "install-local",
            "--codex-home",
            str(codex_home),
            "--repo-root",
            str(repo),
        ],
    )

    assert result.exit_code == 0
    assert "created" in result.output
    assert (codex_home / "skills" / "helixscope").is_symlink()
    assert (codex_home / "helixscope" / "config.yaml").exists()
