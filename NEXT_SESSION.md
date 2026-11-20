# NEXT_SESSION
Resume: upload this ZIP (+ SRT/template/handover if you have them). Read PROJECT_STATE.md.
DONE: M1/M2 first task (see PROJECT_STATE). Remaining plan below was the earlier plan; now do M3: second behaviourally different task + variation report + reconstruction check. (old:) Next milestone (M1→M2): add `taskfactory/patching.py` (apply/revert patch in disposable worktree copies, tests first) and `taskfactory/orchestrate.py` running State A/B/C via existing validation.py + JUnit parsing against pinned itsdangerous 672971d…; then pick a real feature (candidate area: `timed.py`/`url_safe.py` extension points), author requirement + tests BEFORE the reference patch.
Blockers for you: upload PPT template + organiser handover (repo list/schema/matrix) when received; email organisers re: bug-fix & security-task policy; decide GitHub route (web UI upload per GITHUB_PUBLISH_GUIDE once written).

M3 DONE (2 validated tasks, variation, reconstruction). Do M4 (second repo/stack) or M5 (CI + publish guide) next; M5 is cheaper and needed for submission (public GitHub repo, demo video, PPT template).

M5 DONE. Highest-value next: automated discovery (taskfactory discover) so the pipeline *proposes* feature candidates from AST/symbols, then M4 second repo. User: decide licence, publish via GITHUB_PUBLISH_GUIDE, send PPT template.

## After M4
- Add node job to CI/demo (needs `npm install` of `is` deps; no lockfile).
- Remaining: licence decision, PPT, demo video, Windows run, independent test author, sandbox, bug-fix type.
