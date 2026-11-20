# EXPLAINER_EVIDENCE — full SRT reviewed (1077 cues, 00:00:20 → 00:47:00; English auto-captions, may contain errors)
Tags: [SAID]=speaker (Clint, Innodata) / host (Shvi); [PORTAL]=host screen-share; [INFER]=our inference; [DECISION]=ours.
Speaker statements are NOT official written rules; confirm against portal/handover.

## Logistics (host)
- E-01 [SAID 00:01:50–00:04:04] Prize pool ₹10 lakh (5/3/2). Prototype submission closes **6 Dec**; finalists (top 10–15) announced **7–14 Dec**; mentor connect from 15 Dec; Grand Finale/demo day **20 Dec 2026**.
- E-02 [SAID 00:28:00–00:28:45] Team size is now **1–4** (solo allowed); supersedes "3–4" in the Phase 1 record.
- E-03 [PORTAL 00:30:17–00:31:50] Submission fields: prototype brief, technology, **public GitHub repo link**, **demo video link**, **PPT deck — mandatory organiser template** (in submission tab/Resources). Session recording in Interaction tab.
- E-04 [SAID 00:45:37] Team members can change (leave/join); cross-college teams allowed. Support: support+innodata@hack2skill.com (as transcribed).

## Track 1 (speaker, 00:05:57–00:16:01)
- E-05 [SAID 00:06:41–00:06:48] Task "could be a change of feature, a new feature… or a bug fix." → bug-fix appears permitted by speaker; **no written confirmation**; [DECISION] keep feature tasks primary, bug-fix as secondary/flagged until written confirmation.
- E-06 [SAID 00:06:57–00:07:22] Organisers supply a repository; pipeline must be **reusable across repositories**; "not about generating the task but about the factory."
- E-07 [SAID 00:07:44–00:08:38] Task anatomy: (1) requirements, (2) reference code, (3) tests/evidence → "task package"; one repo → **multiple tasks**.
- E-08 [SAID 00:08:51–00:09:38] Validation evidence = proof task is solvable and tests work; shown in **live demo** and checked in judging.
- E-09 [SAID 00:14:54–00:15:58] Matrix: original repo works as-is (pass); with implementation → pass; **feature removed → feature test fails**. "Matrix will be given to you" (not yet provided). Matches our State A/B/C idea (R-11 now SPEAKER-CONFIRMED, not written).
- E-10 [SAID 00:10:00–00:12:18] Reference benchmarks: SWE-bench (Princeton 2023), SWE-bench Verified (OpenAI, ~500), LiveCodeBench (Berkeley, 600+). Contamination concern (public data) is explicitly motivating → our contamination-limitation disclosure is aligned.
- E-11 [SAID 00:13:20–00:14:02] Use cases: benchmarking models, training coding agents, quality tracking.

## Judging (00:16:17–00:19:13)
- E-12 [SAID] Implementation working+**repeatable** 25%; validity+validation evidence 25%; meaningful variation 20%; originality (approach, guards/checkpoints, engineering judgment) 15%; practical impact+communication (approach, solution, validation) 15%.
- E-13 [SAID 00:17:07–00:17:45] Variation example: Black-Friday marquee vs Christmas marquee = acceptable but NOT meaningful (text/colour only). [SAID 00:27:13] Planning real variation and explaining strategy in demo is a "big plus."
- E-14 [SAID 00:26:00–00:26:28] No hard-coding; any manual changes to output must be disclosed with reasons without compromising validity.

## Package format (Q&A 00:35:00–00:39:30)
- E-15 [SAID] Package = folder: **task.toml** (repo + version), **instruction.md** (requirements), **solution/** containing the `.diff` patch, **tests**; modelled on SWE-bench-style (Harbor-like) layout. Organiser template for "quick verification" **still being finalised**; extra validation info will be requested later.
- E-16 [SAID 00:38:43–00:40:17] Reference code **may be AI-generated**; manual verification is up to us but "there has to be a proof"; an AI validator agent is acceptable.

## Inputs / constraints (Q&A)
- E-17 [SAID 00:33:22–00:34:52, 00:41:02] Organisers will provide **three target repositories**; team chooses one; format (zip vs GitHub) **not finalised**; list not yet named. (Confirms Phase 1 claim of three repos; names unknown.)
- E-18 [SAID 00:34:07, 00:42:34] Language/tech free; justify choices; Python mentioned as easy. No mandatory tools/models.
- E-19 [SAID 00:43:20–00:44:51] Security-related task restrictions: **undecided**, "will get back." Architecture tasks: free choice. Guardrails valued.
- E-20 [SAID 00:41:49] Deliverables: source code, documentation, working prototype **and** demo — "all."
- E-21 [SAID 00:44:51–00:45:37] SWE-bench exists; ask is a novel, more effective **factory**.

## Track 2 (visual) 00:19:16–00:25:43 — out of scope for us.

## Open items needing official confirmation
Repo list & format; task.toml schema; test matrix doc; bug-fix eligibility in writing; security-task policy; PPT template file (not attached); AI-credit/API access mechanics (E-? host mentions "AI model credits" for finalists only at 00:02:49 — [SAID]).
