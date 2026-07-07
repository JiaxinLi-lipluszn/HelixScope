from __future__ import annotations

from pathlib import Path
from typing import Literal, cast

from helixscope.spec.models import Locus, MissionSpec, MotifInstance, NormalizationSpec

from .common import MotifImportError, motif_id, open_text, overlaps_locus, parse_float, parse_int


class BedMotifParseError(MotifImportError):
    """Raised when a BED motif record cannot be converted safely."""


def load_bed_motifs(
    path: Path,
    *,
    locus: Locus | None = None,
    source: str | None = None,
) -> tuple[MotifInstance, ...]:
    """Load BED3/BED6-like motif annotations into canonical MotifInstance records.

    BED chromStart/chromEnd are kept as zero-based half-open coordinates. The
    renderer treats motif coordinates as continuous genomic intervals, so no
    one-based conversion is applied during import.
    """

    source_label = source or str(path)
    motifs: list[MotifInstance] = []
    with open_text(path) as handle:
        for line_number, line in enumerate(handle, start=1):
            parsed = _parse_bed_line(
                line,
                line_number=line_number,
                source=source_label,
                locus=locus,
            )
            if parsed is not None:
                motifs.append(parsed)
    return tuple(motifs)


def mission_spec_from_bed(
    path: Path,
    *,
    genome: str,
    locus: Locus,
    title: str | None = None,
    source: str | None = None,
) -> MissionSpec:
    motifs = load_bed_motifs(path, locus=locus, source=source)
    source_label = source or str(path)
    return MissionSpec(
        title=title or f"Motif annotations at {locus.display_coord}",
        genome=genome,
        loci=[locus],
        motifs=list(motifs),
        normalization=NormalizationSpec(
            policy="annotation_only",
            summary=(
                "Motif annotations were imported from BED into canonical "
                "HelixScope motif records."
            ),
            caveats=[
                f"Motif source: {source_label}",
                "BED chromStart/chromEnd are treated as zero-based half-open intervals.",
                "Motif annotations show sequence compatibility, not TF binding by themselves.",
            ],
        ),
    )


def _parse_bed_line(
    line: str,
    *,
    line_number: int,
    source: str,
    locus: Locus | None,
) -> MotifInstance | None:
    stripped = line.strip()
    if not stripped or stripped.startswith(("#", "track ", "browser ")):
        return None

    fields = stripped.split()
    if len(fields) < 3:
        raise BedMotifParseError(f"BED line {line_number} has fewer than 3 columns")

    chrom = fields[0]
    start = parse_int(fields[1], line_number=line_number, field_name="chromStart")
    end = parse_int(fields[2], line_number=line_number, field_name="chromEnd")
    if start >= end:
        raise BedMotifParseError(f"BED line {line_number} has chromStart >= chromEnd")

    if locus is not None and not overlaps_locus(chrom, start, end, locus):
        return None

    label = fields[3] if len(fields) >= 4 and fields[3] != "." else f"motif_{line_number}"
    score = (
        parse_float(fields[4], line_number=line_number, field_name="score")
        if len(fields) >= 5
        else 1.0
    )
    strand = fields[5] if len(fields) >= 6 else "."
    if strand not in {"+", "-", "."}:
        raise BedMotifParseError(
            f"BED line {line_number} has invalid strand {strand!r}; expected +, -, or ."
        )
    motif_strand = cast(Literal["+", "-", "."], strand)

    return MotifInstance(
        id=motif_id(label, line_number),
        chrom=chrom,
        label=label,
        start=start,
        end=end,
        strand=motif_strand,
        score=score,
        source=source,
    )
