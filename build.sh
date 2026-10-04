#!/usr/bin/env bash
# Build predefense.pdf from texFiles/.
# Runs from this directory so the relative image paths in the .tex sources
# (figs/, assets/, static_case/figures/) resolve here; TEXINPUTS points
# \input{...} at texFiles/.
set -euo pipefail
cd -- "$(dirname -- "$0")"
mkdir -p build
export TEXINPUTS="texFiles//:${TEXINPUTS:-}"
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build texFiles/predefense.tex > build/compile-pass1.txt
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build texFiles/predefense.tex > build/compile-pass2.txt
python3 scripts/count_words.py
cp build/predefense.pdf predefense.pdf
printf 'Built predefense.pdf\n'
