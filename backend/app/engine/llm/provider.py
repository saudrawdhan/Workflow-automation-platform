"""Summarization and classification backends behind one interface.

The ``PROVIDER`` environment variable selects the backend: ``mock`` (default, fully
offline), ``anthropic`` (official SDK), or ``local`` (Hugging Face transformers).
Nodes call ``summarize`` / ``classify`` and never depend on which backend answers.
"""
from __future__ import annotations

import os
import re
from typing import List, Tuple

PROVIDER = os.getenv("PROVIDER", "mock").lower()
MODEL = os.getenv("MODEL", "claude-opus-4-8")

_SENTENCE = re.compile(r"(?<=[.!?])\s+")

_KEYWORDS = {
    "complaint": ["refund", "late", "damaged", "broken", "wrong", "disappointed", "poor", "delay"],
    "request": ["please", "could you", "would like", "need", "request", "help", "how do"],
    "praise": ["great", "excellent", "love", "amazing", "thank", "perfect", "happy"],
}

_summarizer = None
_classifier = None


def summarize(text: str, max_sentences: int) -> Tuple[str, str]:
    if PROVIDER == "anthropic":
        return _summarize_anthropic(text, max_sentences), "anthropic"
    if PROVIDER == "local":
        return _summarize_local(text, max_sentences), "local"
    return _summarize_mock(text, max_sentences), "mock"


def classify(text: str, labels: List[str]) -> Tuple[str, float, str]:
    if PROVIDER == "anthropic":
        label, confidence = _classify_anthropic(text, labels)
        return label, confidence, "anthropic"
    if PROVIDER == "local":
        label, confidence = _classify_local(text, labels)
        return label, confidence, "local"
    label, confidence = _classify_mock(text, labels)
    return label, confidence, "mock"


def _summarize_mock(text: str, max_sentences: int) -> str:
    sentences = [s.strip() for s in _SENTENCE.split(text.strip()) if s.strip()]
    if not sentences:
        return text.strip()
    return " ".join(sentences[: max(1, max_sentences)])


def _classify_mock(text: str, labels: List[str]) -> Tuple[str, float]:
    lowered = text.lower()
    scores = {
        label: sum(1 for kw in _KEYWORDS.get(label.lower(), [label.lower()]) if kw in lowered)
        for label in labels
    }
    total = sum(scores.values())
    if total == 0:
        fallback = "other" if "other" in labels else labels[0]
        return fallback, 0.5
    best = max(scores, key=scores.get)
    return best, round(scores[best] / total, 2)


def _summarize_anthropic(text: str, max_sentences: int) -> str:
    import anthropic

    client = anthropic.Anthropic()
    prompt = (
        f"Summarize the following in at most {max_sentences} sentences. "
        f"Return only the summary.\n\n{text}"
    )
    message = client.messages.create(
        model=MODEL,
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(block.text for block in message.content if block.type == "text").strip()


def _classify_anthropic(text: str, labels: List[str]) -> Tuple[str, float]:
    import anthropic

    client = anthropic.Anthropic()
    prompt = (
        f"Classify the text into exactly one of these labels: {', '.join(labels)}. "
        f"Reply with only the label.\n\n{text}"
    )
    message = client.messages.create(
        model=MODEL,
        max_tokens=16,
        messages=[{"role": "user", "content": prompt}],
    )
    answer = "".join(b.text for b in message.content if b.type == "text").strip().lower()
    for label in labels:
        if label.lower() in answer:
            return label, 0.9
    return labels[0], 0.5


def _summarize_local(text: str, max_sentences: int) -> str:
    global _summarizer
    if _summarizer is None:
        from transformers import pipeline

        _summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    result = _summarizer(text, max_length=130, min_length=30, do_sample=False)
    return result[0]["summary_text"].strip()


def _classify_local(text: str, labels: List[str]) -> Tuple[str, float]:
    global _classifier
    if _classifier is None:
        from transformers import pipeline

        _classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
    result = _classifier(text, candidate_labels=labels)
    return result["labels"][0], round(float(result["scores"][0]), 2)
