#!/usr/bin/env bash
set -euo pipefail

workshop="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ "${1:-}" == --help ]]; then
    printf 'Usage: %s --worktree CODEX_CANDIDATE\n' "$0"
    exit 0
fi
if [[ $# != 2 || "$1" != --worktree ]]; then
    printf 'Expected --worktree CODEX_CANDIDATE\n' >&2
    exit 2
fi
candidate="$(cd -- "$2" && pwd)"
if [[ ! -f "$candidate/codex-rs/Cargo.toml" ]] ||
    ! git -C "$candidate" symbolic-ref -q HEAD >/dev/null; then
    printf 'Gate requires a named Codex candidate worktree.\n' >&2
    exit 1
fi
sha="$(git -C "$candidate" rev-parse HEAD)"
check_candidate() {
    [[ "$(git -C "$candidate" rev-parse HEAD)" == "$sha" ]] &&
        [[ -z "$(git -C "$candidate" status --porcelain)" ]]
}
if ! check_candidate; then
    printf 'Commit candidate changes before gating.\n' >&2
    exit 1
fi

# Reuse setup unchanged, but keep its binary selector away from the consumer.
stage="$(mktemp -d "${TMPDIR:-/tmp}/codex-viewer-gate.XXXXXX")"
trap 'rm -rf -- "$stage"' EXIT
mkdir -p "$stage/scripts" "$stage/bin"
cp "$workshop/scripts/setup.sh" "$stage/scripts/setup.sh"
cp "$workshop/bin/codex-viewer" "$stage/bin/codex-viewer"
ln -s "$candidate" "$stage/codex"
cache="${XDG_CACHE_HOME:-$HOME/.cache}/codex-viewer-gates"
if [[ -d /Volumes/Scratch ]]; then
    cache=/Volumes/Scratch/codex-viewer-gates
fi
export CODEX_VIEWER_TARGET_DIR="${CODEX_VIEWER_GATE_TARGET_DIR:-$cache/$sha}"
if [[ "$CODEX_VIEWER_TARGET_DIR" != /* ]]; then
    printf 'CODEX_VIEWER_GATE_TARGET_DIR must be absolute.\n' >&2
    exit 2
fi
mkdir -p "$CODEX_VIEWER_TARGET_DIR"
CODEX_VIEWER_TARGET_DIR="$(cd -- "$CODEX_VIEWER_TARGET_DIR" && pwd -P)"
if [[ -e "$workshop/.build/codex-viewer" ]] &&
    [[ "$workshop/.build/codex-viewer" -ef "$CODEX_VIEWER_TARGET_DIR/release/codex-viewer" ]]; then
    printf 'Gate target must not overwrite the selected consumer binary.\n' >&2
    exit 1
fi
export CARGO_TARGET_DIR="$CODEX_VIEWER_TARGET_DIR"
export CARGO_BUILD_JOBS="${CARGO_BUILD_JOBS:-2}"
receipt="$CODEX_VIEWER_TARGET_DIR/viewer-gate.txt"
rm -f -- "$receipt"
(
    cd "$candidate/codex-rs"
    # Integration tests spawn helpers outside the selected test packages.
    cargo build --locked -p codex-cli -p codex-code-mode-host -p codex-rmcp-client \
        -p codex-exec-server -p codex-shell-escalation -p codex-exec --bins
    # Personal ignore rules can silently omit project config from Git fixtures.
    # Color assertions require ANSI output even when the calling agent disables it.
    (
        unset NO_COLOR
        export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
        export GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.excludesFile GIT_CONFIG_VALUE_0=/dev/null
        just test -p codex-tui -p codex-app-server
    )
    just fix -p codex-tui -p codex-app-server
    just fmt
)
if ! check_candidate; then
    printf 'Gate changed the candidate; review and commit fixes before a final gate.\n' >&2
    exit 1
fi
CODEX_VIEWER_PROFILE=release "$stage/scripts/setup.sh"
CODEX_VIEWER_BINARY="$stage/.build/codex-viewer" "$stage/bin/codex-viewer" --help
if ! check_candidate; then
    printf 'Candidate changed during build; no receipt written.\n' >&2
    exit 1
fi
tree="$(git -C "$candidate" rev-parse 'HEAD^{tree}')"
digest="$(shasum -a 256 "$CODEX_VIEWER_TARGET_DIR/release/codex-viewer")"
completed="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
{
    printf 'candidate=%s\ntree=%s\n' "$sha" "$tree"
    printf 'binary=%s/release/codex-viewer\n' "$CODEX_VIEWER_TARGET_DIR"
    printf 'sha256=%s\n' "${digest%% *}"
    printf 'completed=%s\n' "$completed"
    printf 'terminal_smoke=not-recorded-by-this-gate\n'
} > "$receipt"
printf 'Automated gate passed: %s\n' "$receipt"
