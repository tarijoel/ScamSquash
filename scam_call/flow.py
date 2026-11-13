"""Transcript-based screening and report generation for the simulator."""

import re
from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class Turn:
    id: int
    speaker: Literal["caller", "assistant"]
    text: str


@dataclass(frozen=True)
class Evidence:
    reason: str
    turn_id: int
    quote: str


SIGNALS = (
    ("Unusual payment method", r"\b(gift cards?|bitcoin|crypto(?:currency)?)\b"),
    ("Verification code request", r"\b(?:read|tell|give|send|share)\b.{0,45}\b(?:verification|security|one[- ]time) code\b"),
    ("Threat of immediate consequences", r"\b(shut off|suspend(?:ed)?|arrest(?:ed)?)\b"),
)

FOLLOW_UPS = (
    "Which organization are you calling from?",
    "What number can I call to reach you?",
    "What amount are you asking for, and how would I pay?",
)


def assess(transcript: list[Turn]) -> list[Evidence]:
    evidence = []
    for turn in transcript:
        if turn.speaker != "caller":
            continue
        for reason, pattern in SIGNALS:
            if re.search(pattern, turn.text, re.IGNORECASE):
                evidence.append(Evidence(reason, turn.id, turn.text))
    return evidence


def draft_report(transcript: list[Turn]) -> str:
    evidence = assess(transcript)
    if not evidence:
        return "No incident draft. The screening rules did not flag this call."

    lines = ["Draft incident report", "Assessment: suspected scam", "", "Screening signals"]
    lines.extend(f"- Turn {item.turn_id}: {item.reason}. Caller said: {item.quote}" for item in evidence)
    lines.extend(["", "Transcript (caller claims are unverified)"])
    lines.extend(f"- Turn {turn.id} [{turn.speaker}]: {turn.text}" for turn in transcript)
    return "\n".join(lines)
