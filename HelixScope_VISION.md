# HelixScope Vision

> **HelixScope** is a skill-first biological visualization and reporting system for agentic coding workflows.
>
> It turns natural-language biological questions into validated analysis specs, normalized and aligned visual reports, dynamic control panels, and evidence-based preliminary interpretations.

## 1. The problem

Biological visualization tools are powerful, but they are still mostly designed around manual operation: users choose tracks, configure panels, remember normalization caveats, align data by hand, and then write their own interpretation. This creates a gap between what scientists actually ask and what existing tools directly provide.

A scientist usually starts with a biological question:

> Compare FOXA2, GATA4, ATAC, H3K27ac, and model attribution around the Alb enhancer in liver and non-liver contexts. Normalize the data appropriately, generate controls, and tell me whether this supports a pioneer-factor/cooperation story.

Existing tools can render tracks, but they generally do not own the full workflow:

- understanding the biological intent;
- validating genome builds, coordinates, samples, and metadata;
- choosing a defensible normalization strategy;
- generating dynamic control comparisons;
- aligning heterogeneous tracks, variants, motifs, model attributions, and perturbation outputs;
- producing a report with preliminary evidence statements and caveats.

HelixScope exists to fill that gap.

## 2. Core mission

**HelixScope is not just a plotting library and not just a genome browser.**

It is an **agent-friendly biological visualization skill**: a structured system that teaches coding agents how to transform biological questions into reproducible visual analysis reports.

The core promise is:

> **Ask a biological signal question. Get a validated report, not just a plot.**

HelixScope should help a scientist move from:

```text
natural language question
```

to:

```text
validated mission spec
+ normalized data comparison
+ interactive report
+ dynamic controls
+ evidence statements
+ caveats
```

without forcing the scientist to manually assemble every visualization and comparison from scratch.

## 3. Why “skill-first”

HelixScope should be framed first as a **Codex / Claude Code skill**, then as a Python package and optional web interface.

This matters because the main value is not only code execution. The main value is **workflow judgment**:

- how to compare biological tracks without making invalid quantitative claims;
- how to choose controls;
- how to decide whether cross-TF ChIP amplitudes should be compared;
- how to convert a scientific question into a structured plan;
- how to generate a report that is reproducible and biologically cautious.

Agent skills are well-suited for this because they can package instructions, scripts, schemas, templates, examples, and biological policy documents into a reusable workflow. Claude Agent Skills are explicitly organized as modular capabilities with instructions and optional resources such as scripts and templates, and public skill examples are folder-based bundles of instructions, scripts, and resources. Codex similarly supports repository-level guidance through `AGENTS.md`, which it reads before beginning work.

HelixScope should therefore be designed as:

```text
HelixScope Skill
  + HelixScope Python engine
  + HelixScope Spec schema
  + report templates
  + normalization policies
  + renderer adapters
```

not merely:

```text
plot_track(...)
```

## 4. Design philosophy

### 4.1 Agentic, but not magical

HelixScope should accept natural-language requests, but every agent-generated action must compile into a validated spec before execution.

The workflow should be:

```text
Natural language
  → HelixScope MissionSpec
  → validation
  → analysis plan
  → execution
  → report spec
  → rendered report
```

The agent should not directly generate ad hoc visualization code or unsupported biological conclusions.

### 4.2 Biological caution is part of the product

HelixScope should automatically prevent common interpretive mistakes.

Examples:

- Different TF ChIP-seq tracks should not be compared by raw signal height as though they were absolute binding abundances.
- ATAC and ChIP tracks should not share a y-axis as if they were the same measurement.
- Model attribution and experimental occupancy should be compared by localization/rank/overlap, not by raw amplitude.
- Co-localized ChIP peaks should be described as co-occupancy-compatible, not proof of cooperation.
- Cooperation should require perturbation, motif-edit, co-occupancy, or dependency evidence.

These caveats should be encoded as machine-readable policies, not remembered casually.

### 4.3 Renderer-agnostic, biology-aware

HelixScope should not try to replace mature visualization engines. Instead, it should compile biological reports into renderer-specific specs.

