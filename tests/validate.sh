#!/usr/bin/env bash
set -euo pipefail
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
for script in "$root"/scripts/*.sh "$root"/bin/codex-viewer "$root"/tests/*.sh; do
    bash -n "$script"
done
python3 -B "$root/tests/workshop_test.py"
