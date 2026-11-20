# Contributing
1. `python -m pip install -e ".[dev]"`
2. `ruff check taskfactory scripts tests && python -m pytest -q tests`
3. A new task = a folder under `tasks/` with `task.toml`, `instruction.md`, `solution/solution.diff`, `tests/feature` (all must FAIL in State A), `tests/regression` (must PASS in all states), `mutants.json`. Write tests from `instruction.md` BEFORE the patch. Then `taskfactory validate`, `mutate`, `manifest`, `reconstruct`, `variation`.
4. Never weaken or delete a failing test to get green; record the defect in DEFECTS.md.
5. Equivalent-mutant labels must be justified in `mutants.json` and are verified by the runner.
