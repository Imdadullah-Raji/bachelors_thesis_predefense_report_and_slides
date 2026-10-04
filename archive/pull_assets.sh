#!/usr/bin/env bash
# Restore assets from Google Drive into a fresh clone (existing local files are kept if unchanged).
# Usage: archive/pull_assets.sh [--dry-run]
set -euo pipefail
REMOTE="gdrive-altair:bsc_predefense_assets"
cd -- "$(dirname -- "$0")/.."
rclone copy "$REMOTE" . --progress "$@"
