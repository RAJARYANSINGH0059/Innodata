import sys
import tempfile
import unittest

from taskfactory.models import CommandSpec
from taskfactory.runner import run_command


class CommandRunnerTests(unittest.TestCase):
    def test_runs_explicit_argv(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_command(CommandSpec("hello", [sys.executable, "-c", "print('ok')"]), tmp)
            self.assertTrue(result.passed)
            self.assertEqual(result.stdout.strip(), "ok")

    def test_rejects_working_directory_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                run_command(CommandSpec("escape", [sys.executable, "-V"], cwd="../"), tmp)

    def test_times_out(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_command(
                CommandSpec("slow", [sys.executable, "-c", "import time; time.sleep(1)"], timeout_seconds=0.05),
                tmp,
            )
            self.assertTrue(result.timed_out)
            self.assertFalse(result.passed)


if __name__ == "__main__":
    unittest.main()
