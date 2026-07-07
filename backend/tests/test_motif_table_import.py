from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from helixscope.cli import cli_app
from helixscope.io.motifs.table import load_table_motifs, mission_spec_from_table
from helixscope.spec.loaders import load_mission_spec
from helixscope.spec.models import Locus


def test_load_all_motif_csv_preset(tmp_path: Path) -> None:
    table = tmp_path / "all_motif.csv"
    table.write_text(
        "\n".join(
            [
                "Chromosome,Start,End,motif_alt_id,strand,score",
                "chr7,100,121,FOXA2(MA0047.4),+,14.2",
                "chr8,100,121,OTHER,+,1",
            ]
        ),
        encoding="utf-8",
    )

    motifs = load_table_motifs(
        table,
        preset="all-motif",
        locus=Locus(id="target", coord="chr7:90-190"),
        source="unit_test_all_motif",
    )

    assert len(motifs) == 1
    assert motifs[0].label == "FOXA2(MA0047.4)"
    assert motifs[0].start == 100
    assert motifs[0].end == 121
    assert motifs[0].source == "unit_test_all_motif"


def test_generic_table_can_override_one_based_inclusive_coordinates(tmp_path: Path) -> None:
    table = tmp_path / "generic_one_based.tsv"
    table.write_text(
        "\n".join(
            [
                "chrom\tstart\tend\tstrand\tlabel\tscore",
                "chr7\t101\t121\t+\tFOXA2\t8.5",
            ]
        ),
        encoding="utf-8",
    )

    motifs = load_table_motifs(
        table,
        preset="generic",
        coordinate_system="one-based-inclusive",
        locus=Locus(id="target", coord="chr7:90-190"),
    )

    assert len(motifs) == 1
    assert motifs[0].start == 100
    assert motifs[0].end == 121
    assert motifs[0].label == "FOXA2"
    assert motifs[0].score == 8.5


def test_mission_spec_from_table_records_coordinate_caveat(tmp_path: Path) -> None:
    table = tmp_path / "all_motif.csv"
    table.write_text(
        "\n".join(
            [
                "Chromosome,Start,End,motif_alt_id,score,strand",
                "chr7,100,121,FOXA2(MA0047.4),14.2,+",
            ]
        ),
        encoding="utf-8",
    )

    spec = mission_spec_from_table(
        table,
        genome="hg38",
        locus=Locus(id="target", coord="chr7:90-190"),
        preset="all-motif",
    )

    assert len(spec.motifs) == 1
    assert spec.normalization.policy == "annotation_only"
    assert "zero-based-half-open" in spec.normalization.caveats[1]


def test_cli_import_table(tmp_path: Path) -> None:
    table = tmp_path / "all_motif.csv"
    out = tmp_path / "spec.yaml"
    table.write_text(
        "\n".join(
            [
                "Chromosome,Start,End,motif_alt_id,strand,score",
                "chr7,100,121,FOXA2(MA0047.4),+,14.2",
            ]
        ),
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        cli_app,
        [
            "motifs",
            "import-table",
            str(table),
            "--preset",
            "all-motif",
            "--locus",
            "chr7:90-190",
            "--out",
            str(out),
        ],
    )

    assert result.exit_code == 0
    assert "imported 1 motif" in result.output
    spec = load_mission_spec(out)
    assert spec.motifs[0].label == "FOXA2(MA0047.4)"
