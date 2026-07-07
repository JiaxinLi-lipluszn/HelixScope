from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from helixscope.spec.models import MissionSpec


def load_mapping(path: Path) -> dict[str, Any]:
    suffix = path.suffix.lower()
    text = path.read_text(encoding="utf-8")
    if suffix == ".json":
        data = json.loads(text)
    elif suffix in {".yaml", ".yml"}:
        data = yaml.safe_load(text)
    else:
        raise ValueError(f"Unsupported spec extension: {path.suffix}")
    if not isinstance(data, dict):
        raise ValueError(f"MissionSpec must be a mapping: {path}")
    return data


def load_mission_spec(path: Path) -> MissionSpec:
    return MissionSpec.model_validate(load_mapping(path))


def write_mission_spec(spec: MissionSpec, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = spec.model_dump(mode="json", exclude_none=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
