from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal, cast

from helixscope.spec.models import Locus, MissionSpec, MotifInstance, NormalizationSpec

from .common import (
    MotifImportError,
    choose_column,
    dict_rows,
    motif_id,
    overlaps_locus,
    parse_float,
    parse_int,
)

CoordinateSystem = Literal["zero-based-half-open", "one-based-inclusive"]
TablePreset = Literal["generic", "all-motif"]


@dataclass(frozen=True)
class TableMotifColumns:
    chrom: tuple[str, ...]
    start: tuple[str, ...]
    end: tuple[str, ...]
    label: tuple[str, ...]
    strand: tuple[str, ...]
    score: tuple[str, ...]
    coordinate_system: CoordinateSystem = "zero-based-half-open"


PRESETS: dict[TablePreset, TableMotifColumns] = {
    "generic": TableMotifColumns(
        chrom=("chrom", "chr", "Chromosome", "Chr", "seqnames"),
        start=("start", "Start", "chromStart", "ChromStart"),
        end=("end", "End", "chromEnd", "ChromEnd"),
        label=("label", "name", "motif", "motif_name", "motif_alt_id", "TF", "tf"),
        strand=("strand", "Strand"),
        score=("score", "Score"),
    ),
    "all-motif": TableMotifColumns(
        chrom=("Chromosome", "chrom", "chr"),
        start=("Start", "start"),
        end=("End", "end"),
        label=("motif_alt_id", "motif_name", "motif", "label", "name"),
        strand=("strand", "Strand"),
        score=("score", "Score"),
    ),
}


class TableMotifParseError(MotifImportError):
    """Raised when a tabular motif annotation cannot be converted safely."""


def load_table_motifs(
    path: Path,
    *,
    locus: Locus | None = None,
    source: str | None = None,
    preset: TablePreset = "generic",
    delimiter: str | None = None,
    coordinate_system: CoordinateSystem | None = None,
    chrom_column: str | None = None,
    start_column: str | None = None,
    end_column: str | None = None,
    label_column: str | None = None,
    strand_column: str | None = None,
    score_column: str | None = None,
) -> tuple[MotifInstance, ...]:
    columns = _columns_for_preset(
        preset,
        coordinate_system=coordinate_system,
        chrom_column=chrom_column,
        start_column=start_column,
        end_column=end_column,
        label_column=label_column,
        strand_column=strand_column,
        score_column=score_column,
    )
    source_label = source or str(path)
    motifs: list[MotifInstance] = []
    for line_number, row in dict_rows(path, delimiter=delimiter):
        parsed = _parse_table_row(
            row,
            line_number=line_number,
            source=source_label,
            locus=locus,
            columns=columns,
        )
        if parsed is not None:
            motifs.append(parsed)
    return tuple(motifs)


def mission_spec_from_table(
    path: Path,
    *,
    genome: str,
    locus: Locus,
    title: str | None = None,
    source: str | None = None,
    preset: TablePreset = "generic",
    delimiter: str | None = None,
    coordinate_system: CoordinateSystem | None = None,
    chrom_column: str | None = None,
    start_column: str | None = None,
    end_column: str | None = None,
    label_column: str | None = None,
    strand_column: str | None = None,
    score_column: str | None = None,
) -> MissionSpec:
    motifs = load_table_motifs(
        path,
        locus=locus,
        source=source,
        preset=preset,
        delimiter=delimiter,
        coordinate_system=coordinate_system,
        chrom_column=chrom_column,
        start_column=start_column,
        end_column=end_column,
        label_column=label_column,
        strand_column=strand_column,
        score_column=score_column,
    )
    source_label = source or str(path)
    resolved_coordinate_system = coordinate_system or PRESETS[preset].coordinate_system
    return MissionSpec(
        title=title or f"{preset} motif annotations at {locus.display_coord}",
        genome=genome,
        loci=[locus],
        motifs=list(motifs),
        normalization=NormalizationSpec(
            policy="annotation_only",
            summary=f"Motif annotations were imported from a {preset} tabular export.",
            caveats=[
                f"Motif source: {source_label}",
                f"Input coordinates were treated as {resolved_coordinate_system}.",
                "Motif annotations show sequence compatibility, not TF binding by themselves.",
            ],
        ),
    )


def _parse_table_row(
    row: dict[str, str],
    *,
    line_number: int,
    source: str,
    locus: Locus | None,
    columns: TableMotifColumns,
) -> MotifInstance | None:
    chrom = _choose(row, columns.chrom, True, line_number, "chromosome")
    start = parse_int(
        _choose(row, columns.start, True, line_number, "start"),
        line_number=line_number,
        field_name="start",
    )
    end = parse_int(
        _choose(row, columns.end, True, line_number, "end"),
        line_number=line_number,
        field_name="end",
    )
    if columns.coordinate_system == "one-based-inclusive":
        start -= 1
    if start >= end:
        raise TableMotifParseError(f"line {line_number} has start >= end after conversion")

    if locus is not None and not overlaps_locus(chrom, start, end, locus):
        return None

    label = _choose(row, columns.label, False, line_number, "label") or f"motif_{line_number}"
    strand = _choose(row, columns.strand, False, line_number, "strand") or "."
    if strand not in {"+", "-", "."}:
        strand = "."
    score_value = _choose(row, columns.score, False, line_number, "score")
    score = parse_float(score_value, line_number=line_number, field_name="score")

    return MotifInstance(
        id=motif_id(label, line_number),
        chrom=chrom,
        label=label,
        start=start,
        end=end,
        strand=cast(Literal["+", "-", "."], strand),
        score=score,
        source=source,
    )


def _columns_for_preset(
    preset: TablePreset,
    *,
    coordinate_system: CoordinateSystem | None,
    chrom_column: str | None,
    start_column: str | None,
    end_column: str | None,
    label_column: str | None,
    strand_column: str | None,
    score_column: str | None,
) -> TableMotifColumns:
    columns = PRESETS[preset]
    return TableMotifColumns(
        chrom=(chrom_column,) if chrom_column else columns.chrom,
        start=(start_column,) if start_column else columns.start,
        end=(end_column,) if end_column else columns.end,
        label=(label_column,) if label_column else columns.label,
        strand=(strand_column,) if strand_column else columns.strand,
        score=(score_column,) if score_column else columns.score,
        coordinate_system=coordinate_system or columns.coordinate_system,
    )


def _choose(
    row: dict[str, str],
    candidates: tuple[str, ...],
    required: bool,
    line_number: int,
    role: str,
) -> str:
    value = choose_column(
        row,
        candidates,
        required=required,
        line_number=line_number,
        role=role,
    )
    return value or ""
