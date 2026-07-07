from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from helixscope.cli import cli_app
from helixscope.spec.loaders import load_mission_spec


def test_cli_validate_example() -> None:
    repo = Path(__file__).resolve().parents[2]
    result = CliRunner().invoke(
        cli_app,
        ["validate", str(repo / "examples" / "minimal_locus_probe.yaml")],
    )
    assert result.exit_code == 0
    assert "valid" in result.output


def test_cli_demo(tmp_path: Path) -> None:
    result = CliRunner().invoke(cli_app, ["demo", "--out", str(tmp_path)])
    assert result.exit_code == 0
    assert (tmp_path / "locus_probe.png").exists()
    assert (tmp_path / "report.json").exists()


def test_cli_import_bed_motifs(tmp_path: Path) -> None:
    bed = tmp_path / "motifs.bed"
    out = tmp_path / "bed_motif_spec.yaml"
    bed.write_text(
        "\n".join(
            [
                "chr7\t100\t121\tFOXA2(MA0047.4)\t14.2\t+",
                "chr8\t100\t121\tOTHER\t1\t+",
            ]
        ),
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        cli_app,
        [
            "motifs",
            "import-bed",
            str(bed),
            "--locus",
            "chr7:90-190",
            "--genome",
            "hg38",
            "--out",
            str(out),
            "--title",
            "Imported BED motifs",
        ],
    )

    assert result.exit_code == 0
    assert "imported 1 motif" in result.output
    spec = load_mission_spec(out)
    assert spec.title == "Imported BED motifs"
    assert spec.motifs[0].chrom == "chr7"
    assert spec.motifs[0].label == "FOXA2(MA0047.4)"
