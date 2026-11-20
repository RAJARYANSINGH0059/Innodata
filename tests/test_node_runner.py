import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from taskfactory.orchestrate import validate_task
from taskfactory.test_adapters import classify_junit_xml

XML_PASS = '<?xml version="1.0"?><testsuites><testcase name="a" time="0.1" classname="test"/></testsuites>'
XML_ASSERT = ('<?xml version="1.0"?><testsuites><testcase name="a" classname="test" failure="Expected 1 !== 2">'
              '<failure type="testCodeFailure" message="Expected values to be strictly equal:1 !== 2">detail</failure>'
              '</testcase></testsuites>')
# what Node 22 emits when a test FILE cannot be imported: a "failed test" named after the file
XML_LOAD = ('<?xml version="1.0"?><testsuites><testcase name="bad_import.test.mjs" classname="test" failure="test failed">'
            '<failure type="testCodeFailure" message="test failed">[Error: test failed] { exitCode: 1 }</failure>'
            '</testcase></testsuites>')
XML_TS_LOAD = XML_LOAD.replace("bad_import.test.mjs", "feature.test.ts")


class NodeJunitClassification(unittest.TestCase):
    def classify(self, xml):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "r.xml"
            p.write_text(xml)
            return classify_junit_xml(p)

    def test_pass(self):
        self.assertEqual(self.classify(XML_PASS)[0], "tests_pass")

    def test_assertion_failure_stays_assertion_failure(self):
        self.assertEqual(self.classify(XML_ASSERT)[0], "test_assertion_failure")

    def test_file_load_failure_is_an_error_not_an_assertion_failure(self):
        for xml in (XML_LOAD, XML_TS_LOAD):
            outcome, ev = self.classify(xml)
            self.assertEqual(outcome, "test_error")
            self.assertEqual(ev["errors"][0]["type"], "file_level_failure")
            self.assertEqual(ev["failures"], [])

    def test_a_real_test_named_like_a_file_with_real_message_is_still_a_failure(self):
        xml = XML_ASSERT.replace('name="a"', 'name="parses config.json"')
        self.assertEqual(self.classify(xml)[0], "test_assertion_failure")


GREET_V1 = 'export function greet(name) {\n\treturn "hi " + name;\n}\n'
GREET_V2 = ('export function greet(name, {shout = false} = {}) {\n\tconst out = "hi " + name;\n'
            '\treturn shout ? out.toUpperCase() : out;\n}\n')
BASE_TEST = ('import {test} from "node:test";\nimport assert from "node:assert/strict";\n'
             'import {greet} from "../src/greet.mjs";\ntest("greet", () => assert.equal(greet("a"), "hi a"));\n')
FEATURE_TEST = ('import {test} from "node:test";\nimport assert from "node:assert/strict";\n'
                'import {greet} from "../../src/greet.mjs";\n'
                'test("shout", () => assert.equal(greet("a", {shout: true}), "HI A"));\n')
REGRESSION_TEST = ('import {test} from "node:test";\nimport assert from "node:assert/strict";\n'
                   'import {greet} from "../../src/greet.mjs";\ntest("default", () => assert.equal(greet("b"), "hi b"));\n')
BROKEN_FEATURE = ('import {nothing} from "../../src/does-not-exist.mjs";\nimport {test} from "node:test";\n'
                  'test("never runs", () => nothing());\n')


def git(cwd, *a):
    return subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", *a], cwd=cwd,
                          capture_output=True, text=True, check=True).stdout.strip()


@unittest.skipUnless(shutil.which("node"), "node not installed")
class NodeEndToEnd(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.tmp = Path(self._td.name)
        repo = self.repo = self.tmp / "repo"
        (repo / "src").mkdir(parents=True)
        (repo / "test").mkdir()
        (repo / "src/greet.mjs").write_text(GREET_V1)
        (repo / "test/base.test.mjs").write_text(BASE_TEST)
        git(repo, "init", "-q")
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", "base")
        self.commit = git(repo, "rev-parse", "HEAD")
        (repo / "src/greet.mjs").write_text(GREET_V2)
        self.patch = git(repo, "diff") + "\n"
        git(repo, "checkout", "--", ".")

    def tearDown(self):
        self._td.cleanup()

    def task(self, feature=FEATURE_TEST):
        t = self.tmp / "task"
        for d in ("solution", "tests/feature", "tests/regression"):
            (t / d).mkdir(parents=True)
        (t / "solution/solution.diff").write_text(self.patch)
        (t / "tests/feature/feature.test.mjs").write_text(feature)
        (t / "tests/regression/regression.test.mjs").write_text(REGRESSION_TEST)
        (t / "task.toml").write_text(
            f'[task]\nid="node-syn-001"\nkind="feature"\n[repo]\ncommit="{self.commit}"\n'
            '[solution]\npatch="solution/solution.diff"\n'
            '[tests]\nfeature="tests/feature"\nregression="tests/regression"\ninject_dir="test"\n'
            '[run]\nrunner="node-test"\nbaseline_targets=["test/base.test.mjs"]\nrepeats=2\n')
        return t

    def test_valid_node_task_passes_three_state(self):
        res = validate_task(self.task(), self.repo, self.tmp / "out")
        self.assertEqual(res["report"]["status"], "PASS", [c for c in res["report"]["checks"] if c["status"] != "PASS"])

    def test_unloadable_feature_test_is_not_a_valid_failure(self):
        res = validate_task(self.task(BROKEN_FEATURE), self.repo, self.tmp / "out")
        status = {c["check_id"]: c["status"] for c in res["report"]["checks"]}
        self.assertNotEqual(res["report"]["status"], "PASS")
        self.assertNotEqual(status["original_detects_missing_behaviour"], "PASS")

    def test_always_passing_feature_test_is_rejected(self):
        trivial = 'import {test} from "node:test";\ntest("t", () => {});\n'
        res = validate_task(self.task(trivial), self.repo, self.tmp / "out")
        self.assertEqual(res["report"]["status"], "FAILED")


if __name__ == "__main__":
    unittest.main()
