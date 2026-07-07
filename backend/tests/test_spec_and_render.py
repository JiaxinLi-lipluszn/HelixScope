from __future__ import annotations

from pathlib import Path

from helixscope.render.static import render_report
from helixscope.spec.loaders import load_mission_spec
from helixscope.spec.models import demo_mission_spec


def test_load_minimal_example() -> None:
    repo = Path(__file__).resolve().parents[2]
    spec = load_mission_spec(repo / "examples" / "minimal_locus_probe.yaml")
    assert spec.report_type == "locus_probe"
    assert spec.loci[0].chrom == "chr7"
    assert len(spec.tracks) == 3
    assert spec.motifs[0].score == 12.4
    assert spec.motifs[0].source == "synthetic_fimo_demo"


def test_render_demo_outputs(tmp_path: Path) -> None:
    result = render_report(demo_mission_spec(), tmp_path, {"png", "html"})
    png = tmp_path / "locus_probe.png"
    html = tmp_path / "locus_probe.html"
    assert result.report_json.exists()
    assert png.exists()
    assert png.stat().st_size > 1000
    assert html.exists()
    assert "HelixScope synthetic LocusProbe demo" in html.read_text(encoding="utf-8")


def test_render_crowded_motif_example(tmp_path: Path) -> None:
    repo = Path(__file__).resolve().parents[2]
    spec = load_mission_spec(repo / "examples" / "motif_track_locus_probe.yaml")
    result = render_report(spec, tmp_path, {"png", "html"})
    assert result.report_json.exists()
    assert (tmp_path / "locus_probe.png").stat().st_size > 1000
