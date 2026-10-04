#!/usr/bin/env bash
# Show which files are code (git) and which are assets (Drive), with sizes.
set -euo pipefail
cd -- "$(dirname -- "$0")/.."
echo "== CODE (git) =="
git ls-files --cached --others --exclude-standard
echo
echo "== ASSETS (Drive) =="
git ls-files --others --ignored --exclude-standard | grep -vEf archive/never_upload.txt | xargs -d '\n' du -ch | sort -h | tail -n 40