Potential rendering backends:

- **Gosling / Gosling.js** for scalable, linked, interactive genomics tracks;
- **HiGlass** for multiscale genome tracks and 2D contact maps;
- **Vitessce** for single-cell, spatial, and multimodal linked views;
- **Vega-Lite / Observable Plot / Recharts** for QC plots, summary charts, and report-level statistics;
- static HTML or notebook exports for reproducibility.

The unique layer is the biological orchestration above these renderers.

### 4.4 Reports over screenshots

A HelixScope output should be a report artifact, not just an image.

A report should include:

- interactive figures;
- sample metadata;
- normalization choices;
- control comparisons;
- evidence statements;
- caveats;
- exported specs;
- reproducibility metadata.

## 5. Product identity

### Name

**HelixScope**

### Taglines

- **Mission control for biological signals.**
- **Ask biological data a question; launch a report.**
- **An agentic visualization skill for biological signal worlds.**

### Naming system

```text
HelixScope      = overall skill-first project
MissionSpec     = validated YAML/JSON analysis request
TrackArray      = track loading, alignment, and tiling layer
NormCore        = normalization and comparison policy engine
ControlDeck     = dynamic control experiment generator
LocusProbe      = locus-level report module
EvidenceRelay   = structured evidence statements and caveats
ScopeView       = interactive visualization/report front end
```

## 6. Target users

HelixScope is for scientists and agents working with heterogeneous biological data:

- computational biologists inspecting regulatory genomics results;
- model developers comparing sequence model attribution with experimental tracks;
- single-cell analysts generating locus/cell-state reports;
- wet-lab collaborators who need readable evidence summaries;
- AI coding agents that need a disciplined way to build biological visualizations.

The first target user is a scientist asking:

> I have tracks, model outputs, motifs, and variants. Help me make a biologically valid report.

## 7. Initial scope

HelixScope v0.1 should focus on **regulatory genomics locus reports**, because this is where the need for track alignment, normalization, motifs, variants, model attribution, and biological caveats is especially acute.

### v0.1 supported inputs

- `bigWig` / `bedGraph` signal tracks;
- `BED`, `narrowPeak`, `broadPeak` interval tracks;
- motif instances in `BED` or tabular form;
- `VCF` / variant tables;
- model attribution tracks or tables;
- model variant-effect tables;
- sample metadata in `CSV`, `YAML`, or `JSON`;
- locus definitions in `BED` or YAML.

### v0.1 report types

1. **LocusProbe report**
   - tracks around one or more loci;
   - motifs and variants;
   - model attribution;
   - normalized track summaries;
   - preliminary biological interpretation.

2. **ControlDeck report**
   - target locus vs matched background loci;
   - condition A vs condition B;
   - before/after perturbation;
   - motif-containing vs motif-disrupted loci;
   - case vs control cell type.

3. **Variant report**
   - reference/alternative model prediction;
   - MPRA or variant-effect measurement if available;
   - motif disruption/creation;
   - cell-type-specific trans context summary.

4. **Model attribution report**
   - attribution track visualization;
   - motif-centered aggregation;
   - comparison to ChIP/CUT&RUN/ATAC evidence;
   - caveats about amplitude interpretation.

## 8. Non-goals for v0.1

HelixScope v0.1 should not try to be everything.

It should not initially be:

- a full replacement for IGV, UCSC, JBrowse, Gosling, HiGlass, or Vitessce;
- a complete cloud multi-user platform;
- a general-purpose single-cell dashboard;
- a full spatial transcriptomics viewer;
- an automatic causal discovery system;
- a biological oracle.

It should instead be a reliable, extensible, agentic reporting layer.

## 9. Core workflow

### 9.1 Natural-language request

Example:

```text
Compare FOXA2, GATA4, ATAC, and model attribution around the mouse Alb enhancer. Use liver and non-liver controls. Normalize appropriately and tell me whether the pattern supports a pioneer-factor cooperation story.
```

### 9.2 Intent parsing

The skill identifies:

