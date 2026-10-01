"""Compliance linter for SZL public copy — the Part 2 guardrails as code.

The rules are sentence-scoped and disclaimer-aware. A banned phrase inside a sentence that
already carries the doctrine's own honest qualifier ("Conjecture 1", "not proven",
"advisory", "UNAVAILABLE", "is banned") is compliant: the linter must never punish the
house for stating its own rules. Capability-quantification rules are additionally context
gated, so "the venue is 3 km from the hotel" passes while "detects targets at 5 miles" is
blocked.

A draft with one violation does not ship. There is no override flag by design.
"""

from __future__ import annotations

import html
import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Final

__all__ = [
    "RULES",
    "Rule",
    "Violation",
    "lint",
    "lint_paths",
    "lint_text_files",
    "strip_html",
]

# Sentence ends at terminal punctuation followed by whitespace, or at a line break. Dots inside
# domains, versions and decimals ("a11oy.net", "0.97") never split a sentence.
_SENTENCE_SPLIT: Final = re.compile(r"(?<=[.!?])\s+|(?<=\n)")

# A sentence that already qualifies itself is compliant. Meta-statements about the rules
# ("'proven' is banned") are covered by the banned/forbidden/never-say forms.
_DISCLAIMER: Final = re.compile(
    r"conjecture|not\s+proven|never\s+proven|unproven|not\s+(?:yet\s+)?verified|advisory|"
    r"unavailable|we\s+do\s+not\s+claim|never\s+claim|not\s+financial\s+advice|"
    r"\bbanned\b|forbidden|never\s+(?:say|write|use|forecast|show|imply|quantify|promise)|"
    r"must\s+not|do\s+not\s+say",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Rule:
    """One banned pattern. ``context`` (if set) must also match the same sentence."""

    id: str
    pattern: str
    message: str
    context: str | None = None

    def search(self, sentence: str) -> re.Match[str] | None:
        match = re.search(self.pattern, sentence, re.IGNORECASE)
        if match is None:
            return None
        if self.context is not None and re.search(self.context, sentence, re.IGNORECASE) is None:
            return None
        return match


@dataclass(frozen=True)
class Violation:
    rule_id: str
    message: str
    match: str
    sentence: str

    def __str__(self) -> str:  # pragma: no cover - formatting only
        return f"BANNED [{self.rule_id}] {self.message} -> {self.match!r} in {self.sentence!r}"


_DISTANCE: Final = (
    r"\b\d+(?:\.\d+)?\s*(?:km|kilomet(?:er|re)s?|miles?|met(?:er|re)s?|nautical\s*miles?|nmi)\b"
)
_SENSOR_CONTEXT: Final = (
    r"detect|sensor|radar|lidar|range|coverage|target|threat|drone|\bUAS\b|aircraft|vessel|"
    r"track|acquire|intercept|engage|kill\s*chain"
)

RULES: Final[tuple[Rule, ...]] = (
    # Part 2 rule 4 — Λ discipline.
    Rule(
        "lambda-proven",
        r"(?<!\w)(?:proven|proof-of-performance|closed\s+theorem)(?!\w)",
        "Λ/performance overclaim (Λ is Conjecture 1, advisory)",
    ),
    Rule("lambda-verified-trust", r"verified\s+trust", "Λ discipline: 'verified trust' is banned"),
    Rule("guarantee", r"\bguaranteed?s?\b", "guarantee language"),
    # Trust ceiling 0.97 — never 1.0 / 100%.
    Rule(
        "ceiling-percent",
        r"\b100\s?%\s*(?:trust(?:worthy|ed)?|safe|secure|accurate|accuracy|uptime|reliable)",
        "ceiling violation (max 0.97)",
    ),
    Rule(
        "ceiling-score",
        r"trust\s+(?:level|score|ceiling)\s*(?:of|=|:|is)?\s*(?:1(?:\.0+)?|100\s?%|perfect)\b",
        "ceiling violation (max 0.97)",
    ),
    Rule("superlative", r"\bstate[\s.-]of[\s.-]the[\s.-]art\b", "unverifiable superlative"),
    Rule(
        "absolute",
        r"\b(?:zero|no)\s+hallucinations?\b|\bhallucination-free\b|\b(?:never|cannot)\s+fails?\b",
        "unverifiable absolute",
    ),
    # Part 2 rule 1 — killinchu capability quantification (defense vertical).
    Rule(
        "capability-distance",
        _DISTANCE,
        "killinchu capability quantification (defense vertical)",
        context=_SENSOR_CONTEXT,
    ),
    Rule(
        "capability-scale",
        r"\b(?:kilomet(?:er|re)|mile|met(?:er|re))-scale\b",
        "killinchu capability quantification (defense vertical)",
        context=_SENSOR_CONTEXT,
    ),
    # Part 2 rule 2 — szl-quant is advisory-only, paper-only.
    Rule(
        "quant-returns",
        r"\b(?:strong|consistent|superior|market-beating|alpha-generating|outsized)\s+returns\b"
        r"|\b\d+(?:\.\d+)?\s?%\s+(?:annual(?:ized)?|monthly|yearly)?\s*(?:returns?|yield|gains?)\b"
        r"|\breturns?\s+(?:of|up\s+to)\s+\d",
        "quant performance claim (advisory-only lane)",
    ),
    # Part 2 rule 3 — investor communications never forecast.
    Rule(
        "investor-forecast",
        r"\b(?:projected|forecast(?:ed)?|expected|anticipated)\s+(?:revenue|ARR|MRR|valuation|"
        r"users|growth)\b|\b(?:revenue|ARR|MRR|valuation)\s+(?:will|forecast|projection)\b",
        "investor forecast (describe what exists; link a11oy.net)",
    ),
    # Dead or trap doors verified on 2026-09-30.
    Rule(
        "dead-dns",
        r"\bkhipu\.alloyszlholdings\.com\b",
        "dead DNS door (NO_DNS, verified live 2026-09-30)",
    ),
    Rule(
        "unhyphenated-domain",
        r"(?<![\w.-])a11oy\.com\b",
        "unhyphenated product domain; the product is a-11-oy.com (proof is a11oy.net)",
    ),
)

_TAG: Final = re.compile(r"<(script|style)\b[^>]*>.*?</\1>|<[^>]+>", re.IGNORECASE | re.DOTALL)
_TEXT_SUFFIXES: Final = frozenset({".md", ".txt", ".html", ".htm", ".rst", ".yml", ".yaml"})


def strip_html(text: str) -> str:
    """Drop tags, scripts and styles; unescape entities; keep the words a reader sees."""
    return html.unescape(_TAG.sub(" ", text))


def _sentences(text: str) -> Iterable[str]:
    for sentence in _SENTENCE_SPLIT.split(text):
        stripped = sentence.strip()
        if stripped:
            yield stripped


def lint(text: str, rules: Iterable[Rule] = RULES) -> list[Violation]:
    """Return every violation in ``text``. Empty list means the draft may ship."""
    violations: list[Violation] = []
    seen: set[tuple[str, str]] = set()
    rules = tuple(rules)
    for sentence in _sentences(text):
        disclaimed = _DISCLAIMER.search(sentence) is not None
        for rule in rules:
            match = rule.search(sentence)
            if match is None:
                continue
            if disclaimed and rule.id not in {"dead-dns", "unhyphenated-domain"}:
                continue
            key = (rule.id, sentence)
            if key in seen:
                continue
            seen.add(key)
            violations.append(Violation(rule.id, rule.message, match.group(0), sentence[:120]))
    return violations


def lint_text_files(paths: Iterable[Path]) -> dict[str, list[Violation]]:
    """Lint each file; HTML is reduced to visible text first. Unreadable files are reported."""
    report: dict[str, list[Violation]] = {}
    for path in paths:
        try:
            raw = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            report[str(path)] = [Violation("unreadable", "file is unreadable", str(exc), "")]
            continue
        text = strip_html(raw) if path.suffix.lower() in {".html", ".htm"} else raw
        report[str(path)] = lint(text)
    return report


def lint_paths(
    targets: Iterable[Path], suffixes: frozenset[str] = _TEXT_SUFFIXES
) -> dict[str, list[Violation]]:
    """Expand files and directories (recursively) to text files and lint them all."""
    files: list[Path] = []
    for target in targets:
        if target.is_dir():
            files.extend(
                p
                for p in sorted(target.rglob("*"))
                if p.is_file() and p.suffix.lower() in suffixes and ".git" not in p.parts
            )
        elif target.is_file():
            files.append(target)
        else:
            files.append(target)  # reported as unreadable by lint_text_files
    return lint_text_files(files)
