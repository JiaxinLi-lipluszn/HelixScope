# HelixScope

HelixScope is a headless-first genome visualization and reporting framework.

The stable core is a deterministic Python engine with a CLI and optional API
server. Agent skills sit above that engine: they collect scientific intent,
draft and validate a MissionSpec, then call the CLI to generate artifacts that
scientists can inspect on a headless server.

## Quick Start

Create the bootstrap environment:

```bash
mamba env create -f environment.yml
conda activate HelixScope_env
```

Install the Python project with uv:

```bash
UV_PYTHON_DOWNLOADS=never UV_CACHE_DIR=.uv-cache MPLCONFIGDIR=.matplotlib-cache uv sync
```

Install optional bio/table dependencies when implementing real file-backed
loaders:

```bash
UV_PYTHON_DOWNLOADS=never UV_CACHE_DIR=.uv-cache MPLCONFIGDIR=.matplotlib-cache uv sync --extra bio --extra tables
```

Generate a headless demo report:

```bash
UV_PYTHON_DOWNLOADS=never UV_CACHE_DIR=.uv-cache MPLCONFIGDIR=.matplotlib-cache uv run helixscope demo --out outputs/demo
```

Validate the minimal example:

```bash
UV_PYTHON_DOWNLOADS=never UV_CACHE_DIR=.uv-cache MPLCONFIGDIR=.matplotlib-cache uv run helixscope validate examples/minimal_locus_probe.yaml
```

Start the optional API server:

```bash
UV_PYTHON_DOWNLOADS=never UV_CACHE_DIR=.uv-cache MPLCONFIGDIR=.matplotlib-cache uv run helixscope serve --host 127.0.0.1 --port 8000
```

Build the optional frontend:

```bash
npm --cache .npm-cache --prefix frontend install
npm --cache .npm-cache --prefix frontend run build
```
