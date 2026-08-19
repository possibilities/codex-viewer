#!/usr/bin/env bash
set -euo pipefail

repository_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
codex_root="$repository_root/codex"

if ! git -C "$codex_root" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    git -C "$repository_root" submodule update --init codex
fi

if [[ ! -f "$codex_root/codex-rs/Cargo.toml" ]]; then
    printf 'Codex is not initialized. Run: git submodule update --init\n' >&2
    exit 1
fi

build_profile="${CODEX_VIEWER_PROFILE:-release}"
cargo_arguments=(build --locked -p codex-tui --bin codex-viewer)
case "$build_profile" in
    debug)
        profile_directory=debug
        ;;
    release)
        cargo_arguments+=(--release)
        profile_directory=release
        ;;
    *)
        printf 'Unsupported CODEX_VIEWER_PROFILE: %s (expected debug or release)\n' "$build_profile" >&2
        exit 2
        ;;
esac

target_directory="${CODEX_VIEWER_TARGET_DIR:-$codex_root/codex-rs/target}"
if [[ "$target_directory" != /* ]]; then
    target_directory="$repository_root/$target_directory"
fi

(
    cd "$codex_root/codex-rs"
    CARGO_TARGET_DIR="$target_directory" \
        cargo "${cargo_arguments[@]}"
)

mkdir -p "$repository_root/.build"
ln -sfn "$target_directory/$profile_directory/codex-viewer" "$repository_root/.build/codex-viewer"
printf 'Built %s\n' "$repository_root/.build/codex-viewer"
