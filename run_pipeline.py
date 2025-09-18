"""Command line entry point for the International Relations Codex pipeline."""
from __future__ import annotations

import argparse
import logging
from pathlib import Path

from ir_codex.config import SOURCE_PDF
from ir_codex.pipeline import run_all, run_extract, run_keywords, run_pdf, run_translate

LOGGER_FORMAT = "%(levelname)s: %(message)s"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Executa o pipeline do Codex de Relações Internacionais.")
    parser.add_argument(
        "command",
        choices=["extract", "translate", "keywords", "pdf", "all"],
        help="Passo do pipeline a ser executado.",
    )
    parser.add_argument(
        "--pdf",
        type=Path,
        default=None,
        help="Caminho alternativo para o PDF de origem ao executar a extração.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        help="Nível de logging (DEBUG, INFO, WARNING, ERROR).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    logging.basicConfig(level=args.log_level.upper(), format=LOGGER_FORMAT)

    if args.command == "extract":
        pdf_path = args.pdf or SOURCE_PDF
        run_extract(pdf_path)
    elif args.command == "translate":
        run_translate()
    elif args.command == "keywords":
        run_keywords()
    elif args.command == "pdf":
        run_pdf()
    elif args.command == "all":
        run_all()
    else:  # pragma: no cover - argparse already restricts choices
        raise ValueError(f"Comando desconhecido: {args.command}")


if __name__ == "__main__":
    main()
