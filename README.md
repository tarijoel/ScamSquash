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
