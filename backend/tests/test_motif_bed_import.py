from __future__ import annotations

from pathlib import Path

import pytest

from helixscope.io.motifs.bed import BedMotifParseError, load_bed_motifs, mission_spec_from_bed
from helixscope.spec.models import Locus


def test_load_bed_motifs_filters_locus_and_preserves_columns(tmp_path: Path) -> None:
    bed = tmp_path / "motifs.bed"
    bed.write_text(
        "\n".join(
            [
                "track name=motifs",
                "chr7\t100\t121\tFOXA2(MA0047.4)\t14.2\t+",
                "chr7\t180\t200\tGATA4(MA0482.2)\t.\t-",
                "chr8\t110\t130\tOTHER\t2\t+",
                "chr7\t240\t260\tOUTSIDE\t1\t+",
            ]
        ),
        encoding="utf-8",
    )

    motifs = load_bed_motifs(
        bed,
        locus=Locus(id="target", coord="chr7:90-190"),
        source="unit_test_bed",
    )

    assert [motif.label for motif in motifs] == ["FOXA2(MA0047.4)", "GATA4(MA0482.2)"]
    assert motifs[0].id == "FOXA2_MA0047.4_2"
    assert motifs[0].chrom == "chr7"
    assert motifs[0].start == 100
    assert motifs[0].end == 121
    assert motifs[0].score == 14.2
    assert motifs[0].strand == "+"
    assert motifs[0].source == "unit_test_bed"
    assert motifs[1].score == 1.0


def test_bed_import_rejects_invalid_intervals(tmp_path: Path) -> None:
    bed = tmp_path / "bad.bed"
    bed.write_text("chr7\t200\t100\tBROKEN\t1\t+\n", encoding="utf-8")

    with pytest.raises(BedMotifParseError, match="chromStart >= chromEnd"):
        load_bed_motifs(bed)


def test_mission_spec_from_bed_is_motif_only(tmp_path: Path) -> None:
    bed = tmp_path / "motifs.bed"
    bed.write_text("chr7\t100\t121\tFOXA2(MA0047.4)\t14.2\t+\n", encoding="utf-8")

    spec = mission_spec_from_bed(
        bed,
        genome="hg38",
        locus=Locus(id="target", coord="chr7:90-190"),
        title="BED motif import",
    )

    assert spec.title == "BED motif import"
    assert spec.tracks == []
    assert len(spec.motifs) == 1
    assert spec.normalization.policy == "annotation_only"
