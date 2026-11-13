# Scam Call Assistant

Hackathon prototype that flags suspected scam calls, takes over with a simulated recipient persona, and turns what the caller says into a draft incident report the recipient can review.

## Demo flow

1. Play a scripted call or feed in a synthetic transcript. Include a legitimate call and a scam scenario.
2. Show the risk assessment and the transcript lines that triggered it, such as impersonation, urgency, or a request for an unusual payment.
3. On the flagged call, demonstrate a handoff to an AI using a fictional recipient persona. It asks for details such as the claimed organization, a callback number, and what payment the caller is requesting. It never shares real personal information, credentials, or verification codes.
4. Generate a draft with the call timeline, suspected scam type, the caller's claims, and supporting transcript excerpts. Mark unverified claims and distinguish caller-provided details from model inferences. The recipient reviews and decides whether to submit it.

## First work split

- Call flow: build the demo input, scam detection, and handoff. Emit speaker-labeled transcript events and the reasons the call was flagged.
- AI conversation and report: build the simulated recipient's replies and turn those transcript events into a report the recipient can review.

Agree on a shared transcript format first: timestamp, speaker, and text. Start with synthetic fixtures so both pieces can be built and demoed independently. Choose the runtime, model, and any phone integration after confirming the implementation plan.

## Run the starter

Requires Python 3.10 or newer. From the repository root:

```sh
python3 -m scam_call --demo
python3 -m scam_call
```

The first command runs a scripted utility scam. The second lets you type synthetic caller replies. Press Enter on an empty line to end the call. The simulator uses deterministic screening rules, three scripted follow-up questions, and an in-memory transcript. It prints a draft containing the flagged statements and the caller's unverified claims. Model integration, live telephony, and a review UI are future work.

See [AGENTS.md](AGENTS.md) for coordinating parallel work.

## Browser voice demo

From the browser voice worktree, set `OPENAI_API_KEY` in your Terminal environment and run:

```sh
python3 -m scam_call.browser
```

Open http://127.0.0.1:8765, click **Start listening**, and allow microphone access.
The caller speaks first. Share one mic and wait for two seconds of silence after
each turn. Once the transcript is checked, the page switches between **Caller**
and **Receiver** automatically. The AI stays silent until caller speech triggers
the screening rules. After takeover, only the
caller should speak. The AI asks up to three follow-up questions. Click **End call**
to see the incident draft and **Download transcript** to save the text. Use fictional
details and tell both participants that the demo transcribes their speech.

This local demo streams microphone audio to OpenAI and keeps the API key on the
Python server. It uses turn-taking with the mic muted while the assistant speaks.
The server binds to loopback. A Realtime-enabled API project is required.
