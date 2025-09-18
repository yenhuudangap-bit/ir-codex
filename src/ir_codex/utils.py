"""Utility helpers for the International Relations Codex pipeline."""
from __future__ import annotations

import json
import logging
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List, Sequence

logger = logging.getLogger(__name__)


_SLUG_CLEAN_RE = re.compile(r"[^a-z0-9-]+")


def slugify(value: str) -> str:
    """Create a filesystem-friendly slug from a title."""
    value = value.lower().strip()
    value = re.sub(r"['\"]", "", value)
    value = re.sub(r"[\s_/]+", "-", value)
    value = _SLUG_CLEAN_RE.sub("", value)
    value = value.strip("-")
    return value or "capitulo"


@dataclass
class ChapterRecord:
    """Structured representation of a chapter along the pipeline."""

    number: int
    title: str
    slug: str
    english_text: str
    portuguese_text: str | None = None
    keywords: List[tuple[str, str]] | None = None

    def to_dict(self) -> dict:
        data = asdict(self)
        data["keywords"] = [
            {"pt": pt, "en": en}
            for pt, en in (self.keywords or [])
        ]
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "ChapterRecord":
        keywords = data.get("keywords") or []
        keyword_pairs = [(item["pt"], item["en"]) for item in keywords]
        return cls(
            number=int(data["number"]),
            title=data["title"],
            slug=data["slug"],
            english_text=data["english_text"],
            portuguese_text=data.get("portuguese_text"),
            keywords=keyword_pairs or None,
        )


def save_chapter_records(records: Sequence[ChapterRecord], path: Path) -> None:
    logger.debug("Saving chapter metadata to %s", path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = [record.to_dict() for record in records]
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def load_chapter_records(path: Path) -> list[ChapterRecord]:
    if not path.exists():
        raise FileNotFoundError(f"Metadata file not found: {path}")
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [ChapterRecord.from_dict(item) for item in raw]


def strip_keywords_section(text: str) -> str:
    """Remove an existing keywords section if present."""
    return re.sub(r"\n\nPalavras-chave:.*\Z", "", text, flags=re.S)


__all__ = [
    "ChapterRecord",
    "load_chapter_records",
    "save_chapter_records",
    "slugify",
    "strip_keywords_section",
]
