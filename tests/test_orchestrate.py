import subprocess
import tempfile
import unittest
from pathlib import Path

import json
import os

from taskfactory.mutation import run_mutants
from taskfactory.orchestrate import validate_task
from taskfactory.patching import PatchError, install_files, make_workspace, validate_patch_text

PKG_V1 = 'def greet(name):\n    return "hi " + name\n'
PKG_V2 = 'def greet(name, shout=False):\n    out = "hi " + name\n    return out.upper() if shout else out\n'
BASE_TEST = 'from pkg import greet\n\ndef test_greet():\n    assert greet("a") == "hi a"\n'
FEATURE_TEST = ('from pkg import greet\n\n'
                'def test_shout():\n    assert greet("a", shout=True) == "HI A"\n\n'
                'def test_shout_false():\n    assert greet("a", shout=False) == "hi a"\n')
REGRESSION_TEST = 'from pkg import greet\n\ndef test_default_unchanged():\n    assert greet("b") == "hi b"\n'


def git(cwd, *args):
    r = subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", *args],
                       cwd=cwd, capture_output=True, text=True, check=True)
    return r.stdout.strip()


def build_repo(tmp: Path):
    repo = tmp / "repo"
    (repo / "pkg").mkdir(parents=True)
    (repo / "tests").mkdir()
    (repo / "pkg/__init__.py").write_text(PKG_V1)
    (repo / "tests/test_base.py").write_text(BASE_TEST)
    git(repo, "init", "-q")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "base")
    commit = git(repo, "rev-parse", "HEAD")
    (repo / "pkg/__init__.py").write_text(PKG_V2)
    patch = git(repo, "diff") + "\n"
    git(repo, "checkout", "--", ".")
    return repo, commit, patch


def build_task(tmp: Path, commit: str, patch: str, feature=FEATURE_TEST, regression=REGRESSION_TEST):
    t = tmp / "task"
    (t / "solution").mkdir(parents=True)
    (t / "tests/feature").mkdir(parents=True)
    (t / "tests/regression").mkdir(parents=True)
    (t / "solution/solution.diff").write_text(patch)
    (t / "tests/feature/test_feature.py").write_text(feature)
    (t / "tests/regression/test_regression.py").write_text(regression)
    (t / "task.toml").write_text(
        f'[task]\nid="syn-001"\nkind="feature"\n[repo]\ncommit="{commit}"\n'
        '[solution]\npatch="solution/solution.diff"\n'
        '[tests]\nfeature="tests/feature"\nregression="tests/regression"\ninject_dir="tests"\n'
        '[run]\nbaseline_targets=["tests/test_base.py"]\npythonpath=["."]\nimport_probe="pkg"\nrepeats=2\n')
    return t


