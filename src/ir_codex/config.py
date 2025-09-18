"""Project configuration and filesystem paths."""
from __future__ import annotations

from pathlib import Path


def _resolve_repo_root() -> Path:
    """Return the repository root based on this file location."""
    current = Path(__file__).resolve()
    # __file__ -> .../src/ir_codex/config.py -> parents[0]=..., [1]=src, [2]=repo
    for parent in current.parents:
        if (parent / "data").exists() and (parent / "International-Relations-Theory-E-IR.pdf").exists() or (
            parent / "data" / "International-Relations-Theory-E-IR.pdf"
        ).exists():
            return parent
    # fallback to two levels up
    return current.parents[2]


REPO_ROOT: Path = _resolve_repo_root()
DATA_DIR: Path = REPO_ROOT / "data"
SOURCE_PDF: Path = DATA_DIR / "International-Relations-Theory-E-IR.pdf"
OUTPUT_DIR: Path = REPO_ROOT / "output"
CHAPTERS_DATA_PATH: Path = OUTPUT_DIR / "chapters.json"
EN_TEXT_DIR: Path = OUTPUT_DIR / "chapters_en"
PT_TEXT_DIR: Path = OUTPUT_DIR / "chapters_pt"
PDF_DIR: Path = OUTPUT_DIR / "pdf"
CHAPTER_PDF_DIR: Path = PDF_DIR / "capitulos"
COMPILED_PDF_PATH: Path = PDF_DIR / "compilado.pdf"


def ensure_directories() -> None:
    """Create the output directories that the pipeline expects."""
    for path in (
        OUTPUT_DIR,
        EN_TEXT_DIR,
        PT_TEXT_DIR,
        PDF_DIR,
        CHAPTER_PDF_DIR,
    ):
        path.mkdir(parents=True, exist_ok=True)


__all__ = [
    "REPO_ROOT",
    "DATA_DIR",
    "SOURCE_PDF",
    "OUTPUT_DIR",
    "CHAPTERS_DATA_PATH",
    "EN_TEXT_DIR",
    "PT_TEXT_DIR",
    "PDF_DIR",
    "CHAPTER_PDF_DIR",
    "COMPILED_PDF_PATH",
    "ensure_directories",
]
