"""Translation helpers powered by Hugging Face transformers."""
from __future__ import annotations

import logging
import re
from typing import Iterable, List, Sequence

logger = logging.getLogger(__name__)


def _resolve_device() -> int:
    try:
        import torch

        if torch.cuda.is_available():
            return 0
    except Exception:  # pragma: no cover - torch might be absent during tests
        logger.debug("Torch not available, using CPU for translations")
    return -1


class PortugueseTranslator:
    """Translate English prose and keywords into European Portuguese."""

    def __init__(
        self,
        model_name: str = "Helsinki-NLP/opus-mt-en-pt",
        device: int | None = None,
        max_chunk_chars: int = 400,
    ) -> None:
        self.model_name = model_name
        self.device = _resolve_device() if device is None else device
        self.max_chunk_chars = max_chunk_chars
        self._pipeline = None

    def _get_pipeline(self):
        if self._pipeline is None:
            from transformers import pipeline

            logger.info("Loading translation model %s", self.model_name)
            self._pipeline = pipeline("translation", model=self.model_name, device=self.device)
        return self._pipeline

    def translate_paragraph(self, text: str) -> str:
        translator = self._get_pipeline()
        text = text.strip()
        if not text:
            return ""
        chunks = list(_chunk_text(text, self.max_chunk_chars))
        logger.debug("Translating paragraph in %d chunks", len(chunks))
        results = translator(chunks, max_length=512)
        translated = " ".join(item["translation_text"].strip() for item in results)
        return _normalize_spacing(translated)

    def translate_text(self, text: str) -> str:
        paragraphs = text.split("\n\n")
        translated_paragraphs: list[str] = []
        for paragraph in paragraphs:
            translated_paragraphs.append(self.translate_paragraph(paragraph))
        return "\n\n".join(part for part in translated_paragraphs).strip()

    def translate_keywords(self, keywords: Sequence[str]) -> List[str]:
        translator = self._get_pipeline()
        cleaned = [kw.strip() for kw in keywords if kw.strip()]
        if not cleaned:
            return []
        logger.debug("Translating %d keywords", len(cleaned))
        results = translator(cleaned, max_length=128)
        return [_normalize_spacing(item["translation_text"]) for item in results]


def _chunk_text(text: str, max_chars: int) -> Iterable[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunk = ""
    for sentence in sentences:
        if not sentence:
            continue
        prospective = f"{chunk} {sentence}".strip()
        if len(prospective) <= max_chars or not chunk:
            chunk = prospective
            continue
        yield chunk
        chunk = sentence.strip()
    if chunk:
        yield chunk.strip()


def _normalize_spacing(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


__all__ = ["PortugueseTranslator"]
