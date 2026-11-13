"""Run the call simulator with synthetic messages."""

import argparse
import shutil
import subprocess
import sys

from .flow import FOLLOW_UPS, Turn, assess, draft_report


DEMO_CALL = (
    "Your power will be shut off today unless you pay with gift cards.",
    "I'm with Example Electric.",
    "Call me back at 202-555-0142.",
    "I need 200 dollars on gift cards.",
)


def approve_handoff() -> bool:
    """Ask the recipient before the simulated AI takes over."""
    while True:
        try:
            choice = input("1. Let AI continue\n2. End call\nChoose 1 or 2: ").strip().casefold()
        except EOFError:
            return False
        if choice in {"1", "let ai continue"}:
            return True
        if choice in {"2", "end call", ""}:
            return False
        print("Please choose 1 (Let AI continue) or 2 (End call).")


def run(demo: bool, speaker: str | None = None) -> None:
    transcript: list[Turn] = []
    followups_sent = 0
    demo_turns = iter(DEMO_CALL)

    def reply(message: str) -> None:
        nonlocal speaker
        transcript.append(Turn(len(transcript) + 1, "assistant", message))
        print(f"Assistant: {message}", flush=True)
        if speaker:
            try:
                subprocess.run([speaker, message], check=True)
            except (OSError, subprocess.CalledProcessError):
                print("Speech playback failed. Continuing in text.", file=sys.stderr)
                speaker = None

    reply("Hi. What are you calling about?")
    while True:
        if demo:
            message = next(demo_turns, "")
            if message:
                print(f"Caller: {message}")
        else:
            try:
                message = input("Caller (blank to end): ").strip()
            except EOFError:
                break
        if not message:
            break

        transcript.append(Turn(len(transcript) + 1, "caller", message))
        evidence = assess(transcript)
        if not evidence:
            reply("Is there anything else I should know?")
            continue
        if followups_sent == 0:
            reasons = ", ".join(dict.fromkeys(item.reason for item in evidence))
            print(f"Screening alert: {reasons}")
            if not demo and not approve_handoff():
                reply("I'm going to end the call now.")
                break
        if followups_sent == len(FOLLOW_UPS):
            reply("Thanks. I'm going to end the call now.")
            break
        reply(FOLLOW_UPS[followups_sent])
        followups_sent += 1

    print()
    print(draft_report(transcript))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo", action="store_true", help="Run the scripted utility scam.")
    parser.add_argument("--voice", action="store_true", help="Speak assistant replies on macOS.")
    args = parser.parse_args()
    speaker = shutil.which("say") if args.voice and sys.platform == "darwin" else None
    if args.voice and speaker is None:
        parser.error("--voice requires the macOS say command")
    run(args.demo, speaker)


if __name__ == "__main__":
    main()
