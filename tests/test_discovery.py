import tempfile
import textwrap
import unittest
from pathlib import Path

from taskfactory.discovery import discover

SRC = textwrap.dedent('''
    import zlib
    import json

    def check(age, max_age=None):
        if age < 0:
            raise ValueError("future")
        if max_age is not None and age > max_age:
            raise ValueError("old")

    def no_literal(a, b):
        if a < b:
            raise ValueError("order")          # comparison of two names: not a literal rule

    def no_raise(age):
        if age < 0:
            return None                         # literal comparison but no raise

    def unpack(data):
        return zlib.decompress(data)

    def bounded(data):
        d = zlib.decompressobj()
        return d.decompress(data, 10)

    def parse(s):
        return json.loads(s)

    def outer(x, flag=False):
        return inner(x, flag=flag)

    def inner(x, flag=False):
        return x  # TODO: handle flag

    def _private(x):
        return x
''')
TEST = "from m import check, unpack, outer\n"


class DiscoveryTests(unittest.TestCase):
    def run_discover(self, src=SRC, test=TEST):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root = Path(td.name)
        (root / "m.py").write_text(src)
        (root / "tests").mkdir()
        (root / "tests" / "test_m.py").write_text(test)
        return discover(root)

    def by_kind(self, rep, kind):
        return [c for c in rep["selected"] if c["kind"] == kind]

    def test_rule_parameter_requires_literal_compare_and_raise(self):
        c = self.by_kind(self.run_discover(), "tolerance-or-rule-parameter")
        self.assertEqual([x["symbol"] for x in c], ["check"])
        self.assertEqual(c[0]["snippet"], "if age < 0:")

    def test_resource_guard_flags_unbounded_only(self):
        c = self.by_kind(self.run_discover(), "resource-limit-guard")
        self.assertEqual(sorted(x["symbol"] for x in c), ["parse", "unpack"])  # decompressobj.decompress is bounded/unknown

    def test_option_threading_todo_and_untested(self):
        rep = self.run_discover()
        self.assertEqual([c["symbol"] for c in self.by_kind(rep, "option-threading")], ["outer"])
        self.assertEqual(len(self.by_kind(rep, "documented-todo")), 1)
        untested = {c["symbol"] for c in self.by_kind(rep, "untested-public-api")}
        self.assertIn("parse", untested)
        self.assertNotIn("check", untested)      # referenced by tests
        self.assertNotIn("_private", untested)   # private never reported

    def test_every_candidate_is_anchored_and_deterministic(self):
        a, b = self.run_discover(), self.run_discover()
        strip = lambda r: [{k: v for k, v in c.items()} for c in r["selected"]]  # noqa: E731
        self.assertEqual(strip(a), strip(b))
        for c in a["selected"]:
            self.assertTrue(c["file"] and c["line"] > 0 and c["snippet"] and c["candidate_id"])

    def test_syntax_error_file_is_skipped_not_fatal(self):
        rep = self.run_discover(src="def broken(:\n")
        self.assertEqual(rep["total_candidates"], 0)


if __name__ == "__main__":
    unittest.main()
