from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated, cast

import typer
from rich.console import Console

cli_app = typer.Typer(
    help="HelixScope headless-first genome visualization and report CLI.",
    no_args_is_help=True,
)
motifs_app = typer.Typer(
    help="Import motif annotations into canonical records.",
    no_args_is_help=True,
)
skill_app = typer.Typer(
    help="Install or inspect the HelixScope Codex skill.",
    no_args_is_help=True,
)
cli_app.add_typer(motifs_app, name="motifs")
cli_app.add_typer(skill_app, name="skill")
console = Console()
SpecPath = Annotated[Path, typer.Argument(exists=True, readable=True)]
OutDir = Annotated[Path, typer.Option("--out", "-o", help="Output directory.")]
FormatList = Annotated[str, typer.Option("--formats", help="Comma-separated: png,html.")]
Host = Annotated[str, typer.Option("--host", help="Bind host.")]
Port = Annotated[int, typer.Option("--port", help="Bind port.")]


def _parse_formats(value: str) -> set[str]:
    formats = {item.strip().lower() for item in value.split(",") if item.strip()}
    invalid = formats - {"png", "html"}
    if invalid:
        raise typer.BadParameter(f"Unsupported format(s): {', '.join(sorted(invalid))}")
    if not formats:
        raise typer.BadParameter("At least one output format is required.")
    return formats


def _parse_choice(value: str, *, choices: set[str], name: str) -> str:
    normalized = value.strip()
    if normalized not in choices:
        allowed = ", ".join(sorted(choices))
        raise typer.BadParameter(f"Unsupported {name}: {value}. Choose one of {allowed}.")
    return normalized


@skill_app.command("install-local")
def install_local_skill(
    codex_home: Annotated[
        Path | None,
        typer.Option(
            "--codex-home",
            help="Codex home directory; defaults to $CODEX_HOME or ~/.codex.",
        ),
    ] = None,
    repo_root: Annotated[
        Path | None,
        typer.Option("--repo-root", help="HelixScope repository root; auto-detected by default."),
    ] = None,
    env_name: Annotated[
        str,
        typer.Option("--env-name", help="Bootstrap conda/mamba environment name to remember."),
    ] = "HelixScope_env",
    replace: Annotated[
        bool,
        typer.Option("--replace", help="Replace an existing symlink that points elsewhere."),
    ] = False,
) -> None:
    """Install the HelixScope skill as an editable symlink."""

    from helixscope.skill.install import install_local_skill as install_skill_symlink

    try:
        result = install_skill_symlink(
            codex_home=codex_home,
            repo_root=repo_root,
            env_name=env_name,
            replace=replace,
        )
    except (FileExistsError, FileNotFoundError) as exc:
        raise typer.BadParameter(str(exc)) from exc

    console.print(
        f"[green]{result.status}[/green] {result.target} -> {result.source}"
    )
    console.print(f"  - config: {result.config_path}")
    console.print(f"  - env: {result.env_name}")


@motifs_app.command("import-bed")
def import_bed_motifs(
    bed: Annotated[Path, typer.Argument(exists=True, readable=True, dir_okay=False)],
    locus: Annotated[str, typer.Option("--locus", help="Target locus, e.g. chr7:5500000-5502400.")],
    out: Annotated[Path, typer.Option("--out", "-o", help="MissionSpec YAML to write.")],
    genome: Annotated[str, typer.Option("--genome", help="Genome assembly label.")] = "hg38",
    title: Annotated[str | None, typer.Option("--title", help="Report title.")] = None,
    source: Annotated[
        str | None,
        typer.Option("--source", help="Provenance label stored on imported motifs."),
    ] = None,
) -> None:
    """Convert BED motif annotations into a minimal MissionSpec."""

    from helixscope.io.motifs.bed import BedMotifParseError, mission_spec_from_bed
    from helixscope.spec.loaders import write_mission_spec
    from helixscope.spec.models import Locus

    try:
        mission = mission_spec_from_bed(
            bed,
            genome=genome,
            locus=Locus(id="bed_locus", coord=locus),
            title=title,
            source=source,
        )
    except BedMotifParseError as exc:
        raise typer.BadParameter(str(exc)) from exc

    write_mission_spec(mission, out)
    console.print(f"[green]imported[/green] {len(mission.motifs)} motif(s) from {bed}")
    console.print(f"  - {out}")


@motifs_app.command("import-fimo")
def import_fimo_motifs(
    fimo: Annotated[Path, typer.Argument(exists=True, readable=True, dir_okay=False)],
    locus: Annotated[str, typer.Option("--locus", help="Target locus, e.g. chr7:5500000-5502400.")],
    out: Annotated[Path, typer.Option("--out", "-o", help="MissionSpec YAML to write.")],
    genome: Annotated[str, typer.Option("--genome", help="Genome assembly label.")] = "hg38",
    title: Annotated[str | None, typer.Option("--title", help="Report title.")] = None,
    source: Annotated[
        str | None,
        typer.Option("--source", help="Provenance label stored on imported motifs."),
    ] = None,
) -> None:
    """Convert FIMO TSV motif hits into a minimal MissionSpec."""

    from helixscope.io.motifs.fimo import FimoMotifParseError, mission_spec_from_fimo
    from helixscope.spec.loaders import write_mission_spec
    from helixscope.spec.models import Locus

    try:
        mission = mission_spec_from_fimo(
            fimo,
            genome=genome,
            locus=Locus(id="fimo_locus", coord=locus),
            title=title,
            source=source,
        )
    except FimoMotifParseError as exc:
        raise typer.BadParameter(str(exc)) from exc

    write_mission_spec(mission, out)
    console.print(f"[green]imported[/green] {len(mission.motifs)} motif(s) from {fimo}")
    console.print(f"  - {out}")


