from __future__ import annotations

import json

from typer.testing import CliRunner

from helixscope.cli import cli_app
from helixscope.io.motifs.fimo_scanner import check_fimo


def test_check_fimo_reports_missing_when_path_is_empty(monkeypatch) -> None:
    monkeypatch.setenv("PATH", "")

    status = check_fimo()

    assert status.available is False
    assert status.executable is None
    assert "optional" in status.install_hint


def test_cli_check_fimo_json_reports_availability(monkeypatch) -> None:
    monkeypatch.setenv("PATH", "")

    result = CliRunner().invoke(cli_app, ["motifs", "check-fimo", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["available"] is False
    assert payload["executable"] is None
