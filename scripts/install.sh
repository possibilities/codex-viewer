#!/usr/bin/env bash
set -euo pipefail

repository_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
install_prefix="${PREFIX:-${HOME}/.local}"

"$repository_root/scripts/setup.sh"
mkdir -p "$install_prefix/bin"
ln -sfn "$repository_root/bin/codex-viewer" "$install_prefix/bin/codex-viewer"
printf 'Installed %s\n' "$install_prefix/bin/codex-viewer"
