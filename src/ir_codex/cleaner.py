"""Text cleaning utilities for the pipeline."""
from __future__ import annotations

import re
from typing import Iterable


_WHITESPACE_RE = re.compile(r"\s+")


def normalize_line(line: str) -> str:
    """Collapse repeated whitespace and strip side spaces."""
    line = line.replace("\u00a0", " ")
    line = line.replace("\ufeff", "")
    line = line.strip()
    line = _WHITESPACE_RE.sub(" ", line)
    return line


def clean_text(text: str) -> str:
    """Clean hyphenations and wrap text into paragraphs."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [normalize_line(line) for line in text.split("\n")]

    cleaned_lines: list[str] = []
    for line in lines:
        if not line:
            if cleaned_lines and cleaned_lines[-1] != "":
                cleaned_lines.append("")
            continue
        cleaned_lines.append(line)

    paragraphs: list[str] = []
    buffer: list[str] = []

    for line in cleaned_lines:
        if not line:
            if buffer:
                paragraphs.append(_merge_buffer(buffer))
                buffer = []
            continue
        if buffer and buffer[-1].endswith("-") and line[:1].islower():
            buffer[-1] = buffer[-1][:-1] + line
        else:
            buffer.append(line)

    if buffer:
        paragraphs.append(_merge_buffer(buffer))

    cleaned_text = "\n\n".join(paragraphs)
    return cleaned_text.strip()


def _merge_buffer(lines: Iterable[str]) -> str:
    parts: list[str] = []
    for part in lines:
        if not part:
            continue
        if parts and parts[-1].endswith("-"):
            parts[-1] = parts[-1][:-1] + part
        else:
            parts.append(part)
    return " ".join(parts)


__all__ = ["clean_text", "normalize_line"]
