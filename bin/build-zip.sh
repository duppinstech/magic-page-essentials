#!/usr/bin/env bash
# Build magic-page-essentials.zip from tracked files only, excluding development files.
# Used by .github/workflows/release.yml; run locally with `bash bin/build-zip.sh` to inspect the package.
set -euo pipefail

cd "$(dirname "$0")/.."
rm -rf build magic-page-essentials.zip
mkdir -p build/magic-page-essentials

# Tracked files only (never local settings or untracked scratch files), minus dev-only paths.
git ls-files -z \
  | grep -zvE '^(\.github/|\.claude/|tests/|bin/|docs/|scripts/|\.gitignore$|\.gitattributes$|AGENTS\.md$|CLAUDE\.md$|OWNERSHIP\.md$|CONTRIBUTING\.md$|[Ii][Nn][Tt][Ee][Nn][Tt]\.md$|[Pp][Ll][Aa][Nn]\.md$|composer\.(json|lock)$|phpcs\.xml\.dist$|phpunit\.xml\.dist$)' \
  | xargs -0 -I{} cp --parents {} build/magic-page-essentials/

( cd build && zip -qr9 ../magic-page-essentials.zip magic-page-essentials )
unzip -l magic-page-essentials.zip
