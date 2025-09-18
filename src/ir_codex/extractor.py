"""Extraction of chapters from the source PDF."""
from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Iterable, List

from pypdf import PdfReader

from .cleaner import clean_text
from .config import SOURCE_PDF
from .utils import ChapterRecord, slugify

logger = logging.getLogger(__name__)

_TITLE_PATTERN = re.compile(r"^[A-Z][A-Za-z0-9 ,\-\'\(\)/:&]+$")


def extract_chapters(pdf_path: str | Path = SOURCE_PDF) -> List[ChapterRecord]:
    """Read the PDF and segment its contents into numbered chapters."""
    logger.info("Extracting chapters from %s", pdf_path)
    reader = PdfReader(str(pdf_path))
    all_lines: list[str] = []
    for page_number, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text() or ""
        lines = [line.strip() for line in page_text.splitlines()]
        lines = [_filter_noise(line) for line in lines]
        lines = [line for line in lines if line is not None]
        all_lines.extend(lines)
        all_lines.append("")  # explicit page break to assist heuristics
        logger.debug("Loaded %d lines from page %d", len(lines), page_number)

    chapters: list[ChapterRecord] = []
    current_lines: list[str] = []
    current_number: int | None = None
    current_title: str | None = None

    idx = 0
    while idx < len(all_lines):
        line = all_lines[idx].strip()
        next_line = all_lines[idx + 1].strip() if idx + 1 < len(all_lines) else ""
        prev_line = all_lines[idx - 1].strip() if idx > 0 else ""

        if line.isdigit() and _looks_like_title(next_line) and not prev_line:
            number = int(line)
            title = next_line.strip()
            logger.debug("Detected chapter %s - %s", number, title)
            if current_number is not None and current_title is not None:
                chapters.append(_build_record(current_number, current_title, current_lines))
            current_number = number
            current_title = title
            current_lines = []
            idx += 2
            continue

        current_lines.append(all_lines[idx])
        idx += 1

    if current_number is not None and current_title is not None:
        chapters.append(_build_record(current_number, current_title, current_lines))

    if not chapters:
        raise RuntimeError("No chapters were detected in the PDF. Check extraction heuristics.")

    logger.info("Detected %d chapters", len(chapters))
    return chapters


def _filter_noise(line: str) -> str | None:
    if not line:
        return ""
    if re.fullmatch(r"Page \d+", line, flags=re.IGNORECASE):
        return None
    if line.strip().lower().startswith("international relations theory"):
        return None
    return line


def _looks_like_title(line: str) -> bool:
    if not line:
        return False
    if len(line) > 80:
        return False
    clean = line.strip()
    if clean.lower().startswith("www"):
        return False
    words = clean.split()
    if not words:
        return False
    uppercase_like = all(word[0].isupper() for word in words if any(ch.isalpha() for ch in word))
    return bool(_TITLE_PATTERN.match(clean)) or uppercase_like


def _build_record(number: int, title: str, lines: Iterable[str]) -> ChapterRecord:
    raw_body = "\n".join(lines).strip()
    body = clean_text(raw_body)
    final_text = f"{title}\n\n{body}" if body else title
    record = ChapterRecord(
        number=number,
        title=title,
        slug=slugify(f"{number}-{title}"),
        english_text=final_text.strip(),
    )
    logger.debug("Created record for chapter %s with %d characters", title, len(final_text))
    return record


__all__ = ["extract_chapters"]
