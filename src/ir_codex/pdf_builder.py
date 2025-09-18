"""PDF generation utilities."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Sequence

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, TableOfContents

from .utils import ChapterRecord

logger = logging.getLogger(__name__)


def build_chapter_pdf(chapter: ChapterRecord, output_path: Path) -> None:
    logger.info("Gerando PDF do capítulo %s", chapter.title)
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=25 * mm,
        rightMargin=25 * mm,
        topMargin=25 * mm,
        bottomMargin=25 * mm,
    )
    styles = _create_styles()
    story = _chapter_story(chapter, styles)
    doc.build(story, canvasmaker=NumberedCanvas)


def build_compiled_pdf(chapters: Sequence[ChapterRecord], output_path: Path) -> None:
    logger.info("Gerando PDF compilado em %s", output_path)
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=25 * mm,
        rightMargin=25 * mm,
        topMargin=25 * mm,
        bottomMargin=25 * mm,
    )
    styles = _create_styles()
    toc = TableOfContents()
    toc.levelStyles = [
        ParagraphStyle(
            name="TOCHeading",
            parent=styles["BodyText"],
            fontSize=11,
            leading=14,
            leftIndent=20,
            firstLineIndent=-15,
            spaceAfter=6,
        )
    ]

    story = [Paragraph("Sumário", styles["CodexTitle"]), Spacer(1, 12), toc, PageBreak()]

    for idx, chapter in enumerate(chapters):
        story.extend(_chapter_story(chapter, styles))
        if idx < len(chapters) - 1:
            story.append(PageBreak())

    doc.build(story, canvasmaker=NumberedCanvas)


def _chapter_story(chapter: ChapterRecord, styles: dict[str, ParagraphStyle]) -> list:
    story: list = []
    header = Paragraph(f"{chapter.number}. {chapter.title}", styles["ChapterTitle"])
    story.append(header)
    story.append(Spacer(1, 12))

    text = chapter.portuguese_text or ""
    paragraphs = text.split("\n\n") if text else []
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        story.append(Paragraph(paragraph.replace("\n", " "), styles["CodexBody"]))
        story.append(Spacer(1, 10))

    return story


def _create_styles() -> dict[str, ParagraphStyle]:
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="ChapterTitle",
            parent=styles["Heading1"],
            fontSize=18,
            leading=22,
            spaceAfter=12,
            textColor=colors.HexColor("#1A5276"),
            outlineLevel=0,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CodexBody",
            parent=styles["BodyText"],
            fontSize=11,
            leading=15,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CodexTitle",
            parent=styles["Title"],
            fontSize=22,
            leading=26,
            alignment=1,
            textColor=colors.HexColor("#154360"),
        )
    )
    return styles


class NumberedCanvas(canvas.Canvas):
    """Canvas with page numbers and optional TOC integration."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._saved_page_states: list[dict] = []

    def showPage(self) -> None:  # pragma: no cover - reportlab handles runtime
        self._saved_page_states.append(dict(self.__dict__))
        super().showPage()

    def save(self) -> None:  # pragma: no cover - reportlab handles runtime
        total_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self._draw_page_number(total_pages)
            super().showPage()
        super().save()

    def _draw_page_number(self, page_count: int) -> None:
        self.setFont("Helvetica", 9)
        self.drawRightString(200 * mm, 15 * mm, f"Página {self._pageNumber} de {page_count}")


__all__ = ["build_chapter_pdf", "build_compiled_pdf"]