```yaml
task: locus_report
biological_question: pioneer_factor_cooperation
locus: mouse Alb enhancer
factors: [FOXA2, GATA4]
assays: [ChIP-seq, ATAC-seq, model_attribution]
comparison: [liver, non_liver]
required_outputs:
  - tracks
  - controls
  - normalization_card
  - evidence_summary
```

### 9.3 MissionSpec generation

```yaml
version: 0.1
report_type: locus_probe
title: Alb enhancer FOXA/GATA pioneer-factor report
genome: mm10

loci:
  - id: alb_enhancer
    label: Alb far-upstream enhancer
    coord: chr5:START-END

tracks:
  - id: foxa2_liver
    type: tf_occupancy
    factor: FOXA2
    assay: ChIP-seq
    file: data/foxa2_liver.bw
    cell_type: liver
  - id: gata4_liver
    type: tf_occupancy
    factor: GATA4
    assay: ChIP-seq
    file: data/gata4_liver.bw
    cell_type: liver
  - id: atac_liver
    type: accessibility
    assay: ATAC-seq
    file: data/atac_liver.bw
    cell_type: liver
  - id: model_attr
    type: model_attribution
    file: results/alb_attr.bw
    model: user_model

comparisons:
  - id: liver_vs_non_liver
    type: condition_contrast
  - id: foxa_gata_colocalization
    type: motif_centered_alignment
    factors: [FOXA2, GATA4]

normalization:
  policy: auto
  disallow:
    - raw_cross_tf_amplitude_comparison
  prefer:
    - within_track_percentile
    - motif_centered_enrichment
    - matched_control_loci

outputs:
  - interactive_locus_tracks
  - normalization_card
  - control_deck
  - evidence_summary
```

### 9.4 Validation

HelixScope checks:

- Are all coordinates in the same genome build?
- Are track files readable?
- Are sample metadata fields complete?
- Are comparisons biologically valid?
- Are replicates available?
- Is the user asking for an invalid amplitude comparison?
- Are required control loci available or should they be generated?

### 9.5 Execution

The analysis engine runs:

- track summarization over loci;
- local signal extraction;
- motif-centered aggregation;
- summit alignment;
- replicate correlation;
- matched control selection;
- delta track generation;
- evidence statement construction.

### 9.6 Report generation

The final report includes:

- interactive track panels;
- control panels;
- QC charts;
- normalization explanation;
- preliminary interpretation;
- caveats;
- downloadable specs and tables.

## 10. Normalization policy

Normalization is a first-class concept in HelixScope.

HelixScope should include a `NormCore` module that recommends, applies, and explains normalization choices.

### Example policies

| Comparison request | Default HelixScope behavior |
|---|---|
| Same TF, same assay, different conditions | Allow comparison after library-size/spike-in-aware/replicate-aware normalization. |
| Different TF ChIP tracks in same cell type | Do not compare raw amplitude. Use peak support, within-track percentile, motif-centered enrichment, or occupancy presence/absence. |
| ATAC vs ChIP | Show aligned panels but do not share y-axis or imply comparable units. |
| Model attribution vs ChIP | Compare localization, rank, or motif-centered enrichment, not raw amplitude. |
| Replicates | Check replicate consistency before aggregation. |
| Perturbation before/after | Generate delta tracks and matched controls; report effect size and uncertainty. |
| Variant ref/alt | Report predicted model delta, motif disruption, and experimental effect if available. |

The report should always include a **Normalization Card** explaining what was done and what should not be inferred.

## 11. Evidence statements

HelixScope should generate structured evidence statements before generating prose.

Example:

```json
{
  "claim": "FOXA2 and GATA4 show co-localized occupancy over the Alb enhancer interval.",
  "support": ["foxa2_liver_peak_overlap", "gata4_liver_peak_overlap"],
  "confidence": "occupancy-supported",
  "caveat": "Co-localized ChIP peaks do not prove cooperative binding without perturbation, motif editing, or co-occupancy assays."
}
```

The natural-language report should be derived from these structured objects.

This prevents the agent from inventing biological conclusions beyond the data.

