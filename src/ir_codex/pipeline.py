"""High level pipeline orchestration."""
from __future__ import annotations

import logging
from pathlib import Path

from .config import (
    CHAPTERS_DATA_PATH,
    CHAPTER_PDF_DIR,
    COMPILED_PDF_PATH,
    EN_TEXT_DIR,
    PT_TEXT_DIR,
    SOURCE_PDF,
    ensure_directories,
)
from .extractor import extract_chapters
from .keywords import KeywordGenerator
from .pdf_builder import build_chapter_pdf, build_compiled_pdf
from .translator import PortugueseTranslator
from .utils import ChapterRecord, load_chapter_records, save_chapter_records, strip_keywords_section

logger = logging.getLogger(__name__)


def run_extract(pdf_path: Path = SOURCE_PDF) -> list[ChapterRecord]:
    ensure_directories()
    chapters = extract_chapters(pdf_path)
    _cleanup_directory(EN_TEXT_DIR, suffix=".txt")
    for chapter in chapters:
        output_path = EN_TEXT_DIR / f"{chapter.number:02d}-{chapter.slug}.txt"
        output_path.write_text(chapter.english_text, encoding="utf-8")
        logger.debug("Saved raw chapter to %s", output_path)
    save_chapter_records(chapters, CHAPTERS_DATA_PATH)
    logger.info("Extração concluída: %d capítulos", len(chapters))
    return chapters


def run_translate(translator: PortugueseTranslator | None = None) -> list[ChapterRecord]:
    ensure_directories()
    chapters = load_chapter_records(CHAPTERS_DATA_PATH)
    translator = translator or PortugueseTranslator()
    _cleanup_directory(PT_TEXT_DIR, suffix=".txt")
    for chapter in chapters:
        translated = translator.translate_text(chapter.english_text)
        chapter.portuguese_text = translated
        output_path = PT_TEXT_DIR / f"{chapter.number:02d}-{chapter.slug}.txt"
        output_path.write_text(translated, encoding="utf-8")
        logger.debug("Translated chapter %s", chapter.title)
    save_chapter_records(chapters, CHAPTERS_DATA_PATH)
    logger.info("Tradução concluída para %d capítulos", len(chapters))
    return chapters


def run_keywords(translator: PortugueseTranslator | None = None) -> list[ChapterRecord]:
    ensure_directories()
    chapters = load_chapter_records(CHAPTERS_DATA_PATH)
    translator = translator or PortugueseTranslator()
    generator = KeywordGenerator(translator)
    for chapter in chapters:
        if not chapter.portuguese_text:
            raise RuntimeError(
                f"Capítulo {chapter.number} sem tradução. Execute o passo de tradução antes das palavras-chave."
            )
        keywords = generator.generate(chapter.english_text)
        chapter.keywords = keywords
        text = strip_keywords_section(chapter.portuguese_text)
        if keywords:
            keyword_line = "Palavras-chave: " + "; ".join(f"{pt} ({en})" for pt, en in keywords)
            text = f"{text}\n\n{keyword_line}" if text else keyword_line
        chapter.portuguese_text = text
        output_path = PT_TEXT_DIR / f"{chapter.number:02d}-{chapter.slug}.txt"
        output_path.write_text(text, encoding="utf-8")
        logger.debug("Keywords criadas para %s", chapter.title)
    save_chapter_records(chapters, CHAPTERS_DATA_PATH)
    logger.info("Palavras-chave geradas para %d capítulos", len(chapters))
    return chapters


def run_pdf() -> None:
    ensure_directories()
    chapters = load_chapter_records(CHAPTERS_DATA_PATH)
    missing = [chapter.title for chapter in chapters if not chapter.portuguese_text]
    if missing:
        raise RuntimeError(
            "Alguns capítulos não estão traduzidos: " + ", ".join(missing)
        )
    _cleanup_directory(CHAPTER_PDF_DIR, suffix=".pdf")
    CHAPTER_PDF_DIR.mkdir(parents=True, exist_ok=True)
    for chapter in chapters:
        pdf_path = CHAPTER_PDF_DIR / f"{chapter.number:02d}-{chapter.slug}.pdf"
        build_chapter_pdf(chapter, pdf_path)
    COMPILED_PDF_PATH.parent.mkdir(parents=True, exist_ok=True)
    build_compiled_pdf(chapters, COMPILED_PDF_PATH)
    logger.info("PDFs gerados em %s", CHAPTER_PDF_DIR)


def run_all() -> None:
    ensure_directories()
    run_extract()
    translator = PortugueseTranslator()
    run_translate(translator=translator)
    run_keywords(translator=translator)
    run_pdf()
    logger.info("Pipeline completo concluído.")


def _cleanup_directory(directory: Path, suffix: str) -> None:
    if not directory.exists():
        return
    for item in directory.iterdir():
        if item.is_file() and item.name.endswith(suffix):
            item.unlink()


__all__ = ["run_all", "run_extract", "run_keywords", "run_pdf", "run_translate"]
