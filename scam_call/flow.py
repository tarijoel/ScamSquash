"""Transcript-based screening and report generation for the simulator."""

import re
from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class Turn:
    id: int
    speaker: Literal["caller", "receiver", "assistant"]
    text: str


@dataclass(frozen=True)
class Evidence:
    reason: str
    turn_id: int
    quote: str


PAYMENT_METHOD = r"(?:gift cards?|bitcoin|crypto(?:currency)?|wire transfer)"
PAYMENT_AMOUNT = r"(?:\$\s*\d[\d,]*(?:\.\d{2})?|\d[\d,]*(?:\.\d{2})?\s+dollars?)"
PAYMENT_REQUEST = (
    rf"(?:\b(?:pay|send|transfer|wire)\s+(?:me\s+|us\s+|with\s+|by\s+|using\s+|via\s+|in\s+)?"
    rf"(?:{PAYMENT_AMOUNT}|{PAYMENT_METHOD})\b"
    rf"|\b(?:i|we) (?:need|require)\s+{PAYMENT_AMOUNT}\b"
    r"|\b(?:you (?:must|need to|have to)|unless you) pay\b)"
)
PHONE_NUMBER = r"(?<!\d)(?:\+1[ .-]?)?(?:\(\d{3}\)|\d{3})[ .-]?\d{3}[ .-]?\d{4}(?!\d)"
ORGANIZATION = r"\b(?:i['’]m (?:with|from)|calling (?:from|on behalf of)|i represent)\s+([^.!?;\n]+)"

SIGNALS = (
    (
        "Mention of sensitive identity or banking information",
        r"\b(?:social security(?: number)?|ssn|bank(?:ing)? (?:information|details|account(?: number)?)"
        r"|routing number)\b",
    ),
    (
        "Unusual payment request",
        rf"{PAYMENT_REQUEST}[^.!?;\n]{{0,60}}\b{PAYMENT_METHOD}\b"
        rf"|\b(?:pay|send|transfer)\s+(?:me\s+|us\s+)?"
        rf"(?:(?:with|by|using|via|in)\s+)?{PAYMENT_METHOD}\b",
    ),
    (
        "Request for a verification code or password",
        r"\b(?:read|tell|give|send|share)\b[^.!?;\n]{0,45}"
        r"\b(?:verification code|security code|one[- ]time code|password)\b",
    ),
    (
        "Threat tied to a payment request",
        rf"(?=[^.!?;\n]*{PAYMENT_REQUEST})[^.!?;\n]*"
        r"\b(?:shut off|suspend(?:ed)?|arrest(?:ed)?|disconnect(?:ed)?)\b",
    ),
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


def incident_details(transcript: list[Turn]) -> list[str]:
    details = []
    callback_prompted = False
    for turn in transcript:
        if turn.speaker == "assistant":
            callback_prompted = turn.text == FOLLOW_UPS[1]
            continue

        if turn.speaker != "caller":
            callback_prompted = False
            continue

        organization = re.search(ORGANIZATION, turn.text, re.IGNORECASE)
        if organization:
            details.append(
                f"- Claimed organization: {organization[1].strip()} (turn {turn.id})"
            )

        callback_mentioned = re.search(
            r"\b(?:call (?:me|us) (?:back|at)|call back|callback number|reach (?:me|us) at)\b",
            turn.text,
            re.IGNORECASE,
        )
        if callback_prompted or callback_mentioned:
            for number in re.findall(PHONE_NUMBER, turn.text):
                details.append(f"- Callback number supplied by caller: {number} (turn {turn.id})")

        if re.search(PAYMENT_REQUEST, turn.text, re.IGNORECASE):
            details.append(f"- Payment request (turn {turn.id}): {turn.text}")
        callback_prompted = False

    return details


def draft_report(transcript: list[Turn]) -> str:
    evidence = assess(transcript)
    if not evidence:
        return "No incident draft. The screening rules did not flag this call."

    lines = ["Draft incident report", "Assessment: suspected scam"]
    details = incident_details(transcript)
    if details:
        lines.extend(["", "Incident details (unverified caller claims)", *details])

    lines.extend(["", "Screening signals"])
    lines.extend(f"- Turn {item.turn_id}: {item.reason}. Caller said: {item.quote}" for item in evidence)
    lines.extend(["", "Transcript (caller claims are unverified)"])
    lines.extend(f"- Turn {turn.id} [{turn.speaker}]: {turn.text}" for turn in transcript)
    return "\n".join(lines)
