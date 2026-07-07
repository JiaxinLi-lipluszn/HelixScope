from __future__ import annotations

import re
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

COORD_RE = re.compile(r"^(?P<chrom>[^:]+):(?P<start>[0-9,]+)-(?P<end>[0-9,]+)$")


class Locus(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    label: str | None = None
    coord: str | None = None
    chrom: str | None = None
    start: int | None = None
    end: int | None = None

    @model_validator(mode="before")
    @classmethod
    def parse_coord(cls, data: Any) -> Any:
        if not isinstance(data, dict) or not data.get("coord"):
            return data
        match = COORD_RE.match(str(data["coord"]))
        if not match:
            raise ValueError("coord must look like chr1:1000-2000")
        parsed = dict(data)
        parsed.setdefault("chrom", match.group("chrom"))
        parsed.setdefault("start", int(match.group("start").replace(",", "")))
        parsed.setdefault("end", int(match.group("end").replace(",", "")))
        return parsed

    @model_validator(mode="after")
    def validate_interval(self) -> Locus:
        if self.chrom is None or self.start is None or self.end is None:
            raise ValueError("locus requires coord or chrom/start/end")
        if self.start >= self.end:
            raise ValueError("locus start must be smaller than end")
        return self

    @property
    def display_label(self) -> str:
        return self.label or self.id

    @property
    def display_coord(self) -> str:
        return f"{self.chrom}:{self.start}-{self.end}"


class TrackSpec(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
    label: str | None = None
    type: str = "signal"
    assay: str | None = None
    file: str | None = None
    source: Literal["synthetic", "file"] = "synthetic"
    factor: str | None = None
    cell_type: str | None = None
    color: str | None = None

    @property
    def display_label(self) -> str:
        if self.label:
            return self.label
        parts = [self.factor, self.assay, self.cell_type]
        return " ".join(part for part in parts if part) or self.id


class MotifInstance(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    chrom: str | None = None
    label: str
    start: int
    end: int
    strand: Literal["+", "-", "."] = "."
    score: float = 1.0
    source: str | None = None

    @model_validator(mode="after")
    def validate_interval(self) -> MotifInstance:
        if self.start >= self.end:
            raise ValueError("motif start must be smaller than end")
        return self


class VariantSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    position: int
    ref: str | None = None
    alt: str | None = None
    label: str | None = None

    @property
    def display_label(self) -> str:
        if self.label:
            return self.label
        if self.ref and self.alt:
            return f"{self.id} {self.ref}>{self.alt}"
        return self.id


class NormalizationSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    policy: str = "demo_within_track_scaling"
    summary: str = "Synthetic demo signals are scaled within each track."
    caveats: list[str] = Field(
        default_factory=lambda: [
            "Do not compare raw amplitudes across assay or TF families.",
            "Co-localization is compatible with shared occupancy, not proof of cooperation.",
        ]
    )


class MissionSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: str = "0.1"
    report_type: Literal["locus_probe"] = "locus_probe"
    title: str
    genome: str
    loci: list[Locus] = Field(min_length=1)
    tracks: list[TrackSpec] = Field(default_factory=list)
    motifs: list[MotifInstance] = Field(default_factory=list)
    variants: list[VariantSpec] = Field(default_factory=list)
    normalization: NormalizationSpec = Field(default_factory=NormalizationSpec)


def demo_mission_spec() -> MissionSpec:
    return MissionSpec(
        title="HelixScope synthetic LocusProbe demo",
        genome="hg38",
        loci=[
            Locus(
                id="demo_enhancer",
                label="Synthetic enhancer",
                coord="chr7:5500000-5502400",
            )
        ],
        tracks=[
            TrackSpec(id="atac_demo", label="ATAC demo", assay="ATAC-seq", color="#277da1"),
            TrackSpec(id="chip_demo", label="TF occupancy demo", assay="ChIP-seq", color="#f3722c"),
            TrackSpec(
                id="attr_demo",
                label="Model attribution demo",
                type="model_attribution",
                color="#43aa8b",
            ),
        ],
        motifs=[
            MotifInstance(
                id="motif_1",
                label="FOXA2(MA0047.4)",
                start=5500720,
                end=5500741,
                strand="+",
                score=12.4,
                source="synthetic_fimo_demo",
            ),
            MotifInstance(
                id="motif_2",
                label="GATA4(MA0482.2)",
                start=5501260,
                end=5501275,
                strand="-",
                score=9.8,
                source="synthetic_fimo_demo",
            ),
            MotifInstance(
                id="motif_3",
                label="HNF4A(MA0114.4)",
                start=5501690,
                end=5501712,
                strand="+",
                score=7.7,
                source="synthetic_fimo_demo",
            ),
        ],
        variants=[
            VariantSpec(id="rsDemo1", position=5501304, ref="A", alt="G"),
        ],
    )
