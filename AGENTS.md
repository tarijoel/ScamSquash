# Working in parallel

Read this file and the README before editing. Tell the other contributor what files you plan to own and agree on shared interface changes before starting them.

- Use one branch and one worktree per task. From a clean clone, fetch and run `git worktree add -b agent/<task> ../scam-call-<task> origin/main`. Use `main` as the base if working locally before the first push.
- Check `git status --short --branch` before editing and before staging. Stage explicit paths. If you encounter unexpected changes, preserve them and coordinate with their owner.
- Keep commits focused. Push your own branch and open a pull request to main. Merge one pull request at a time and check the next branch against updated main. Coordinate any overlapping changes and resolve conflicts with both contributors.
- Avoid force pushes, hard resets, cleaning shared directories, and rewriting someone else's branch. GitHub branches and pull requests are the shared record of progress.
- Use synthetic calls in examples and checks. Keep transcripts from actual calls and credentials outside Git.

## File ownership

- `scam_call/flow.py` owns detection, screening responses, and report generation.
- `scam_call/__main__.py` owns the local simulator. A future phone adapter should be a separate module.
- The shared interface is a transcript of `Turn` records. Coordinate changes to the speaker names, turn IDs, and return values before modifying it.

Run `python3 -m scam_call --demo` and try a benign call with `python3 -m scam_call` before opening a pull request that changes the flow.
