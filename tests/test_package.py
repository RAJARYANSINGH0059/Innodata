import tempfile
import unittest
from pathlib import Path

from taskfactory.package import build_task_package, verify_task_package


class PackageTests(unittest.TestCase):
    def metadata(self):
        return {
            "task_id": "demo-feature-001",
            "kind": "feature",
            "title": "Add bounded pagination to the sample listing API",
            "repository_url": "https://example.invalid/demo",
            "license": "MIT",
            "base_commit": "abcdef1234567",
            "working_tree_digest": "a" * 64,
            "generation_model": "manual-fixture",
            "prompt_version": "0.1.0",
            "seed": 42,
        }

    def build(self, path):
        return build_task_package(
            path,
            self.metadata(),
            "## Requirement\nReturn at most `limit` records and a stable next cursor.",
            "diff --git a/demo.py b/demo.py\n--- a/demo.py\n+++ b/demo.py\n@@\n- return rows\n+ return rows[:limit]\n",
            {"test_pagination.py": "def test_page_limit():\n    assert page([1, 2], 1) == [1]"},
            {"test_existing_order.py": "def test_default_order():\n    assert order([2, 1]) == [1, 2]"},
            {"traceability.json": {"REQ-001": ["AC-001", "AC-002"]}, "validation.json": {"status": "NOT_RUN"}},
        )

    def test_package_builds_and_verifies(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "package"
            result = self.build(root)
            self.assertTrue(result["valid"], result["errors"])
            self.assertEqual(result["task_id"], "demo-feature-001")
            self.assertTrue((root / "manifest.sha256").is_file())

    def test_tampering_is_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "package"
            self.build(root)
            (root / "instructions.md").write_text("tampered\n", encoding="utf-8")
            result = verify_task_package(root)
            self.assertFalse(result["valid"])
            self.assertTrue(any("checksum mismatch" in error for error in result["errors"]))

    def test_bug_fix_kind_is_not_released(self):
        with tempfile.TemporaryDirectory() as tmp:
            metadata = self.metadata()
            metadata["kind"] = "bug_fix"
            with self.assertRaises(ValueError):
                build_task_package(
                    Path(tmp) / "package", metadata, "instructions", "patch",
                    {"feature.py": "test"}, {"regression.py": "test"}, {},
                )

    def test_path_traversal_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                build_task_package(
                    Path(tmp) / "package", self.metadata(), "instructions", "patch",
                    {"../../escape.py": "test"}, {"regression.py": "test"}, {},
                )

    def test_nonempty_output_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "package"
            root.mkdir()
            (root / "keep.txt").write_text("keep", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                self.build(root)


if __name__ == "__main__":
    unittest.main()
