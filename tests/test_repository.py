import tempfile
import unittest
from pathlib import Path

from taskfactory.repository import inspect_repository


class RepositoryInspectionTests(unittest.TestCase):
    def test_detects_languages_and_project_markers(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "main.py").write_text("print('hello')\n", encoding="utf-8")
            (root / "package.json").write_text('{"name":"demo"}\n', encoding="utf-8")
            (root / ".gitignore").write_text("node_modules\n", encoding="utf-8")
            snap = inspect_repository(root)
            self.assertFalse(snap.is_git_repository)
            self.assertEqual(snap.file_count, 3)
            self.assertEqual(snap.languages["Python"], 1)
            self.assertIn("JavaScript/TypeScript project (package.json)", snap.project_markers)
            self.assertEqual(len(snap.working_tree_digest), 64)

    def test_invalid_path_rejected(self):
        with self.assertRaises(ValueError):
            inspect_repository("/path/that/does/not/exist")


if __name__ == "__main__":
    unittest.main()
