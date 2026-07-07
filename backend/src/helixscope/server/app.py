from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from helixscope import __version__

app = FastAPI(title="HelixScope", version=__version__)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "helixscope-backend", "version": __version__}


@app.get("/reports/demo-metadata")
def demo_metadata() -> dict[str, object]:
    return {
        "report_type": "locus_probe",
        "headless_first": True,
        "artifacts": ["locus_probe.png", "locus_probe.html", "report.json"],
    }
