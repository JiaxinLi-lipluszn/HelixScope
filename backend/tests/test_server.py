from __future__ import annotations

from helixscope.server.app import app, demo_metadata, health


def test_health_endpoint() -> None:
    payload = health()
    assert payload["status"] == "ok"
    assert payload["service"] == "helixscope-backend"


def test_demo_metadata_endpoint() -> None:
    payload = demo_metadata()
    assert payload["report_type"] == "locus_probe"


def test_expected_routes_are_registered() -> None:
    paths = {route.path for route in app.routes}
    assert "/health" in paths
    assert "/reports/demo-metadata" in paths