## 12. Architecture

```text
                    ┌───────────────────────────┐
                    │ User / agent prompt        │
                    └─────────────┬─────────────┘
                                  ↓
                    ┌───────────────────────────┐
                    │ HelixScope Skill           │
                    │ SKILL.md + examples        │
                    └─────────────┬─────────────┘
                                  ↓
                    ┌───────────────────────────┐
                    │ MissionSpec                │
                    │ validated YAML/JSON        │
                    └─────────────┬─────────────┘
                                  ↓
        ┌─────────────────────────┴─────────────────────────┐
        ↓                                                   ↓
┌───────────────────────┐                         ┌───────────────────────┐
│ Python analysis engine │                         │ Renderer compiler      │
│ tracks / intervals / QC│                         │ Gosling / Vega / HTML  │
└───────────┬───────────┘                         └───────────┬───────────┘
            └───────────────────┬─────────────────────────────┘
                                ↓
                    ┌───────────────────────────┐
                    │ Evidence-based report      │
                    │ figures + caveats + text   │
                    └───────────────────────────┘
```

## 13. Repository structure

```text
helixscope/
  README.md
  VISION.md
  AGENTS.md
  CLAUDE.md

  skills/
    helixscope/
      SKILL.md
      schemas/
        mission_spec.schema.json
        track.schema.json
        comparison.schema.json
        normalization.schema.json
      scripts/
        validate_spec.py
        summarize_tracks.py
        normalize_tracks.py
        motif_centered_signal.py
        matched_control_loci.py
        render_report.py
      resources/
        normalization_policies.md
        biological_caveats.md
        supported_formats.md
        report_templates/
          locus_probe.md
          control_deck.md
          variant_report.md
      examples/
        alb_enhancer_pioneer.yaml
        k562_gata_tal1.yaml
        translOOM_variant.yaml

  helixscope/
    __init__.py
    spec/
      schema.py
      validators.py
    io/
      bigwig.py
      bed.py
      vcf.py
      motifs.py
      metadata.py
    normalize/
      advisor.py
      policies.py
    analysis/
      locus_summary.py
      motif_alignment.py
      control_matching.py
      replicate_qc.py
      differential_signal.py
    render/
      gosling.py
      vega.py
      report.py
    agent/
      intent_schema.py
      planner.py
      safety_checks.py
    server/
      api.py

  frontend/
    app/
    components/
      LocusProbe.tsx
      ControlDeck.tsx
      NormalizationCard.tsx
      EvidenceRelay.tsx

  examples/
    alb_enhancer/
    translOOM_variant/
    k562_gata1_tal1/
```

## 14. Implementation stack

### Backend

- Python first.
- Optional Rust later for performance-critical tiling and interval aggregation.

Suggested libraries:

- `pydantic` for schema validation;
- `polars`, `pandas`, `pyarrow`, `duckdb` for tabular data;
- `bioframe`, `pyranges` for genomic intervals;
- `pyBigWig` for bigWig signal extraction;
- `pysam` for BAM/CRAM support;
- `cooler` for contact maps;
- `anndata`, `mudata` for future single-cell/multi-omics support;
- `fastapi` for an optional report server.

### Frontend

- React / Next.js / TypeScript;
- Gosling.js for genome tracks;
- HiGlass for contact maps;
- Vitessce for future single-cell and spatial views;
- Vega-Lite / Observable Plot / Recharts for QC charts;
- static HTML report export for reproducibility.

## 15. Skill behavior rules

When invoked, the HelixScope skill should:

1. Parse the biological question into a structured intent.
2. Identify loci, tracks, samples, assays, conditions, and requested comparisons.
3. Check genome build and coordinate compatibility.
4. Validate file availability and metadata completeness.
5. Choose a normalization policy and state why.
6. Refuse or rewrite invalid comparisons.
7. Generate controls when appropriate.
8. Produce a validated MissionSpec.
9. Run analysis scripts.
10. Compile renderer specs.
11. Generate evidence statements.
12. Write a concise report with caveats.

## 16. Scientific guardrails

