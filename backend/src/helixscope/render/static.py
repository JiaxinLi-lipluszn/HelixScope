from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import cast

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from jinja2 import Template
from matplotlib.axes import Axes
from numpy.typing import NDArray

from helixscope.render.motifs import motif_track_height_ratio, plot_motif_track
from helixscope.spec.models import Locus, MissionSpec


@dataclass(frozen=True)
class RenderResult:
    out_dir: Path
    report_json: Path
    artifacts: tuple[Path, ...]


def render_report(spec: MissionSpec, out_dir: Path, formats: Iterable[str]) -> RenderResult:
    out_dir.mkdir(parents=True, exist_ok=True)
    requested = {fmt.lower() for fmt in formats}
    artifacts: list[Path] = []

    png_path: Path | None = None
    if "png" in requested:
        png_path = out_dir / "locus_probe.png"
        _render_png(spec, png_path)
        artifacts.append(png_path)

    if "html" in requested:
        html_path = out_dir / "locus_probe.html"
        _render_html(spec, html_path, png_path)
        artifacts.append(html_path)

    report_json = out_dir / "report.json"
    _write_report_json(spec, report_json, artifacts)
    return RenderResult(out_dir=out_dir, report_json=report_json, artifacts=tuple(artifacts))


def _render_png(spec: MissionSpec, path: Path) -> None:
    locus = spec.loci[0]
    tracks = spec.tracks
    motif_lane_count = plot_motif_track_lane_count(spec, locus)
    motif_ratio = motif_track_height_ratio(motif_lane_count, has_variants=bool(spec.variants))
    row_count = len(tracks) + 2
    height = max(6.4, 1.25 * len(tracks) + motif_ratio + 2.4)

    fig, axes = plt.subplots(
        row_count,
        1,
        figsize=(12, height),
        sharex=True,
        gridspec_kw={"height_ratios": [1.0] * len(tracks) + [motif_ratio, 1.35]},
    )
    if not isinstance(axes, np.ndarray):
        axes = np.array([axes])

    x = cast(NDArray[np.float64], np.linspace(locus.start or 0, locus.end or 1, 800))
    fig.suptitle(spec.title, fontsize=16, fontweight="bold", y=0.985)

    for index, track in enumerate(tracks):
        ax = axes[index]
        signal = _synthetic_signal(x, locus, index)
        color = track.color or _palette(index)
        ax.fill_between(x, signal, color=color, alpha=0.22, linewidth=0)
        ax.plot(x, signal, color=color, linewidth=1.8)
        ax.set_ylim(0, max(1.05, float(signal.max()) * 1.18))
        ax.set_ylabel(track.display_label, rotation=0, ha="right", va="center", labelpad=72)
        ax.grid(axis="y", color="#e6e8eb", linewidth=0.8)
        ax.spines[["top", "right"]].set_visible(False)

    plot_motif_track(axes[len(tracks)], locus, spec.motifs, spec.variants)
    _draw_normalization_card(axes[-1], spec, locus)

    axes[-2].set_xlim(locus.start, locus.end)
    axes[-2].set_xlabel(f"{spec.genome} {locus.display_coord}")
    fig.tight_layout(rect=(0.06, 0.03, 0.98, 0.96))
    fig.savefig(path, dpi=220)
    plt.close(fig)


def _synthetic_signal(x: NDArray[np.float64], locus: Locus, index: int) -> NDArray[np.float64]:
    start = locus.start or int(x.min())
    end = locus.end or int(x.max())
    width = end - start
    centers = np.array([start + width * 0.28, start + width * 0.54, start + width * 0.72])
    scales = np.array([0.045, 0.075, 0.035]) * width
    weights = np.array([1.0, 0.72 + index * 0.12, 0.48 + index * 0.08])
    signal = np.zeros_like(x, dtype=float)
    for center, scale, weight in zip(centers, scales, weights, strict=True):
        signal += weight * np.exp(-0.5 * ((x - center) / scale) ** 2)
    ripple = 0.06 * (index + 1) * (np.sin((x - start) / width * np.pi * 6) + 1.1)
    signal = signal + ripple
    signal = signal / max(signal.max(), 1e-9)
    return cast(NDArray[np.float64], signal * (1.0 + 0.18 * index))


def plot_motif_track_lane_count(spec: MissionSpec, locus: Locus) -> int:
    from helixscope.render.motifs import layout_motifs_for_locus

    return layout_motifs_for_locus(locus, spec.motifs).lane_count


def _draw_normalization_card(ax: Axes, spec: MissionSpec, locus: Locus) -> None:
    ax.axis("off")
    caveats = "\n".join(f"- {item}" for item in spec.normalization.caveats)
    text = (
        "Normalization Card\n"
        f"Genome: {spec.genome} | Locus: {locus.display_label} ({locus.display_coord})\n"
        f"Policy: {spec.normalization.policy}\n"
        f"{spec.normalization.summary}\n"
        f"{caveats}"
    )
    ax.text(
        0.01,
        0.94,
        text,
        transform=ax.transAxes,
        va="top",
        ha="left",
        fontsize=10,
        linespacing=1.35,
        bbox={
            "boxstyle": "round,pad=0.45,rounding_size=0.08",
            "facecolor": "#f8f9fa",
            "edgecolor": "#ced4da",
            "linewidth": 0.9,
        },
    )


def _render_html(spec: MissionSpec, path: Path, png_path: Path | None) -> None:
    image = png_path.name if png_path else None
    template = Template(
        """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{ title }}</title>
  <style>
    body { margin: 0; font-family: Arial, sans-serif; color: #17202a; background: #f6f7f9; }
    main { max-width: 1180px; margin: 0 auto; padding: 28px; }
    h1 { margin: 0 0 8px; font-size: 28px; }
    .meta { margin: 0 0 20px; color: #52616f; }
    img { width: 100%; height: auto; border: 1px solid #d7dce2; background: white; }
    pre { white-space: pre-wrap; background: white; border: 1px solid #d7dce2; padding: 16px; }
  </style>
</head>
<body>
  <main>
    <h1>{{ title }}</h1>
    <p class="meta">{{ report_type }} | {{ genome }}</p>
    {% if image %}<img src="{{ image }}" alt="HelixScope locus report">{% endif %}
    <h2>Normalization</h2>
    <pre>{{ normalization }}</pre>
  </main>
</body>
</html>
"""
    )
    path.write_text(
        template.render(
            title=spec.title,
            report_type=spec.report_type,
            genome=spec.genome,
            image=image,
            normalization=spec.normalization.model_dump_json(indent=2),
        ),
        encoding="utf-8",
    )


def _write_report_json(spec: MissionSpec, path: Path, artifacts: list[Path]) -> None:
    payload = {
        "spec": spec.model_dump(mode="json"),
        "artifacts": [artifact.name for artifact in artifacts],
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _palette(index: int) -> str:
    colors = ["#277da1", "#f3722c", "#43aa8b", "#577590", "#bc4749", "#6d597a"]
    return colors[index % len(colors)]
