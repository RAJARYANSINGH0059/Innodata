# DECISIONS

NOT STARTED (M0). See PROJECT_STATE.md.
- DEC-004 Variation = behaviour class + code surface, measured by weighted Jaccard with thresholds fixed before measurement; declared dimensions are our claims and are cross-checked by lexical overlap, never used alone.
- DEC-005 "Equivalent" mutants must be verified by the runner (not caught by tests) and justified in text; post-hoc classification is disclosed.
- DEC-006 Feature tests must all fail in State A; preservation tests go in regression dir and must pass in all states.
