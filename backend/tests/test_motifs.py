from __future__ import annotations

from helixscope.render.motifs import (
    assign_motif_lanes,
    human_readable_motif_label,
    layout_motifs_for_locus,
    motif_glyphs_in_locus,
    motif_track_height_ratio,
)
from helixscope.spec.models import Locus, MotifInstance


def test_human_readable_motif_label_prefers_tf_name() -> None:
    assert human_readable_motif_label("FOXA2(MA0047.4)") == "FOXA2"
    assert human_readable_motif_label("FOXA2") == "FOXA2"
    assert human_readable_motif_label("(MA0047.4)") == "MA0047.4"


def test_motif_glyphs_filter_clip_and_sort() -> None:
    locus = Locus(id="locus", coord="chr1:100-200")
    motifs = [
        MotifInstance(id="outside", label="OUT", start=220, end=230),
        MotifInstance(id="partial", label="FOXA2(MA0047.4)", start=90, end=110, score=3),
        MotifInstance(id="inside", label="GATA4(MA0482.2)", start=150, end=160, score=9),
    ]
    glyphs = motif_glyphs_in_locus(locus, motifs)
    assert [glyph.id for glyph in glyphs] == ["partial", "inside"]
    assert glyphs[0].start == 100
    assert glyphs[0].label == "FOXA2(MA0047.4)"
    assert glyphs[0].display_label == "FOXA2"


def test_assign_motif_lanes_compacts_overlapping_intervals() -> None:
    glyphs = motif_glyphs_in_locus(
        Locus(id="locus", coord="chr1:100-260"),
        [
            MotifInstance(id="a", label="A", start=110, end=140),
            MotifInstance(id="b", label="B", start=145, end=165),
            MotifInstance(id="c", label="C", start=220, end=240),
        ],
        human_readable_labels=False,
    )
    layout = assign_motif_lanes(glyphs, jitter_bp=20)
    assert layout.lane_count == 2
    assert [glyph.lane for glyph in layout.glyphs] == [0, 1, 0]


def test_layout_height_grows_with_lanes() -> None:
    locus = Locus(id="locus", coord="chr1:100-260")
    layout = layout_motifs_for_locus(
        locus,
        [
            MotifInstance(id="a", label="A", start=110, end=140),
            MotifInstance(id="b", label="B", start=145, end=165),
        ],
        jitter_bp=20,
    )
    assert layout.lane_count == 2
    assert motif_track_height_ratio(layout.lane_count, has_variants=True) > 1.2
