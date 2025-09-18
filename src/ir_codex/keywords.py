"""Keyword extraction for each chapter."""
from __future__ import annotations

import logging
import re
from collections import Counter
from typing import Iterable, List, Tuple

from .translator import PortugueseTranslator

logger = logging.getLogger(__name__)

_STOPWORDS = {
    "a",
    "about",
    "above",
    "after",
    "again",
    "against",
    "all",
    "am",
    "an",
    "and",
    "any",
    "are",
    "aren't",
    "as",
    "at",
    "be",
    "because",
    "been",
    "before",
    "being",
    "below",
    "between",
    "both",
    "but",
    "by",
    "can",
    "cannot",
    "could",
    "couldn't",
    "did",
    "didn't",
    "do",
    "does",
    "doesn't",
    "doing",
    "don't",
    "down",
    "during",
    "each",
    "few",
    "for",
    "from",
    "further",
    "had",
    "hadn't",
    "has",
    "hasn't",
    "have",
    "haven't",
    "having",
    "he",
    "he'd",
    "he'll",
    "he's",
    "her",
    "here",
    "here's",
    "hers",
    "herself",
    "him",
    "himself",
    "his",
    "how",
    "how's",
    "i",
    "i'd",
    "i'll",
    "i'm",
    "i've",
    "if",
    "in",
    "into",
    "is",
    "isn't",
    "it",
    "it's",
    "its",
    "itself",
    "let's",
    "me",
    "more",
    "most",
    "mustn't",
    "my",
    "myself",
    "no",
    "nor",
    "not",
    "of",
    "off",
    "on",
    "once",
    "only",
    "or",
    "other",
    "ought",
    "our",
    "ours",
    "ourselves",
    "out",
    "over",
    "own",
    "same",
    "shan't",
    "she",
    "she'd",
    "she'll",
    "she's",
    "should",
    "shouldn't",
    "so",
    "some",
    "such",
    "than",
    "that",
    "that's",
    "the",
    "their",
    "theirs",
    "them",
    "themselves",
    "then",
    "there",
    "there's",
    "these",
    "they",
    "they'd",
    "they'll",
    "they're",
    "they've",
    "this",
    "those",
    "through",
    "to",
    "too",
    "under",
    "until",
    "up",
    "very",
    "was",
    "wasn't",
    "we",
    "we'd",
    "we'll",
    "we're",
    "we've",
    "were",
    "weren't",
    "what",
    "what's",
    "when",
    "when's",
    "where",
    "where's",
    "which",
    "while",
    "who",
    "who's",
    "whom",
    "why",
    "why's",
    "with",
    "won't",
    "would",
    "wouldn't",
    "you",
    "you'd",
    "you'll",
    "you're",
    "you've",
    "your",
    "yours",
    "yourself",
    "yourselves",
}

_TOKEN_RE = re.compile(r"[^A-Za-z0-9']+")


class KeywordGenerator:
    def __init__(self, translator: PortugueseTranslator, max_keywords: int = 8) -> None:
        self.translator = translator
        self.max_keywords = max_keywords

    def extract(self, text: str) -> List[str]:
        phrases = _extract_candidate_phrases(text)
        scored = _score_phrases(phrases)
        keywords: list[str] = []
        seen = set()
        for phrase, score in sorted(scored.items(), key=lambda item: item[1], reverse=True):
            candidate = " ".join(phrase)
            if len(candidate) < 4:
                continue
            if candidate in seen:
                continue
            seen.add(candidate)
            keywords.append(candidate)
            if len(keywords) >= self.max_keywords:
                break
        if keywords:
            return keywords
        # Fallback to most common words if RAKE yields nothing
        flat_words = [word for phrase in phrases for word in phrase]
        counter = Counter(flat_words)
        return [word for word, _ in counter.most_common(self.max_keywords)]

    def generate(self, english_text: str) -> List[Tuple[str, str]]:
        english_keywords = self.extract(english_text)
        portuguese_keywords = self.translator.translate_keywords(english_keywords)
        if len(portuguese_keywords) != len(english_keywords):
            logger.warning(
                "Número de traduções de palavras-chave diferente do esperado: %d vs %d",
                len(portuguese_keywords),
                len(english_keywords),
            )
        return list(zip(portuguese_keywords, english_keywords))


def _extract_candidate_phrases(text: str) -> List[List[str]]:
    sentences = re.split(r"[.!?\n]+", text)
    phrases: list[list[str]] = []
    for sentence in sentences:
        words = [
            word.lower()
            for word in _TOKEN_RE.split(sentence)
            if word and not word.isdigit()
        ]
        phrase: list[str] = []
        for word in words:
            if word in _STOPWORDS:
                if phrase:
                    phrases.append(phrase)
                    phrase = []
            else:
                phrase.append(word)
        if phrase:
            phrases.append(phrase)
    return phrases


def _score_phrases(phrases: Iterable[List[str]]) -> dict[Tuple[str, ...], float]:
    freq: Counter[str] = Counter()
    degree: Counter[str] = Counter()
    for phrase in phrases:
        unique_words = set(phrase)
        phrase_length = len(phrase)
        for word in phrase:
            freq[word] += 1
            degree[word] += phrase_length
        for word in unique_words:
            degree[word] += phrase_length - 1

    word_scores = {word: degree[word] / freq[word] for word in freq}

    phrase_scores: dict[Tuple[str, ...], float] = {}
    for phrase in phrases:
        key = tuple(phrase)
        phrase_scores[key] = sum(word_scores[word] for word in phrase)
    return phrase_scores


__all__ = ["KeywordGenerator"]
