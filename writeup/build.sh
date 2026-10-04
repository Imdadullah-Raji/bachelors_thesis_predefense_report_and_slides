#!/usr/bin/env bash
# Build both writeup versions:
#   predefense_author.pdf  -- author's copy, red boxes mark missing evidence
#   predefense_reader.pdf  -- reader's copy, generated from the author copy
# Runs from predefense/ so image paths (figs/, assets/, static_case/figures/) resolve.
set -euo pipefail
HERE=$(cd -- "$(dirname -- "$0")" && pwd)
cd -- "$HERE/.."
python3 scripts/make_reader_copy.py > /dev/null
for V in author reader; do
  mkdir -p "writeup/build/$V"
  for pass in 1 2 3; do
    TEXINPUTS="writeup/$V//:${TEXINPUTS:-}" pdflatex -interaction=nonstopmode -halt-on-error \
      -output-directory="writeup/build/$V" "writeup/$V/predefense.tex" > "writeup/build/$V/compile-pass$pass.txt"
  done
  cp "writeup/build/$V/predefense.pdf" "writeup/predefense_$V.pdf"
  printf 'Built writeup/predefense_%s.pdf\n' "$V"
done
