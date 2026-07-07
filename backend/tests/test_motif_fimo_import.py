from __future__ import annotations

from pathlib import Path

from helixscope.io.motifs.fimo import load_fimo_motifs, mission_spec_from_fimo
from helixscope.spec.models import Locus


def test_load_fimo_motifs_converts_sequence_relative_coordinates(tmp_path: Path) -> None:
    fimo = tmp_path / "fimo.tsv"
    fimo.write_text(
        "\n".join(
            [
                "# FIMO output",
                "motif_id\tmotif_alt_id\tsequence_name\tstart\tstop\tstrand\tscore\tp-value\tq-value\tmatched_sequence",
                "MA0047.4\tFOXA2\tchr7:90-190\t11\t31\t+\t14.2\t1e-5\t0.01\tACGT",
                "MA0482.2\tGATA4\tchr8:90-190\t11\t31\t-\t9.1\t1e-4\t0.02\tACGT",
                "",
                "# FIMO footer lines should be ignored",
            ]
        ),
        encoding="utf-8",
    )

    motifs = load_fimo_motifs(
        fimo,
        locus=Locus(id="target", coord="chr7:90-190"),
        source="unit_test_fimo",
    )

    assert len(motifs) == 1
    assert motifs[0].chrom == "chr7"
    assert motifs[0].label == "FOXA2(MA0047.4)"
    assert motifs[0].start == 100
    assert motifs[0].end == 121
    assert motifs[0].strand == "+"
    assert motifs[0].score == 14.2
    assert motifs[0].source == "unit_test_fimo"


def test_mission_spec_from_fimo_is_annotation_only(tmp_path: Path) -> None:
    fimo = tmp_path / "fimo.tsv"
    fimo.write_text(
        "\n".join(
            [
                "motif_id\tmotif_alt_id\tsequence_name\tstart\tstop\tstrand\tscore",
                "MA0047.4\tFOXA2\tchr7:90-190\t11\t31\t+\t14.2",
            ]
        ),
        encoding="utf-8",
    )

    spec = mission_spec_from_fimo(
        fimo,
        genome="hg38",
        locus=Locus(id="target", coord="chr7:90-190"),
    )

    assert spec.tracks == []
    assert len(spec.motifs) == 1
    assert spec.normalization.policy == "annotation_only"
