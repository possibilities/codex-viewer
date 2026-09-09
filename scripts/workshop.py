"""Read-only branch checks and local supervision for the merge-only workshop."""

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
CHECKOUT = ROOT / "codex"
BRANCH = "codex-viewer"


def git(path, *args):
    return subprocess.check_output(
        ["git", "-C", str(path), *args], text=True, stderr=subprocess.PIPE
    ).strip()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def verify_remote(name, repository):
    allowed = {
        f"https://github.com/{repository}.git",
        f"https://github.com/{repository}",
        f"git@github.com:{repository}.git",
        f"git@github.com:{repository}",
        f"ssh://git@github.com/{repository}.git",
    }
    for args in [("get-url", "--all", name), ("get-url", "--push", "--all", name)]:
        urls = git(CHECKOUT, "remote", *args).splitlines()
        require(len(urls) == 1 and urls[0] in allowed,
                f"{name} must identify only {repository} for fetch and push")


def model():
    return {
        "workshop": str(ROOT), "checkout": str(CHECKOUT),
        "upstream_remote": "upstream", "upstream_repo": "openai/codex",
        "upstream_branch": "main", "fork_remote": "origin",
        "fork_repo": "possibilities/codex", "integration_branch": BRANCH,
        "mirror_branch": None, "composition": "merge-only",
        "carry_prefixes": [], "carry_refs": [],
        "quarantine_prefix": "DELETEME/", "preserve_open_prs": False,
        "publication_refs": [f"refs/heads/{BRANCH}"],
    }


def supervision(configure):
    settings = {
        "supervisor.trunk": [BRANCH], "supervisor.mirror": [""],
        "supervisor.carryPrefix": [""], "supervisor.carryRef": [],
        "supervisor.quarantinePrefix": ["DELETEME/"],
        "supervisor.workshop": [str(ROOT)],
    }
    for path, values in [(CHECKOUT, settings), (ROOT, {
        "supervisor.checkout": [str(CHECKOUT)]
    })]:
        for key, expected in values.items():
            result = subprocess.run(
                ["git", "-C", str(path), "config", "--local", "--get-all", key],
                text=True, capture_output=True,
            )
            require(result.returncode in (0, 1), f"Cannot read {key}")
            actual = result.stdout.splitlines()
            if configure and actual != expected:
                if actual:
                    git(path, "config", "--local", "--unset-all", key)
                for value in expected:
                    git(path, "config", "--local", "--add", key, value)
            else:
                require(actual == expected,
                        f"{key} differs; run --configure-supervision")
    print("Supervision configured" if configure else "Supervision matches")


def check_pin(pin):
    if pin is None:
        entry = git(ROOT, "ls-tree", "HEAD", "codex").split()
        require(len(entry) == 4 and entry[:2] == ["160000", "commit"],
                "HEAD must contain the codex submodule pin")
        pin = entry[2]
    require(re.fullmatch(r"[0-9a-f]{40}", pin), "--pin requires a full commit SHA")
    git(CHECKOUT, "cat-file", "-e", f"{pin}^{{commit}}")
    output = git(CHECKOUT, "ls-remote", "--exit-code", "origin",
                 f"refs/heads/{BRANCH}").split()
    require(len(output) == 2 and re.fullmatch(r"[0-9a-f]{40}", output[0])
            and output[1] == f"refs/heads/{BRANCH}",
            "Expected exactly one published viewer head")
    published = output[0]
    try:
        git(CHECKOUT, "cat-file", "-e", f"{published}^{{commit}}")
    except subprocess.CalledProcessError:
        raise ValueError("Published head is missing locally; fetch origin codex-viewer, then recheck") from None
    result = subprocess.run(
        ["git", "-C", str(CHECKOUT), "merge-base", "--is-ancestor", pin, published],
        capture_output=True, text=True,
    )
    require(result.returncode == 0,
            f"Pin {pin} is not reachable from published {BRANCH} {published}; "
            "publish the gated inner commit before the outer pin")
    print(f"Pin {pin} is published on {BRANCH} ({published})")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--check", action="store_true", help="verify public pin reachability (default)")
    modes.add_argument("--print-model", action="store_true")
    modes.add_argument("--configure-supervision", action="store_true")
    modes.add_argument("--check-supervision", action="store_true")
    parser.add_argument("--pin", help="check a prospective full SHA instead of the committed gitlink")
    args = parser.parse_args()
    require(not args.pin or not (args.print_model or args.configure_supervision or args.check_supervision),
            "--pin applies only to --check")
    if args.print_model:
        print(json.dumps(model(), indent=2))
        return
    require((CHECKOUT / "codex-rs/Cargo.toml").is_file(),
            "Initialize the pinned codex submodule first")
    for key, expected in {
        "submodule.codex.path": "codex",
        "submodule.codex.branch": BRANCH,
        "submodule.codex.url": "https://github.com/possibilities/codex.git",
    }.items():
        require(git(ROOT, "config", "-f", str(ROOT / ".gitmodules"), "--get", key) == expected,
                f".gitmodules {key} differs from the workshop contract")
    verify_remote("origin", "possibilities/codex")
    # Fresh consumer clones need only origin. Maintenance also needs upstream.
    if "upstream" in git(CHECKOUT, "remote").splitlines():
        verify_remote("upstream", "openai/codex")
    if args.configure_supervision or args.check_supervision:
        supervision(args.configure_supervision)
    else:
        check_pin(args.pin)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, subprocess.CalledProcessError) as error:
        detail = error.stderr.strip() if isinstance(error, subprocess.CalledProcessError) else str(error)
        print(f"codex-viewer workshop: {detail}", file=sys.stderr)
        sys.exit(1)
