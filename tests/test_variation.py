import shutil
import tempfile
import unittest
from pathlib import Path

from taskfactory.variation import compare, signature, variation_report

TASKS = Path(__file__).resolve().parents[1] / "tasks"
T1 = TASKS / "itsdangerous-leeway-001"
T2 = TASKS / "itsdangerous-decompress-limit-002"


def rename_clone(src: Path, dst: Path, old: str, new: str) -> Path:
    """Superficial variation: same behaviour, renamed parameter/identifier (cf. Black Friday vs Christmas marquee)."""
    shutil.copytree(src, dst)
    for f in dst.rglob("*"):
        if f.is_file() and f.suffix in {".py", ".md", ".toml", ".diff"}:
            f.write_text(f.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")
    return dst


class VariationTests(unittest.TestCase):
    def test_identical_task_scores_one(self):
        s = signature(T1)
        self.assertEqual(compare(s, s)["composite"], 1.0)

    def test_renamed_clone_is_flagged_not_distinct(self):
        with tempfile.TemporaryDirectory() as td:
            clone = rename_clone(T1, Path(td) / "clone", "leeway", "skew_tolerance")
            res = compare(signature(T1), signature(clone))
            self.assertGreaterEqual(res["composite"], 0.5, res)
            self.assertEqual(res["verdict"], "TOO_SIMILAR")

    def test_genuinely_different_tasks_are_distinct(self):
        res = variation_report([T1, T2])["pairs"][0]
        self.assertEqual(res["verdict"], "DISTINCT", res)
        self.assertEqual(res["shared_files"], [])
        self.assertEqual(res["shared_declared_dimensions"], [])

    def test_signature_extracts_changed_symbols(self):
        self.assertIn("TimestampSigner", signature(T1)["symbols"])
        self.assertIn("_decompress", signature(T2)["symbols"])
        self.assertIn("max_decompressed_size", signature(T2)["symbols"])


if __name__ == "__main__":
    unittest.main()
