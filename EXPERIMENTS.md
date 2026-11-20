# EXPERIMENTS
## EXP-001 Does the three-state gate + hand-written variants find defects in an AI-authored task?
- Inputs: itsdangerous @672971d; task itsdangerous-leeway-001; Python 3.13.
- Procedure: tests→patch→validate(3 repeats)→14 variants.
- Result: gate caught test defect D-002 (B-state); variants exposed oracle gap M12 and harness bug D-003. Final: PASS, 12/12 wrong killed, 2/2 alt accepted.
- Limits: n=1 task, 1 repo, same-author (L-1). Not evidence of general factory quality.
## EXP-002 Does the variation metric separate meaningful from superficial variation?
- Hypothesis: weighted Jaccard over patch files/symbols/entrypoints/criteria/test tokens flags a renamed clone as TOO_SIMILAR and a different behaviour class as DISTINCT.
- Inputs: tasks 001 and 002 (+ synthetic rename clone of 001). Thresholds fixed BEFORE measuring: DISTINCT<0.25, TOO_SIMILAR≥0.5.
- Result: 0.061 (001 vs 002) DISTINCT; 0.947 (001 vs rename clone) TOO_SIMILAR.
- Limits: n=3 comparisons, lexical metric; no embedding/semantic check; a clone that changes structure but not behaviour would not be caught. Manual adjudication required.
## EXP-003 Reconstruction
- Both tasks rebuilt from manifest + fresh clone reproduce recorded status, tree digests, patch hash and failing-test set (5/5 comparisons each).