class OrchestrateTests(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.tmp = Path(self._td.name)
        self.repo, self.commit, self.patch = build_repo(self.tmp)

    def tearDown(self):
        self._td.cleanup()

    def statuses(self, result):
        return {c["check_id"]: c["status"] for c in result["report"]["checks"]}

    def test_valid_feature_task_passes_all_states(self):
        task = build_task(self.tmp, self.commit, self.patch)
        result = validate_task(task, self.repo, self.tmp / "out")
        self.assertEqual(result["report"]["status"], "PASS", self.statuses(result))
        self.assertEqual(result["state_tree_digests"]["original"], result["state_tree_digests"]["removed"])
        self.assertNotEqual(result["state_tree_digests"]["original"], result["state_tree_digests"]["reference"])

    def test_tests_that_pass_without_feature_are_rejected(self):
        always = 'def test_trivial():\n    assert True\n'
        task = build_task(self.tmp, self.commit, self.patch, feature=always)
        result = validate_task(task, self.repo, self.tmp / "out")
        self.assertEqual(result["report"]["status"], "FAILED")
        self.assertEqual(self.statuses(result)["original_detects_missing_behaviour"], "FAILED")

    def test_collection_error_is_not_valid_failure(self):
        broken = 'from pkg import does_not_exist\n\ndef test_x():\n    assert does_not_exist()\n'
        task = build_task(self.tmp, self.commit, self.patch, feature=broken)
        result = validate_task(task, self.repo, self.tmp / "out")
        self.assertNotEqual(result["report"]["status"], "PASS")
        self.assertNotEqual(self.statuses(result)["original_detects_missing_behaviour"], "PASS")

    def test_tests_failing_with_reference_are_rejected(self):
        wrong = 'from pkg import greet\n\ndef test_x():\n    assert greet("a", shout=True) == "nope"\n'
        task = build_task(self.tmp, self.commit, self.patch, feature=wrong)
        result = validate_task(task, self.repo, self.tmp / "out")
        self.assertEqual(self.statuses(result)["reference_implements_requirement"], "FAILED")

    def test_regression_broken_by_patch_is_rejected(self):
        bad_patch = self.patch.replace('"hi " + name', '"yo " + name')
        task = build_task(self.tmp, self.commit, bad_patch)
        result = validate_task(task, self.repo, self.tmp / "out")
        self.assertEqual(result["report"]["status"], "FAILED")

    def test_nonapplying_patch_fails_cleanly(self):
        task = build_task(self.tmp, self.commit, self.patch.replace("hi", "zz", 1))
        result = validate_task(task, self.repo, self.tmp / "out")
        self.assertEqual(result["report"]["status"], "FAILED")


class MutationTests(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.tmp = Path(self._td.name)
        self.repo, self.commit, self.patch = build_repo(self.tmp)

    def tearDown(self):
        self._td.cleanup()

    def test_mutants_killed_survivors_alt_valid_and_relative_out(self):
        task = build_task(self.tmp, self.commit, self.patch)
        mut = [
            dict(id="W1", kind="wrong", file="pkg/__init__.py", old='out.upper() if shout else out', new='out', description="ignores shout"),
            dict(id="W2", kind="wrong", file="pkg/__init__.py", old='"hi "', new='"hi " ', description="untested whitespace-only mutant"),
            dict(id="A1", kind="alt_valid", file="pkg/__init__.py", old='out.upper() if shout else out', new='(out.upper() if shout else out)', description="parenthesised"),
            dict(id="BAD", kind="wrong", file="pkg/__init__.py", old='no such text', new='x'),
        ]
        mf = self.tmp / "mutants.json"
        mf.write_text(json.dumps(mut))
        cwd = os.getcwd()
        os.chdir(self.tmp)  # relative out dir must still work
        try:
            rep = run_mutants(task, self.repo, mf, "rel_out")
        finally:
            os.chdir(cwd)
        got = {r["id"]: r["outcome"] for r in rep["results"]}
        self.assertEqual(got["W1"], "KILLED")
        self.assertEqual(got["W2"], "SURVIVED")  # honest: this mutant is not detectable by these tests
        self.assertEqual(got["A1"], "ACCEPTED")
        self.assertEqual(got["BAD"], "INVALID")


class PatchSafetyTests(unittest.TestCase):
    def test_rejects_traversal_absolute_git_and_symlink(self):
        for bad in ("--- a/../evil\n+++ b/../evil\n", "--- /etc/passwd\n+++ /etc/passwd\n",
                    "--- a/.git/hooks/x\n+++ b/.git/hooks/x\n",
                    "diff --git a/l b/l\nnew file mode 120000\n--- /dev/null\n+++ b/l\n"):
            with self.assertRaises(PatchError, msg=bad):
                validate_patch_text(bad)

    def test_rejects_empty_and_binary(self):
        with self.assertRaises(PatchError):
            validate_patch_text("nothing here\n")
        with self.assertRaises(PatchError):
            validate_patch_text("--- a/x\n+++ b/x\nGIT binary patch\n")

    def test_install_rejects_symlink_and_escape(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            (td / "ws").mkdir()
            (td / "src").mkdir()
            (td / "src/a.py").write_text("x=1\n")
            with self.assertRaises(PatchError):
                install_files(td / "ws", td / "src", "../out")
            (td / "src/link").symlink_to(td / "src/a.py")
            with self.assertRaises(PatchError):
                install_files(td / "ws", td / "src", "tests")

    def test_workspace_requires_matching_commit(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            repo, commit, _ = build_repo(td)
            head = make_workspace(repo, commit[:12], td / "w1")
            self.assertEqual(head, commit)
            with self.assertRaises(PatchError):
                make_workspace(repo, "deadbeef" * 5, td / "w2")


if __name__ == "__main__":
    unittest.main()


class ReconstructTests(unittest.TestCase):
    def test_manifest_detects_modified_missing_and_unlisted(self):
        from taskfactory.reconstruct import verify_manifest, write_manifest
        with tempfile.TemporaryDirectory() as td:
            repo, commit, patch = build_repo(Path(td))
            task = build_task(Path(td), commit, patch)
            write_manifest(task)
            self.assertEqual(verify_manifest(task), [])
            (task / "tests/feature/test_feature.py").write_text("def test_x():\n    assert True\n")
            (task / "extra.txt").write_text("x")
            (task / "instruction.md").write_text("x")
            (task / "solution/solution.diff").unlink()
            probs = verify_manifest(task)
            self.assertIn("modified: tests/feature/test_feature.py", probs)
            self.assertIn("unlisted: extra.txt", probs)
            self.assertIn("missing: solution/solution.diff", probs)

    def test_reconstruct_matches_recorded_and_rejects_tamper(self):
        from taskfactory.reconstruct import reconstruct, write_manifest
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            repo, commit, patch = build_repo(td)
            task = build_task(td, commit, patch)
            validate_task(task, repo, td / "rec")
            write_manifest(task)
            ok = reconstruct(task, repo, td / "rec/validation_report.json", td / "again")
            self.assertEqual(ok["status"], "PASS", ok)
            (task / "solution/solution.diff").write_text(patch + "\n# tampered\n")
            self.assertNotEqual(patch + "\n# tampered\n", patch)
            bad = reconstruct(task, repo, td / "rec/validation_report.json", td / "again2")
            self.assertEqual(bad["status"], "FAILED")


class JunitSafetyTests(unittest.TestCase):
    def test_oversized_report_rejected_without_parsing(self):
        import taskfactory.test_adapters as ta
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "r.xml"
            p.write_text("<testsuite><testcase name='a'/></testsuite>")
            old, ta.MAX_REPORT_BYTES = ta.MAX_REPORT_BYTES, 5
            try:
                outcome, info = ta.classify_junit_xml(p)
            finally:
                ta.MAX_REPORT_BYTES = old
            self.assertEqual(outcome, "invalid_test_report")
            self.assertIn("size cap", info["error"])

    def test_entity_bomb_is_not_expanded(self):
        from taskfactory.test_adapters import classify_junit_xml
        bomb = ('<?xml version="1.0"?><!DOCTYPE l [<!ENTITY a "' + "x" * 1000 + '">'
                + "".join(f'<!ENTITY b{i} "&{"a" if i == 0 else "b" + str(i - 1)};&{"a" if i == 0 else "b" + str(i - 1)};&{"a" if i == 0 else "b" + str(i - 1)};">' for i in range(12))
                + ']><testsuite><testcase name="&b11;"/></testsuite>')
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "bomb.xml"
            p.write_text(bomb)
            outcome, _ = classify_junit_xml(p)
        self.assertEqual(outcome, "invalid_test_report")
