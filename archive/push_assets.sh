#!/usr/bin/env bash
# Upload assets (every file git ignores) to Google Drive, keeping relative paths.
# Uses `rclone copy`, so nothing on the remote is ever deleted.
# Usage: archive/push_assets.sh [--dry-run]
set -euo pipefail
REMOTE="gdrive-altair:bsc_predefense_assets"
cd -- "$(dirname -- "$0")/.."
LIST=$(mktemp)
trap 'rm -f "$LIST"' EXIT
git ls-files --others --ignored --exclude-standard | grep -vEf archive/never_upload.txt > "$LIST"
rclone copy . "$REMOTE" --files-from "$LIST" --progress "$@"
