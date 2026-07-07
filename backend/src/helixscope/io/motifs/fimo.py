from __future__ import annotations

import re
from pathlib import Path
from typing import Literal, cast

from helixscope.spec.models import Locus, MissionSpec, MotifInstance, NormalizationSpec

from .common import (
    MotifImportError,
    dict_rows,
    motif_id,
    overlaps_locus,
    parse_float,
    parse_int,
)

SEQUENCE_COORD_RE = re.compile(
    r"(?P<chrom>[^:\s]+):(?P<start>[0-9,]+)-(?P<end>[0-9,]+)"
)


class FimoMotifParseError(MotifImportError):
    """Raised when a FIMO TSV row cannot be converted safely."""


def load_fimo_motifs(
    path: Path,
    *,
    locus: Locus | None = None,
    source: str | None = None,
) -> tuple[MotifInstance, ...]:
    """Load FIMO TSV hits into canonical MotifInstance records.

    FIMO start/stop are one-based inclusive coordinates within `sequence_name`.
    If `sequence_name` contains `chr:start-end`, hits are converted to genomic
    zero-based half-open coordinates by adding that sequence offset.
    """

    source_label = source or str(path)
    motifs: list[MotifInstance] = []
    for line_number, row in dict_rows(path, delimiter="\t"):
        parsed = _parse_fimo_row(
            row,
            line_number=line_number,
            source=source_label,
            locus=locus,
        )
        if parsed is not None:
            motifs.append(parsed)
    return tuple(motifs)


def mission_spec_from_fimo(
    path: Path,
    *,
    genome: str,
    locus: Locus,
    title: str | None = None,
    source: str | None = None,
) -> MissionSpec:
    motifs = load_fimo_motifs(path, locus=locus, source=source)
    source_label = source or str(path)
    return MissionSpec(
        title=title or f"FIMO motif annotations at {locus.display_coord}",
        genome=genome,
        loci=[locus],
        motifs=list(motifs),
        normalization=NormalizationSpec(
            policy="annotation_only",
            summary="Motif annotations were imported from FIMO TSV output.",
            caveats=[
                f"Motif source: {source_label}",
                "FIMO start/stop are treated as one-based inclusive sequence coordinates.",
                "Motif annotations show sequence compatibility, not TF binding by themselves.",
            ],
        ),
    )


def _parse_fimo_row(
    row: dict[str, str],
    *,
    line_number: int,
    source: str,
    locus: Locus | None,
) -> MotifInstance | None:
    sequence_name = _required(row, "sequence_name", line_number=line_number)
    raw_start = parse_int(
        _required(row, "start", line_number=line_number),
        line_number=line_number,
        field_name="start",
    )
    raw_stop = parse_int(
        _required(row, "stop", line_number=line_number),
        line_number=line_number,
        field_name="stop",
    )
    left = min(raw_start, raw_stop)
    right = max(raw_start, raw_stop)
    chrom, start, end = _resolve_fimo_interval(sequence_name, left, right)

    if locus is not None and not overlaps_locus(chrom, start, end, locus):
        return None

    motif_id_value = row.get("motif_id", "").strip() or f"motif_{line_number}"
    motif_alt_id = row.get("motif_alt_id", "").strip()
    label = _fimo_label(motif_id_value, motif_alt_id)
    strand = row.get("strand", ".").strip() or "."
    if strand not in {"+", "-", "."}:
        raise FimoMotifParseError(
            f"line {line_number} has invalid strand {strand!r}; expected +, -, or ."
        )
    motif_strand = cast(Literal["+", "-", "."], strand)
    score = parse_float(row.get("score"), line_number=line_number, field_name="score")

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


def _resolve_fimo_interval(sequence_name: str, left: int, right: int) -> tuple[str, int, int]:
    match = SEQUENCE_COORD_RE.search(sequence_name)
    if match:
        chrom = match.group("chrom")
        sequence_start = int(match.group("start").replace(",", ""))
        return chrom, sequence_start + left - 1, sequence_start + right

    return sequence_name, left - 1, right


def _required(row: dict[str, str], key: str, *, line_number: int) -> str:
    value = row.get(key, "").strip()
    if not value:
        raise FimoMotifParseError(f"line {line_number} is missing required FIMO column {key!r}")
    return value


def _fimo_label(motif_id_value: str, motif_alt_id: str) -> str:
    if motif_alt_id and motif_alt_id != "." and motif_alt_id != motif_id_value:
        return f"{motif_alt_id}({motif_id_value})"
    return motif_id_value