HelixScope must avoid overclaiming.

It should distinguish:

- visualization from inference;
- co-localization from cooperation;
- occupancy from causality;
- signal enrichment from abundance;
- motif compatibility from TF identity;
- model attribution from experimental evidence.

Reports should use cautious language such as:

- “consistent with”;
- “supports occupancy evidence”;
- “co-localization-compatible”;
- “requires perturbation evidence to establish cooperation”;
- “not quantitatively comparable across TFs by raw amplitude.”

## 17. First demonstration cases

### 17.1 Alb enhancer pioneer-factor report

Question:

> Do FOXA/GATA tracks and accessibility around the mouse Alb enhancer support a pioneer-factor/cooperation story?

Data:

- FOXA2 ChIP/CUT&RUN;
- GATA4 ChIP/CUT&RUN;
- ATAC/DNase;
- motif instances;
- optional model attribution;
- liver vs non-liver controls.

Output:

- LocusProbe report;
- Normalization Card;
- motif-centered FOXA/GATA signal summary;
- caveat that co-localization is not proof of cooperation.

### 17.2 TransLoom variant report

Question:

> For a regulatory variant, does the model predict the right effect direction and the right affected TF-family context?

Data:

- variant table;
- MPRA or saturation MPRA effect;
- ref/alt model predictions;
- motif disruption;
- TF expression / occupancy evidence.

Output:

- variant effect card;
- motif disruption summary;
- model-vs-experiment comparison;
- trans-context evidence summary.

### 17.3 K562 GATA/TAL1 enhancer report

Question:

> Do GATA1, TAL1, ATAC, and model attribution align at erythroid enhancers?

Data:

- K562 TF tracks;
- ATAC;
- enhancer BED;
- motif instances;
- attribution tracks.

Output:

- enhancer panel;
- motif-centered aggregation;
- matched control comparison;
- preliminary evidence statements.

## 18. Roadmap

### v0.1: Skill-first static reports

- `AGENTS.md`
- `skills/helixscope/SKILL.md`
- MissionSpec schema
- Python backend for bigWig/BED/VCF/motif data
- static HTML report generator
- Normalization Card
- LocusProbe and ControlDeck reports

### v0.2: Natural-language spec drafting

- `helixscope ask` command;
- natural-language to draft MissionSpec;
- validation loop;
- editable YAML output.

### v0.3: Interactive web viewer

- React/Next.js frontend;
- Gosling.js renderer;
- report viewer;
- downloadable JSON/YAML specs.

### v0.4: Multimodal expansion

- HiGlass contact maps;
- AnnData / single-cell panels;
- Vitessce integration;
- spatial support.

### v0.5: Plugin ecosystem

- TransLoom adapter;
- ArchR adapter;
- SCENIC+ / LINGER adapters;
- custom renderer plugins;
- custom normalization policies.

## 19. Success criteria

HelixScope succeeds if a scientist can say:

> Compare these biological signals, choose sane normalization, generate controls, and write a cautious report.

and receive:

- a validated spec;
- a reproducible report;
- accurate visualizations;
- transparent normalization choices;
- meaningful controls;
- preliminary interpretation;
- no overclaimed biology.

## 20. References and design inspirations

- Claude Agent Skills package instructions, metadata, scripts, and templates into modular capabilities: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- Anthropic public skills repository describes skills as folders of instructions, scripts, and resources: https://github.com/anthropics/skills
- Codex supports repository-level guidance through `AGENTS.md`: https://developers.openai.com/codex/guides/agents-md
- `AGENTS.md` is described as a README-like instruction file for coding agents: https://agents.md/
- Gosling is a grammar-based toolkit for scalable, linked, interactive genomics visualization: https://pmc.ncbi.nlm.nih.gov/articles/PMC8826597/
- HiGlass supports multiscale navigation of 2D genome maps alongside 1D tracks: https://pmc.ncbi.nlm.nih.gov/articles/PMC6109259/
- Vitessce is a relevant inspiration for multimodal and spatial single-cell linked views: https://vitessce.io/
