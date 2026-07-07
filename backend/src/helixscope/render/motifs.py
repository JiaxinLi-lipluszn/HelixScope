from __future__ import annotations

import heapq
import re
from collections.abc import Iterable
from dataclasses import dataclass

from matplotlib.axes import Axes
from matplotlib.collections import PatchCollection
from matplotlib.colors import to_rgba
from matplotlib.patches import Rectangle

from helixscope.spec.models import Locus, MotifInstance, VariantSpec


@dataclass(frozen=True)
class MotifGlyph:
    id: str
    label: str
    display_label: str
    start: int
    end: int
    strand: str
    score: float
    lane: int = 0
    source: str | None = None

    @property
    def width(self) -> int:
        return max(self.end - self.start, 1)


@dataclass(frozen=True)
class MotifLayout:
    glyphs: tuple[MotifGlyph, ...]
    lane_count: int


def human_readable_motif_label(text: str) -> str:
    """Return a readable display label without changing annotation provenance."""

    value = str(text).strip()
    if not value:
        return value
    if "(" not in value:
        return value

    prefix, _ = value.split("(", 1)
    prefix = prefix.strip()
    if prefix:
        return prefix

    match = re.search(r"\(([^)]+)\)", value)
    return match.group(1) if match else value


def motif_glyphs_in_locus(
    locus: Locus,
    motifs: Iterable[MotifInstance],
    *,
    human_readable_labels: bool = True,
) -> tuple[MotifGlyph, ...]:
    """Filter motif annotations to one locus and clip partially visible motifs."""

    start = locus.start or 0
    end = locus.end or 0
    glyphs: list[MotifGlyph] = []
    for motif in motifs:
        if motif.chrom is not None and motif.chrom != locus.chrom:
            continue
        if motif.end <= start or motif.start >= end:
            continue
        clipped_start = max(start, motif.start)
        clipped_end = min(end, motif.end)
        display_label = (
            human_readable_motif_label(motif.label) if human_readable_labels else motif.label
        )
        glyphs.append(
            MotifGlyph(
                id=motif.id,
                label=motif.label,
                display_label=display_label,
                start=clipped_start,
                end=clipped_end,
                strand=motif.strand,
                score=motif.score,
                source=motif.source,
            )
        )
    return tuple(sorted(glyphs, key=lambda row: (row.start, row.end, row.label, row.id)))


def assign_motif_lanes(glyphs: Iterable[MotifGlyph], *, jitter_bp: int = 50) -> MotifLayout:
    """Assign non-overlapping display lanes using a heap over lane end positions."""

    lane_heap: list[tuple[int, int]] = []
    next_lane = 0
    assigned: list[MotifGlyph] = []

    for glyph in sorted(glyphs, key=lambda row: (row.start, row.end, row.label, row.id)):
        if lane_heap and glyph.start - jitter_bp > lane_heap[0][0]:
            _, lane = heapq.heappop(lane_heap)
        else:
            lane = next_lane
            next_lane += 1
        lane_end = glyph.end + jitter_bp
        heapq.heappush(lane_heap, (lane_end, lane))
        assigned.append(
            MotifGlyph(
                id=glyph.id,
                label=glyph.label,
                display_label=glyph.display_label,
                start=glyph.start,
                end=glyph.end,
                strand=glyph.strand,
                score=glyph.score,
                lane=lane,
                source=glyph.source,
            )
        )

    lane_count = max((glyph.lane for glyph in assigned), default=-1) + 1
    return MotifLayout(glyphs=tuple(assigned), lane_count=lane_count)


def layout_motifs_for_locus(
    locus: Locus,
    motifs: Iterable[MotifInstance],
    *,
    jitter_bp: int = 50,
    human_readable_labels: bool = True,
) -> MotifLayout:
    return assign_motif_lanes(
        motif_glyphs_in_locus(locus, motifs, human_readable_labels=human_readable_labels),
        jitter_bp=jitter_bp,
    )


def motif_track_height_ratio(lane_count: int, *, has_variants: bool) -> float:
    base = 0.65 + max(lane_count, 1) * 0.32
    if has_variants:
        base += 0.28
    return min(max(base, 0.9), 2.6)


def plot_motif_track(
    ax: Axes,
    locus: Locus,
    motifs: Iterable[MotifInstance],
    variants: Iterable[VariantSpec],
    *,
    jitter_bp: int = 50,
    bar_height: float = 0.62,
    lane_gap: float = 0.18,
    font_size: float = 8.0,
) -> MotifLayout:
    layout = layout_motifs_for_locus(locus, motifs, jitter_bp=jitter_bp)
    variant_list = tuple(variants)

    ax.set_xlim(locus.start, locus.end)
    ax.set_yticks([])
    ax.set_ylabel("Motifs / variants", rotation=0, ha="right", va="center", labelpad=72)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.grid(axis="x", color="#eef0f2", linewidth=0.8)

    if not layout.glyphs and not variant_list:
        midpoint = ((locus.start or 0) + (locus.end or 1)) / 2
        ax.text(
            midpoint,
            0.5,
            "No motif or variant annotations supplied",
            ha="center",
            va="center",
            color="#6c757d",
        )
        ax.set_ylim(0, 1)
        return layout

    lane_step = bar_height + lane_gap
    rectangles: list[Rectangle] = []
    facecolors: list[tuple[float, float, float, float]] = []
    scores = [abs(glyph.score) for glyph in layout.glyphs]
    max_score = max(scores) if scores else 1.0

    for glyph in layout.glyphs:
        y = glyph.lane * lane_step + 0.1
        color = _strand_color(glyph.strand)
        alpha = _score_alpha(glyph.score, max_score)
        rectangles.append(Rectangle((glyph.start, y), glyph.width, bar_height))
        facecolors.append(to_rgba(color, alpha))
        ax.text(
            glyph.start + glyph.width / 2,
            y + bar_height / 2,
            glyph.display_label,
            fontsize=font_size,
            ha="center",
            va="center",
            color="#1f2933",
            clip_on=True,
        )

    if rectangles:
        collection = PatchCollection(
            rectangles,
            facecolors=facecolors,
            edgecolors="none",
            linewidths=0,
            match_original=False,
        )
        ax.add_collection(collection)

    variant_y = max(layout.lane_count, 1) * lane_step + 0.12
    for variant in variant_list:
        ax.axvline(variant.position, color="#d62828", linewidth=1.4, linestyle="--", alpha=0.9)
        ax.text(
            variant.position,
            variant_y,
            variant.display_label,
            ha="center",
            va="bottom",
            fontsize=font_size,
            color="#9d0208",
            clip_on=True,
        )

    y_max = variant_y + (0.45 if variant_list else 0.1)
    ax.set_ylim(0, max(y_max, 1.0))
    return layout


def _score_alpha(score: float, max_score: float) -> float:
    if max_score <= 0:
        return 0.55
    return min(max(abs(score / max_score) * 0.58, 0.16), 0.72)


def _strand_color(strand: str) -> str:
    if strand == "+":
        return "#d1495b"
    if strand == "-":
        return "#277da1"
    return "#6c757d"