@motifs_app.command("import-table")
def import_table_motifs(
    table: Annotated[Path, typer.Argument(exists=True, readable=True, dir_okay=False)],
    locus: Annotated[str, typer.Option("--locus", help="Target locus, e.g. chr7:5500000-5502400.")],
    out: Annotated[Path, typer.Option("--out", "-o", help="MissionSpec YAML to write.")],
    genome: Annotated[str, typer.Option("--genome", help="Genome assembly label.")] = "hg38",
    title: Annotated[str | None, typer.Option("--title", help="Report title.")] = None,
    source: Annotated[
        str | None,
        typer.Option("--source", help="Provenance label stored on imported motifs."),
    ] = None,
    preset: Annotated[
        str,
        typer.Option("--preset", help="generic or all-motif."),
    ] = "generic",
    delimiter: Annotated[
        str | None,
        typer.Option("--delimiter", help="Column delimiter; use '\\t' for tab."),
    ] = None,
    coordinate_system: Annotated[
        str,
        typer.Option(
            "--coordinate-system",
            help="auto, zero-based-half-open, or one-based-inclusive.",
        ),
    ] = "auto",
    chrom_column: Annotated[str | None, typer.Option("--chrom-column")] = None,
    start_column: Annotated[str | None, typer.Option("--start-column")] = None,
    end_column: Annotated[str | None, typer.Option("--end-column")] = None,
    label_column: Annotated[str | None, typer.Option("--label-column")] = None,
    strand_column: Annotated[str | None, typer.Option("--strand-column")] = None,
    score_column: Annotated[str | None, typer.Option("--score-column")] = None,
) -> None:
    """Convert a tabular motif export into a minimal MissionSpec."""

    from helixscope.io.motifs.table import (
        CoordinateSystem,
        TableMotifParseError,
        TablePreset,
        mission_spec_from_table,
    )
    from helixscope.spec.loaders import write_mission_spec
    from helixscope.spec.models import Locus

    preset_value = _parse_choice(
        preset,
        choices={"generic", "all-motif"},
        name="table preset",
    )
    coordinate_value = None
    if coordinate_system != "auto":
        coordinate_value = _parse_choice(
            coordinate_system,
            choices={"zero-based-half-open", "one-based-inclusive"},
            name="coordinate system",
        )

    try:
        mission = mission_spec_from_table(
            table,
            genome=genome,
            locus=Locus(id="table_locus", coord=locus),
            title=title,
            source=source,
            preset=cast(TablePreset, preset_value),
            delimiter=delimiter,
            coordinate_system=cast(CoordinateSystem, coordinate_value)
            if coordinate_value is not None
            else None,
            chrom_column=chrom_column,
            start_column=start_column,
            end_column=end_column,
            label_column=label_column,
            strand_column=strand_column,
            score_column=score_column,
        )
    except TableMotifParseError as exc:
        raise typer.BadParameter(str(exc)) from exc

    write_mission_spec(mission, out)
    console.print(f"[green]imported[/green] {len(mission.motifs)} motif(s) from {table}")
    console.print(f"  - {out}")


@motifs_app.command("check-fimo")
def check_fimo_scanner(
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Emit machine-readable availability metadata."),
    ] = False,
) -> None:
    """Check whether the optional FIMO scanner executable is available."""

    from helixscope.io.motifs.fimo_scanner import check_fimo

    status = check_fimo()
    if json_output:
        print(
            json.dumps(
                {
                    "available": status.available,
                    "executable": status.executable,
                    "install_hint": status.install_hint,
                },
                sort_keys=True,
            )
        )
        return

    if status.available:
        console.print(f"[green]available[/green] fimo -> {status.executable}")
    else:
        console.print("[yellow]missing[/yellow] fimo executable was not found on PATH")
    console.print(f"  - {status.install_hint}")


@cli_app.command("validate")
def validate_spec(spec: SpecPath) -> None:
    """Validate a MissionSpec YAML/JSON file."""

    from helixscope.spec.loaders import load_mission_spec

    mission = load_mission_spec(spec)
    console.print(
        f"[green]valid[/green] {spec} -> {mission.report_type} "
        f"with {len(mission.loci)} locus/loci and {len(mission.tracks)} track(s)"
    )


@cli_app.command("render")
def render_spec(
    spec: SpecPath,
    out: OutDir,
    formats: FormatList = "png,html",
) -> None:
    """Render a validated MissionSpec to headless report artifacts."""

    from helixscope.render.static import render_report
    from helixscope.spec.loaders import load_mission_spec

    mission = load_mission_spec(spec)
    result = render_report(mission, out, _parse_formats(formats))
    console.print(f"[green]rendered[/green] {result.report_json}")
    for artifact in result.artifacts:
        console.print(f"  - {artifact}")


@cli_app.command("demo")
def demo(
    out: OutDir,
    formats: FormatList = "png,html",
) -> None:
    """Render a synthetic LocusProbe report to prove the headless stack works."""

    from helixscope.render.static import render_report
    from helixscope.spec.models import demo_mission_spec

    mission = demo_mission_spec()
    result = render_report(mission, out, _parse_formats(formats))
    console.print(f"[green]demo rendered[/green] {result.report_json}")
    for artifact in result.artifacts:
        console.print(f"  - {artifact}")


@cli_app.command("serve")
def serve(
    host: Host = "127.0.0.1",
    port: Port = 8000,
) -> None:
    """Start the optional FastAPI server for frontend exploration."""

    import uvicorn

    uvicorn.run("helixscope.server.app:app", host=host, port=port, reload=False)


def main() -> None:
    cli_app()
