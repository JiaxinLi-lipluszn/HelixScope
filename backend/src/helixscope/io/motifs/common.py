from __future__ import annotations

import csv
import gzip
import re
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from pathlib import Path
from typing import TextIO

from helixscope.spec.models import Locus


class MotifImportError(ValueError):
    """Raised when an external motif annotation cannot be converted safely."""


@contextmanager
def open_text(path: Path) -> Iterator[TextIO]:
    if path.suffix == ".gz":
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            yield handle
    else:
        with path.open("r", encoding="utf-8") as handle:
            yield handle


def overlaps_locus(chrom: str, start: int, end: int, locus: Locus) -> bool:
    if locus.start is None or locus.end is None:
        return False
    return chrom == locus.chrom and end > locus.start and start < locus.end


def motif_id(label: str, line_number: int) -> str:
    token = re.sub(r"[^A-Za-z0-9_.:-]+", "_", label).strip("_")
    return f"{token or 'motif'}_{line_number}"


def parse_int(value: str, *, line_number: int, field_name: str) -> int:
    try:
        return int(str(value).replace(",", ""))
    except ValueError as exc:
        raise MotifImportError(
            f"line {line_number} has non-integer {field_name}: {value!r}"
        ) from exc


def parse_float(value: str | None, *, line_number: int, field_name: str) -> float:
    if value is None or value == "" or value == ".":
        return 1.0
    try:
        return float(value)
    except ValueError as exc:
        raise MotifImportError(
            f"line {line_number} has non-numeric {field_name}: {value!r}"
        ) from exc


def choose_column(
    row: dict[str, str],
    candidates: Sequence[str],
    *,
    required: bool,
    line_number: int,
    role: str,
) -> str | None:
    lower_to_key = {key.lower(): key for key in row}
    for candidate in candidates:
        key = lower_to_key.get(candidate.lower())
        if key is not None:
            value = row.get(key)
            if value is not None and value != "":
                return value
    if required:
        raise MotifImportError(
            f"line {line_number} is missing required {role} column; tried "
            f"{', '.join(candidates)}"
        )
    return None


def detect_delimiter(header: str, requested: str | None = None) -> str:
    if requested is not None:
        if requested == r"\t":
            return "\t"
        return requested
    return "\t" if header.count("\t") >= header.count(",") else ","


def dict_rows(path: Path, *, delimiter: str | None = None) -> Iterator[tuple[int, dict[str, str]]]:
    with open_text(path) as handle:
        header = ""
        header_line = 0
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            header = line
            header_line = line_number
            break
        if not header:
            return

        resolved_delimiter = detect_delimiter(header, delimiter)
        reader = csv.DictReader(
            handle,
            fieldnames=header.rstrip("\n\r").split(resolved_delimiter),
            delimiter=resolved_delimiter,
        )
        for offset, row in enumerate(reader, start=header_line + 1):
            values = [(value or "").strip() for value in row.values()]
            if not row or not any(values):
                continue
            first_value = next((value for value in values if value), "")
            if first_value.startswith("#"):
                continue
            yield offset, {key: (value or "").strip() for key, value in row.items() if key}
