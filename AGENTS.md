# ScamSquash agent handoff

The integrated development baseline is `agent/browser-voice` until its PR merges.
Fetch before starting. Base new branches on `origin/agent/browser-voice` while
that PR is open and on `origin/main` once it is merged.

## Work in parallel

- Use one branch and worktree per task. For example, after fetching, run
  `git worktree add -b agent/<task> ../scam-call-<task> origin/agent/browser-voice`.
- Agree on file ownership and interface changes before editing. Check
  `git status --short --branch` before edits and stage explicit paths.
- Preserve unexpected changes. Push your own branch and use pull requests.
  Coordinate overlapping edits and avoid force pushes or resets of shared work.
- Use fictional test calls. Keep API keys, role links, transcripts, audio and
  downloaded model files outside Git.

## Current modes and ownership

- Screening and evidence: `scam_call/flow.py` defines transcript turns, caller-only
  detection, evidence citations and the incident draft. Preserve
  `Turn(id, speaker, text)`, `assess(transcript)` and `draft_report(transcript)`.
  Speaker roles are caller, receiver and assistant. Requests for sensitive data,
  unusual payments and threats tied to payment can trigger takeover.
- Local two-device room: `scam_call/local_room.py` and `scam_call/web/room.html`.
  Run `python3 -m scam_call.local_room` on port 8767. The README covers ffmpeg,
  CPU Whisper, Ollama, and the HTTPS tunnel. Share distinct Caller and Receiver
  links. The room uses recorded turns, takes over automatically on caller
  evidence, and uses Mac speech with a browser fallback. After End call, download
  the transcript before selecting New call. New call keeps both role links.
- OpenAI browser demo: `scam_call/browser.py`, `web/index.html`, and `web/app.js`
  under `scam_call`. Run `python3 -m scam_call.browser` on port 8765. This is
  the single-mic demo with alternating roles, a two-second pause, and automatic
  takeover using the Realtime API. It requires available API quota.
- CLI simulator: `scam_call/__main__.py`. Run `python3 -m scam_call --demo`
  for a scripted check or `python3 -m scam_call --voice` for the interactive
  macOS spoken demo.
- Twilio conference trial: `python3 -m scam_call.phone_trial` serves conference
  TwiML on port 8766. Two verified phones connected in the trial. Live PSTN
  transcription and takeover are separate work; the trial blocks media streaming.

## Next work and verification

The next useful checks are two-device playback in Safari and Chrome, a benign
caller turn, a suspicious caller request, receiver lockout, and a draft with
evidence. Confirm each phone shows its expected role. Verify that a New call
clears prior turns and allows new recordings on the same links. Keep
`/state`'s call ID and the upload's `X-Call` header in sync.

Run `python3 -m scam_call --demo`, `python3 -m compileall -q scam_call` and
`git diff --check` before submitting changes. For room troubleshooting, first
check the loopback server and Ollama, then verify the public tunnel. A working
loopback room does not guarantee the phone links work. Cloudflare needs outbound
port 7844 and its temporary hostname changes when the tunnel restarts.
