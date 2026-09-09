"""Exercise maintenance boundaries with real local Git graphs and fake builds."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parent.parent
REAL_GIT = shutil.which("git")


class WorkshopTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="viewer workshop ")
        self.addCleanup(self.temp.cleanup)
        base = Path(self.temp.name)
        self.root = base / "workshop"
        self.root.mkdir()
        for directory in ("scripts", "bin"):
            shutil.copytree(SOURCE / directory, self.root / directory)
        self.codex = self.root / "codex"
        self.codex.mkdir()
        self.env = dict(os.environ, GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
        for path, branch in [(self.root, "main"), (self.codex, "codex-viewer")]:
            self.git(path, "init", "-b", branch)
            self.git(path, "config", "user.name", "Workshop test")
            self.git(path, "config", "user.email", "test@example.invalid")
        (self.codex / "codex-rs").mkdir()
        (self.codex / "codex-rs/Cargo.toml").write_text("# fixture\n")
        self.git(self.codex, "add", ".")
        self.git(self.codex, "commit", "-m", "baseline")
        self.baseline = self.git(self.codex, "rev-parse", "HEAD")
        self.remote = base / "remote.git"
        self.git(self.root, "clone", "--bare", str(self.codex), str(self.remote))
        self.git(self.codex, "remote", "add", "origin", "https://github.com/possibilities/codex.git")
        self.git(self.codex, "remote", "add", "upstream", "https://github.com/openai/codex.git")
        (self.root / ".gitmodules").write_text(
            '[submodule "codex"]\n path = codex\n'
            ' url = https://github.com/possibilities/codex.git\n branch = codex-viewer\n'
        )
        (self.root / ".gitignore").write_text(".build/\n")
        self.git(self.root, "add", "scripts", "bin", ".gitignore", ".gitmodules")
        self.git(self.root, "update-index", "--add", "--cacheinfo", f"160000,{self.baseline},codex")
        self.git(self.root, "commit", "-m", "workshop fixture")
        mockbin = base / "mockbin"
        mockbin.mkdir()
        self.log = base / "calls.jsonl"
        shim = '''#!/usr/bin/env python3
import json, os, pathlib, sys
name = pathlib.Path(sys.argv[0]).name
args = sys.argv[1:]
if name == "git":
    if "ls-remote" in args and "origin" in args:
        args[args.index("origin")] = os.environ["TEST_REMOTE"]
    os.execv(os.environ["TEST_GIT"], [os.environ["TEST_GIT"], *args])
with open(os.environ["TEST_LOG"], "a") as log:
    log.write(json.dumps([name, args]) + "\\n")
if name == "just" and args and args[0] == "test":
    assert "NO_COLOR" not in os.environ
    assert os.environ["GIT_CONFIG_GLOBAL"] == "/dev/null"
    assert os.environ["GIT_CONFIG_NOSYSTEM"] == "1"
    assert os.environ["GIT_CONFIG_COUNT"] == "1"
    assert os.environ["GIT_CONFIG_KEY_0"] == "core.excludesFile"
    assert os.environ["GIT_CONFIG_VALUE_0"] == "/dev/null"
if name == "just" and args == ["fmt"] and os.environ.get("TEST_FMT_DIRTY"):
    pathlib.Path("Cargo.toml").write_text("# changed by formatter\\n")
if name == "cargo":
    if os.environ.get("TEST_BUILD_FAIL"):
        sys.exit(17)
    if "codex-viewer" not in args:
        sys.exit(0)
    profile = "release" if "--release" in args else "debug"
    binary = pathlib.Path(os.environ["CARGO_TARGET_DIR"]) / profile / "codex-viewer"
    binary.parent.mkdir(parents=True, exist_ok=True)
    binary.write_text("#!/bin/sh\\nprintf 'fixture viewer help\\\\n'\\n")
    binary.chmod(0o755)
'''
        for name in ("git", "just", "cargo"):
            path = mockbin / name
            path.write_text(shim)
            path.chmod(0o755)
        self.target = base / "gate target"
        self.env.update(
            PATH=f"{mockbin}:{os.environ['PATH']}", TEST_REMOTE=str(self.remote),
            TEST_GIT=REAL_GIT, TEST_LOG=str(self.log),
            CODEX_VIEWER_GATE_TARGET_DIR=str(self.target),
            CODEX_VIEWER_TARGET_DIR=str(base / "consumer target"),
        )
        # Ambient development overrides must not select an old binary in gates.
        self.env["CODEX_VIEWER_BINARY"] = "/does/not/exist"

    def git(self, path, *args):
        return subprocess.check_output(
            [REAL_GIT, "-C", str(path), *args], env=self.env,
            text=True, stderr=subprocess.PIPE,
        ).strip()

    def run_script(self, name, *args, ok=True):
        result = subprocess.run(
            [str(self.root / "scripts" / name), *args], env=self.env,
            capture_output=True, text=True,
        )
        if ok:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def advance(self):
        (self.codex / "feature").write_text("new carry\n")
        self.git(self.codex, "add", "feature")
        self.git(self.codex, "commit", "-m", "new carry")
        return self.git(self.codex, "rev-parse", "HEAD")

    def test_model_and_supervision_claim_only_viewer(self):
        data = json.loads(self.run_script("reconcile-branches.sh", "--print-model").stdout)
        self.assertEqual(data["publication_refs"], ["refs/heads/codex-viewer"])
        self.assertIsNone(data["mirror_branch"])
        before = self.git(self.codex, "show-ref")
        self.run_script("reconcile-branches.sh", "--configure-supervision")
        self.run_script("reconcile-branches.sh", "--check-supervision")
        self.run_script("reconcile-branches.sh", "--configure-supervision")
        self.assertEqual(before, self.git(self.codex, "show-ref"))
        self.assertEqual(self.git(self.codex, "config", "supervisor.trunk"), "codex-viewer")
        self.assertEqual(self.git(self.root, "config", "supervisor.checkout"), str(self.codex))
        self.run_script("reconcile-branches.sh", "--apply", ok=False)

    def test_check_accepts_published_ancestor_and_rejects_unpublished_pin(self):
        self.run_script("reconcile-branches.sh", "--check")
        sha = self.advance()
        before = self.git(self.codex, "show-ref")
        result = self.run_script("reconcile-branches.sh", "--check", "--pin", sha, ok=False)
        self.assertIn("not reachable", result.stderr)
        self.assertEqual(before, self.git(self.codex, "show-ref"))
        self.git(self.codex, "push", str(self.remote), "HEAD:refs/heads/codex-viewer")
        self.run_script("reconcile-branches.sh", "--check")
        self.run_script("reconcile-branches.sh", "--check", "--pin", sha)

    def test_check_rejects_wrong_push_destination(self):
        self.git(self.codex, "remote", "set-url", "--push", "origin", "https://github.com/openai/codex.git")
        self.run_script("reconcile-branches.sh", "--check", ok=False)

    def test_check_rejects_wrong_submodule_branch(self):
        self.git(self.root, "config", "-f", ".gitmodules", "submodule.codex.branch", "integration")
        self.run_script("reconcile-branches.sh", "--check", ok=False)

    def test_gate_orders_checks_and_does_not_select_consumer(self):
        self.env["NO_COLOR"] = "1"
        self.run_script("gate.sh", "--worktree", str(self.codex))
        calls = [json.loads(line) for line in self.log.read_text().splitlines()]
        self.assertEqual(calls, [
            ["cargo", ["build", "--locked", "-p", "codex-cli", "-p", "codex-code-mode-host",
                       "-p", "codex-rmcp-client", "-p", "codex-exec-server",
                       "-p", "codex-shell-escalation", "-p", "codex-exec", "--bins"]],
            ["just", ["test", "-p", "codex-tui", "-p", "codex-app-server"]],
            ["just", ["fix", "-p", "codex-tui", "-p", "codex-app-server"]],
            ["just", ["fmt"]],
            ["cargo", ["build", "--locked", "-p", "codex-tui", "--bin", "codex-viewer", "--release"]],
        ])
        self.assertIn(f"candidate={self.baseline}", (self.target / "viewer-gate.txt").read_text())
        self.assertFalse((self.root / ".build").exists())
        self.assertEqual(self.git(self.codex, "status", "--porcelain"), "")

    def test_gate_fails_on_formatter_changes_without_build_or_receipt(self):
        self.env["TEST_FMT_DIRTY"] = "1"
        self.run_script("gate.sh", "--worktree", str(self.codex), ok=False)
        self.assertFalse((self.target / "viewer-gate.txt").exists())
        self.assertNotIn('--release', self.log.read_text())

    def test_gate_fails_on_dirty_or_detached_candidate(self):
        (self.codex / "untracked").write_text("in progress")
        self.run_script("gate.sh", "--worktree", str(self.codex), ok=False)
        (self.codex / "untracked").unlink()
        self.git(self.codex, "switch", "--detach")
        self.run_script("gate.sh", "--worktree", str(self.codex), ok=False)
        self.assertFalse(self.log.exists())

    def test_failed_build_does_not_leave_success_receipt(self):
        self.run_script("gate.sh", "--worktree", str(self.codex))
        self.env["TEST_BUILD_FAIL"] = "1"
        self.run_script("gate.sh", "--worktree", str(self.codex), ok=False)
        self.assertFalse((self.target / "viewer-gate.txt").exists())

    def test_gate_refuses_the_selected_consumer_target(self):
        binary = self.target / "release/codex-viewer"
        binary.parent.mkdir(parents=True)
        binary.write_text("selected binary")
        (self.root / ".build").mkdir()
        (self.root / ".build/codex-viewer").symlink_to(binary)
        self.run_script("gate.sh", "--worktree", str(self.codex), ok=False)
        self.assertEqual(binary.read_text(), "selected binary")
        self.assertFalse(self.log.exists())

    def test_consumer_rejects_dirty_and_unpublished_states_before_build(self):
        sha = self.advance()
        self.run_script("update-pin.sh", "--sha", sha, ok=False)
        self.assertFalse(self.log.exists())
        self.git(self.root, "add", "codex")
        self.git(self.root, "commit", "-m", "unpublished pin fixture")
        self.run_script("update-pin.sh", "--sha", sha, ok=False)
        self.assertFalse(self.log.exists())

    def test_consumer_builds_published_pin_without_committing(self):
        before = self.git(self.root, "rev-parse", "HEAD")
        self.run_script("update-pin.sh", "--sha", self.baseline)
        self.assertEqual(before, self.git(self.root, "rev-parse", "HEAD"))
        self.assertTrue((self.root / ".build/codex-viewer").exists())

    def test_consumer_fast_forwards_to_exact_published_candidate(self):
        candidate = Path(self.temp.name) / "candidate"
        self.git(self.codex, "worktree", "add", "-b", "candidate", str(candidate))
        (candidate / "feature").write_text("new carry\n")
        self.git(candidate, "add", "feature")
        self.git(candidate, "commit", "-m", "candidate carry")
        sha = self.git(candidate, "rev-parse", "HEAD")
        self.git(candidate, "push", str(self.remote), "HEAD:refs/heads/codex-viewer")
        before = self.git(self.root, "rev-parse", "HEAD")
        self.run_script("update-pin.sh", "--sha", sha)
        self.assertEqual(self.git(self.codex, "rev-parse", "HEAD"), sha)
        self.assertEqual(self.git(self.root, "rev-parse", "HEAD"), before)
        self.assertIn(self.baseline, self.git(self.root, "ls-tree", "HEAD", "codex"))
        self.assertEqual(self.git(self.root, "status", "--porcelain"), "M codex")


if __name__ == "__main__":
    unittest.main(verbosity=2)
