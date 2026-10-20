"""Exercise setup from the user's command line, including existing data."""

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "playground.py"
PROJECTS = ("reading-list", "room-booking")


class SetupTests(unittest.TestCase):
    def setUp(self):
        self.workspace = tempfile.TemporaryDirectory(prefix="context-playground-")
        self.addCleanup(self.workspace.cleanup)
        self.parent = Path(self.workspace.name)
        self.target = self.parent / "Demo with spaces and контекст"

    def run_setup(self, env=None):
        return subprocess.run(
            [sys.executable, "-B", str(SCRIPT), str(self.target)],
            capture_output=True, text=True, env=env, check=False,
        )

    def assert_created(self, result):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for project in PROJECTS:
            repo = self.target / "projects" / project
            root = subprocess.run(
                ["git", "-C", str(repo), "rev-parse", "--show-toplevel"],
                capture_output=True, text=True, check=True,
            )
            self.assertEqual(Path(root.stdout.strip()).resolve(), repo.resolve())
            for name in ("AGENTS.md", "README.md"):
                self.assertTrue((repo / name).is_file())
            for path in ("../../context/shared/review.md",
                         "../../context/personal/profile.md"):
                self.assertIn(path, (repo / "AGENTS.md").read_text())
                self.assertTrue((repo / path).is_file())

    def test_creates_independent_repositories_with_one_shared_context(self):
        self.assert_created(self.run_setup())
        policies = list(self.target.rglob("review.md"))
        self.assertEqual(policies, [self.target / "context/shared/review.md"])
        self.assertFalse(any(path.is_symlink() for path in self.target.rglob("*")))
        self.assertEqual(
            (ROOT / "templates/context/shared/review.md").read_bytes(),
            policies[0].read_bytes(),
        )

    def test_existing_files_and_empty_directories_are_never_replaced(self):
        self.target.mkdir()
        for populated in (False, True):
            with self.subTest(populated=populated):
                if populated:
                    (self.target / "keep.txt").write_text("my work", encoding="utf-8")
                before = sorted(self.target.iterdir())
                result = self.run_setup()
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("already exists", result.stderr)
                self.assertEqual(sorted(self.target.iterdir()), before)
        self.assertEqual((self.target / "keep.txt").read_text(), "my work")

    def test_existing_file_is_never_replaced(self):
        self.target.write_text("my work", encoding="utf-8")
        result = self.run_setup()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("already exists", result.stderr)
        self.assertEqual(self.target.read_text(), "my work")

    def test_repeat_setup_preserves_user_changes(self):
        self.assert_created(self.run_setup())
        policy = self.target / "context/shared/review.md"
        policy.write_text("My updated policy", encoding="utf-8")
        result = self.run_setup()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(policy.read_text(), "My updated policy")

    def test_whole_demo_can_move_without_rewriting_paths(self):
        self.assert_created(self.run_setup())
        moved = self.parent / "Moved demo"
        self.target.rename(moved)
        self.target = moved
        for project in PROJECTS:
            repo = moved / "projects" / project
            self.assertEqual(
                (repo / "../../context/shared/review.md").resolve(),
                (moved / "context/shared/review.md").resolve(),
            )
        self.assert_created(subprocess.CompletedProcess([], 0, "", ""))

    def test_git_environment_cannot_redirect_initialization(self):
        sentinel = self.parent / "unrelated"
        sentinel.mkdir()
        (sentinel / "keep.txt").write_text("my work", encoding="utf-8")
        env = dict(os.environ, GIT_DIR=str(sentinel / ".git"),
                   GIT_WORK_TREE=str(sentinel), GIT_INDEX_FILE=str(sentinel / "index"))
        self.assert_created(self.run_setup(env))
        self.assertEqual([p.name for p in sentinel.iterdir()], ["keep.txt"])

    def test_missing_git_fails_before_creating_anything(self):
        env = dict(os.environ, PATH="")
        result = self.run_setup(env)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Git executable not found", result.stderr)
        self.assertFalse(self.target.exists())

    def test_missing_parent_is_not_created_implicitly(self):
        self.target = self.parent / "missing parent" / "demo"
        result = self.run_setup()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Parent directory does not exist", result.stderr)
        self.assertFalse(self.target.parent.exists())

    def test_non_ascii_destination_works_with_limited_stdout_encoding(self):
        env = dict(os.environ, PYTHONIOENCODING="ascii")
        self.assert_created(self.run_setup(env))


if __name__ == "__main__":
    unittest.main()
