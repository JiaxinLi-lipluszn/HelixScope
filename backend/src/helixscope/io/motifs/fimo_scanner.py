from __future__ import annotations

from dataclasses import dataclass
from shutil import which


@dataclass(frozen=True)
class FimoAvailability:
    available: bool
    executable: str | None
    install_hint: str


def check_fimo() -> FimoAvailability:
    """Report whether the optional FIMO scanner is available on PATH."""

    executable = which("fimo")
    if executable:
        return FimoAvailability(
            available=True,
            executable=executable,
            install_hint=(
                "FIMO is available; scanner workflows still need a reference "
                "FASTA and motif database."
            ),
        )
    return FimoAvailability(
        available=False,
        executable=None,
        install_hint=(
            "FIMO is optional and was not found in the active HelixScope "
            "environment. Install the MEME Suite, for example from bioconda as "
            "package 'meme', only when motif scanning is needed."
        ),
    )
