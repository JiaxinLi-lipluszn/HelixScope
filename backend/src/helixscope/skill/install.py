from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import yaml

DEFAULT_ENV_NAME = "HelixScope_env"
DEFAULT_PYTHON_ENV = ".venv"
DEFAULT_HELIXSCOPE_CLI = ".venv/bin/helixscope"
CONFIG_VERSION = 1


@dataclass(frozen=True)
class SkillInstallResult:
    source: Path
    target: Path
    config_path: Path
    repo_root: Path
    env_name: str
    status: Literal["created", "already_linked", "replaced"]


def default_codex_home() -> Path:
    configured = os.environ.get("CODEX_HOME")
    if configured:
        return Path(configured).expanduser()
    return Path.home() / ".codex"


def discover_repo_root(start: Path | None = None) -> Path:
    cursor = (start or Path(__file__)).resolve()
    if cursor.is_file():
        cursor = cursor.parent
    for parent in (cursor, *cursor.parents):
        if (parent / "pyproject.toml").exists() and (
            parent / "skills" / "helixscope" / "SKILL.md"
        ).exists():
            return parent
    raise FileNotFoundError("Could not find HelixScope repo root from current install.")


def install_local_skill(
    *,
    codex_home: Path | None = None,
    repo_root: Path | None = None,
    env_name: str = DEFAULT_ENV_NAME,
    replace: bool = False,
) -> SkillInstallResult:
    resolved_codex_home = (codex_home or default_codex_home()).expanduser()
    resolved_repo_root = discover_repo_root(repo_root)
    source = resolved_repo_root / "skills" / "helixscope"
    if not (source / "SKILL.md").exists():
        raise FileNotFoundError(f"HelixScope skill source is missing: {source}")

    skills_dir = resolved_codex_home / "skills"
    target = skills_dir / "helixscope"
    source_resolved = source.resolve()

    skills_dir.mkdir(parents=True, exist_ok=True)
    status: Literal["created", "already_linked", "replaced"] = "created"

    if target.exists() or target.is_symlink():
        if not target.is_symlink():
            raise FileExistsError(
                f"Skill target already exists and is not a symlink: {target}. "
                "Move it aside before installing the editable HelixScope skill."
            )

        target_resolved = target.resolve(strict=False)
        if target_resolved == source_resolved:
            status = "already_linked"
        elif replace:
            target.unlink()
            target.symlink_to(source_resolved, target_is_directory=True)
            status = "replaced"
        else:
            raise FileExistsError(
                f"Skill target points to {target_resolved}, not {source_resolved}. "
                "Use --replace to update an existing symlink."
            )
    else:
        target.symlink_to(source_resolved, target_is_directory=True)

    config_path = write_skill_config(
        codex_home=resolved_codex_home,
        repo_root=resolved_repo_root,
        source=source_resolved,
        target=target,
        env_name=env_name,
    )
    return SkillInstallResult(
        source=source_resolved,
        target=target,
        config_path=config_path,
        repo_root=resolved_repo_root,
        env_name=env_name,
        status=status,
    )


def write_skill_config(
    *,
    codex_home: Path,
    repo_root: Path,
    source: Path,
    target: Path,
    env_name: str,
) -> Path:
    config_dir = codex_home / "helixscope"
    config_dir.mkdir(parents=True, exist_ok=True)
    config_path = config_dir / "config.yaml"
    payload = {
        "version": CONFIG_VERSION,
        "repo_root": str(repo_root),
        "skill_source": str(source),
        "skill_link": str(target),
        "bootstrap_env_name": env_name,
        "python_env": DEFAULT_PYTHON_ENV,
        "helixscope_cli": DEFAULT_HELIXSCOPE_CLI,
        "uv_python_downloads": "never",
    }
    config_path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return config_path
