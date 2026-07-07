---
name: helixscope
description: Use HelixScope to turn biological signal visualization requests into validated MissionSpecs and deterministic headless reports. Trigger when a user asks for genome visualization, locus reports, biological track comparison, normalization-aware regulatory genomics plots, or agentic report generation with HelixScope.
---

# HelixScope

HelixScope is a skill-first workflow over a deterministic Python engine. Use the
skill to collect scientific intent, write a MissionSpec, validate it, then call
the CLI to generate artifacts the scientist can inspect on a headless server.

## Local editable install

When installed locally, prefer the editable symlink installer:

```bash
uv run helixscope skill install-local --env-name HelixScope_env
```

This links `$CODEX_HOME/skills/helixscope` to the repository's
`skills/helixscope` directory and writes `$CODEX_HOME/helixscope/config.yaml`.
If that config exists, read it first and treat `repo_root` and
`bootstrap_env_name` as authoritative. Run HelixScope commands from `repo_root`.
Prefer the configured repo-local CLI, usually `.venv/bin/helixscope`, because
headless non-interactive shells may not have `uv` on `PATH`. Use `uv` for
bootstrap or sync steps, but use the repo-local CLI for deterministic
validate/render/import commands once `.venv` exists. Because the skill is a
symlink and the Python project is installed editable by UV, local updates to
`SKILL.md` and `backend/src/helixscope` are picked up on the next skill load or
CLI run without reinstalling.

Treat the configured HelixScope environment as the default reproducibility
boundary, but allow cross-environment discovery. The agent may search the
server for candidate executables, conda environments, reference FASTA files,
motif databases, and existing annotation outputs. Discovery is not use:
executables from unrelated conda environments, global module loads, or
unregistered reference/motif database paths must not be executed or used in a
report until the user gives explicit consent in the conversation, or the
resource has been registered in HelixScope configuration. Codex sandbox/tool
approval, including any "approve for me" behavior, is only execution
permission; it does not count as scientific workflow consent.

## Core workflow

1. Clarify the biological question, genome build, loci, assays, files, sample
   metadata, desired controls, and final artifacts.
2. Draft a MissionSpec YAML. Prefer explicit coordinates and file paths.
   Motif annotations belong in `motifs`; each item should preserve provenance
   with `source` when known. The deterministic renderer expects absolute
   genomic `start`/`end`, `label`, optional `strand`, and optional `score`.
   Do not rewrite motif labels as preprocessing. Display labels should be
   human-readable TF or motif-family names when possible; accession IDs remain
   in the original label/source metadata.
3. If motif annotations are already provided as curated BED, FIMO TSV output,
   legacy `all_motif.csv`, or a simple generic table, do not parse them in the
   agent. Convert them through a deterministic importer first:

```bash
MPLCONFIGDIR=.matplotlib-cache .venv/bin/helixscope motifs import-bed path/to/motifs.bed --locus chr7:5500000-5502400 --genome hg38 --out outputs/report_name/spec.yaml --title "Motif annotations at chr7:5500000-5502400"
MPLCONFIGDIR=.matplotlib-cache .venv/bin/helixscope motifs import-fimo path/to/fimo.tsv --locus chr7:5500000-5502400 --genome hg38 --out outputs/report_name/spec.yaml --title "FIMO motif annotations at chr7:5500000-5502400"
MPLCONFIGDIR=.matplotlib-cache .venv/bin/helixscope motifs import-table path/to/all_motif.csv --preset all-motif --locus chr7:5500000-5502400 --genome hg38 --out outputs/report_name/spec.yaml --title "Motif annotations at chr7:5500000-5502400"
```

   Use `import-table --preset all-motif` for legacy all_motif exports. Use
   `--preset generic` with explicit `--chrom-column`, `--start-column`,
   `--end-column`, and `--label-column` only when the user provides a simple
   tabular annotation file. Avoid offering broad motif-suite or
   variant-effect workflows as normal HelixScope choices; keep those as
   upstream scientific analyses outside this skill.
4. If the user asks for motifs at a locus but provides no motif annotation
   file, explain that the renderer cannot infer motifs. Treat this as an
   optional FIMO scanning need, not a core HelixScope dependency. First check
   availability:

```bash
MPLCONFIGDIR=.matplotlib-cache .venv/bin/helixscope motifs check-fimo --json
```

   If FIMO is missing, ask before installing or downloading anything. The agent
   may search for existing FIMO installations in other environments and may
   search for local reference FASTA or motif databases, but those findings are
   candidates only. Offer clear choices: install MEME/FIMO into the configured
   HelixScope environment, explicitly reuse a discovered external FIMO/resource
   for this task, register that external resource for future tasks, or provide
   an existing BED/FIMO TSV/all_motif annotation file. Do not silently install
   FIMO from the skill. Do not execute a `fimo` binary from another conda
   environment, or use shared `/data1` reference resources, unless the user has
   explicitly consented in the conversation. If FIMO is available in the
   configured environment, still collect or confirm the reference FASTA and
   motif database path before scanning.
5. Validate before rendering:

```bash
MPLCONFIGDIR=.matplotlib-cache .venv/bin/helixscope validate path/to/spec.yaml
```

6. Render headless artifacts:

```bash
MPLCONFIGDIR=.matplotlib-cache .venv/bin/helixscope render path/to/spec.yaml --out outputs/report_name --formats png,html
```

7. Return the artifact paths and a cautious evidence summary. Do not invent
   biological conclusions beyond the available evidence.

## Motif annotation provenance

Motif annotations are not inferred by the renderer. They should come from an
upstream FIMO scan, a curated motif BED, or a legacy `all_motif.csv`-style
result table. When converting those outputs into MissionSpec, preserve the
source file or method in `source`; use absolute genomic coordinates; and treat
motif matches as sequence-compatibility annotations, not direct occupancy
evidence.

## Scientific guardrails

- Do not compare raw amplitudes across different TF ChIP tracks as absolute TF
  abundance.
- Do not share y-axes between assay families such as ATAC, ChIP, and model
  attribution unless the MissionSpec explicitly defines a valid normalization.
- Describe motif/track overlap as compatible with occupancy or localization,
  not proof of cooperation.
- Require perturbation, motif editing, co-occupancy, or dependency evidence
  before making cooperation or causality claims.
- Always include the normalization policy and caveats in the report summary.

## Implementation boundary

The backend and CLI are deterministic. The agent may ask questions and draft
MissionSpecs, but it should not put LLM reasoning inside the FastAPI server or
inside rendering code.
