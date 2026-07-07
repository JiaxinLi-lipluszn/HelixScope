UV_ENV := UV_PYTHON_DOWNLOADS=never UV_CACHE_DIR=.uv-cache MPLCONFIGDIR=.matplotlib-cache

.PHONY: env sync sync-bio lock-check test demo serve frontend-install frontend-build

env:
	mamba env create -f environment.yml

sync:
	$(UV_ENV) uv sync

sync-bio:
	$(UV_ENV) uv sync --extra bio --extra tables

lock-check:
	$(UV_ENV) uv lock --check

test:
	$(UV_ENV) uv run pytest

demo:
	$(UV_ENV) uv run helixscope demo --out outputs/demo

serve:
	$(UV_ENV) uv run helixscope serve --host 127.0.0.1 --port 8000

frontend-install:
	npm --cache .npm-cache --prefix frontend install

frontend-build:
	npm --cache .npm-cache --prefix frontend run build
