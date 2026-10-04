#!/usr/bin/env bash
# Build both ghostwritten versions:
#   predefense_author.pdf  -- author's copy, red boxes mark missing evidence
#   predefense_reader.pdf  -- reader's copy, generated from the author copy
# Runs from predefense/ so image paths (figs/, assets/, static_case/figures/) resolve.
set -euo pipefail
HERE=$(cd -- "$(dirname -- "$0")" && pwd)
cd -- "$HERE/.."
python3 scripts/make_reader_copy.py > /dev/null
for V in author reader; do
  mkdir -p "ghostwritten/build/$V"
  for pass in 1 2 3; do
    TEXINPUTS="ghostwritten/$V//:${TEXINPUTS:-}" pdflatex -interaction=nonstopmode -halt-on-error \
      -output-directory="ghostwritten/build/$V" "ghostwritten/$V/predefense.tex" > "ghostwritten/build/$V/compile-pass$pass.txt"
  done
  cp "ghostwritten/build/$V/predefense.pdf" "ghostwritten/predefense_$V.pdf"
  printf 'Built ghostwritten/predefense_%s.pdf\n' "$V"
done
