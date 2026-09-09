#!/usr/bin/env bash
set -euo pipefail
workshop="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ "${1:-}" == --help ]]; then
    printf 'Usage: %s --sha PUBLISHED_VIEWER_COMMIT\nBuilds and prepares the outer pin; does not commit or push.\n' "$0"
    exit 0
fi
if [[ $# != 2 || "$1" != --sha || ! "$2" =~ ^[0-9a-f]{40}$ ]]; then
    printf 'Expected --sha and a full published viewer commit SHA.\n' >&2
    exit 2
fi
sha="$2"
if [[ "$(git -C "$workshop" symbolic-ref --short HEAD)" != main ]] ||
    [[ "$(git -C "$workshop/codex" symbolic-ref --short HEAD)" != codex-viewer ]] ||
    [[ -n "$(git -C "$workshop" status --porcelain)" ]] ||
    [[ -n "$(git -C "$workshop/codex" status --porcelain)" ]]; then
    printf 'Consumer update requires clean outer main and inner codex-viewer checkouts.\n' >&2
    exit 1
fi
"$workshop/scripts/reconcile-branches.sh" --check --pin "$sha"
git -C "$workshop/codex" merge-base --is-ancestor HEAD "$sha"
git -C "$workshop/codex" merge --ff-only "$sha"
check_candidate() {
    [[ "$(git -C "$workshop/codex" rev-parse HEAD)" == "$sha" ]] &&
        [[ -z "$(git -C "$workshop/codex" status --porcelain)" ]]
}
if ! check_candidate; then
    printf 'Inner checkout changed during handover; inspect it before building.\n' >&2
    exit 1
fi
CODEX_VIEWER_PROFILE=release "$workshop/scripts/setup.sh"
CODEX_VIEWER_BINARY="$workshop/.build/codex-viewer" "$workshop/bin/codex-viewer" --help
if ! check_candidate; then
    printf 'Inner checkout changed during build; do not commit this pin.\n' >&2
    exit 1
fi
"$workshop/scripts/reconcile-branches.sh" --check --pin "$sha"
printf 'Built published viewer %s. Review codex and update SCRATCHPAD.md before committing the outer pin.\n' "$sha"
