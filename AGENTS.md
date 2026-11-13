# Working in parallel

Read this file and the README before editing. Tell the other contributor what files you plan to own and agree on shared interface changes before starting them.

- Use one branch and one worktree per task. From a clean clone, fetch and run `git worktree add -b agent/<task> ../scam-call-<task> origin/main`. Use `main` as the base if working locally before the first push.
- Check `git status --short --branch` before editing and before staging. Stage explicit paths. If you encounter unexpected changes, preserve them and coordinate with their owner.
- Keep commits focused. Push your own branch and open a pull request to main. Merge one pull request at a time and check the next branch against updated main. Coordinate any overlapping changes and resolve conflicts with both contributors.
- Avoid force pushes, hard resets, cleaning shared directories, and rewriting someone else's branch. GitHub branches and pull requests are the shared record of progress.
- Use synthetic calls in examples and checks. Keep transcripts from actual calls and credentials outside Git.

## First milestone: call simulation and report review

### Codex — screening and evidence (`agent/screening-report`)

Own `scam_call/flow.py`.

- Improve the screening rules so routine urgency alone does not trigger a report. Keep every flag tied to a caller turn and its exact wording.
- Add a concise incident summary to the draft, including the claimed organization, callback number, and payment request when supported by the transcript. Mark caller claims as unverified and cite the turn IDs.
- Verify the scripted utility scam, a routine appointment reminder, and a message that sounds urgent but does not request money or credentials.

### Other agent — simulator and handoff (`agent/simulator-handoff`)

Own `scam_call/__main__.py`.

- After the first flag in interactive mode, show the screening reasons and offer **Let AI continue** or **End call**. Keep the scripted demo noninteractive.
- Use the existing follow-up prompts after approval and retain the bounded turn count. Show the draft when a flagged call ends, including when the user ends it at the handoff.
- Verify that both choices work and that a routine call never prompts for handoff.

### Shared contract and integration

Keep `Turn(id, speaker, text)`, `Evidence(reason, turn_id, quote)`, `FOLLOW_UPS`, `assess(transcript)`, and `draft_report(transcript)` compatible for this milestone. Treat the report as display text. Either branch should work against the current main on its own. Coordinate before changing shared files or interfaces.

After both pull requests merge, run the scripted demo and try both interactive handoff choices. Keep live telephony and model integration for the next milestone.

Run `python3 -m scam_call --demo` and try a benign call with `python3 -m scam_call` before opening a pull request that changes the flow.
