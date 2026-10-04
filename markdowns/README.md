# Thesis predefense write-up

Open **predefense.pdf** for the compiled A4 report. The LaTeX sources live in `texFiles/`: edit **writeup.tex** for the main text, **methodology_section.tex** for the methodology, **predefense.tex** for the title page/layout, and **references.tex** for the bibliography.

Rebuild from the `predefense/` directory (the parent of this folder):

```bash
cd ~/Research/Thesis/reports/predefense
bash build.sh
```

`build.sh` runs, from `predefense/`:

```bash
export TEXINPUTS="texFiles//:$TEXINPUTS"   # lets \input{writeup.tex} etc. resolve
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build texFiles/predefense.tex   # twice
python3 scripts/count_words.py
cp build/predefense.pdf predefense.pdf
```

Image paths in the sources (`figs/`, `assets/`, `static_case/figures/`) are relative to `predefense/`, so compile from there, not from inside `texFiles/`.

The word count and its definition are in `WORD_COUNT.txt`. The reproducible counter includes prose, headings, figure captions, and table text; it excludes bibliography, title-page metadata, mathematical expressions, and words embedded within image files. The extracted counting text is `build/word_count_text.txt`.

All newly created report files are within this directory. Existing `static_case/` analyses and `figs/` assets are preserved. Imported images are copied into `assets/`. Three selected papers from the requested rclone paper collection are stored in `reference_sources/` for reference checking; they are not bundled inside the report PDF.

## Items deliberately left open

- Cover details are filled from `Top Page info.md`: both authors and IDs, supervisor, department, institution, and 30 September 2026. A degree designation is not added because the supplied cover information does not specify one.
- Identified reduced-order model, retained dimension, prediction errors, and completed control results.
- Digitized benchmark overlay and quantitative validation errors. `eldredge_validated.png` contains computed curves, not an overlaid reference-data comparison.
- Edition/publisher/year of the Strogatz book actually consulted.
- Final publication metadata for the Durante manuscript. Authors, title, journal, and year were verified from the supplied manuscript; uncertain remaining fields are visibly marked.
- Grid/domain convergence and the physical mechanism of the 29°–30° jump are limitations, not invented results.

No essential requested image was missing. The file named `pod_regimes_vorticity.png` was found in the notes' `Figures` directory. It contains instantaneous fields at 10°, 20°, and 28°, not POD eigenmodes. It is included with the correct caption.

## Print and figure choices

The report uses A4 pages, 24 mm margins, 11 pt Computer Modern text, vector static-result plots, and the supplied high-resolution raster pitching figures. All figure captions identify relevant distinctions in averaging or error-bar definitions. The decomposition figure has only its interpretive headline cropped; the plotted data and legend are retained.

The main force panel follows the requested dotted post-shedding means and solid extrema. The alternative mean-solid/min–max-bar lift plot remains available at `static_case/figures/01_lift_errorbars.pdf`, with both choices together in `static_case/lift_alternatives_A4.pdf`.

See `SOURCE_NOTES.md` for source locations and scientific corrections made while drafting.

The methodology now follows the author’s original `methodology_writeup.md`, preserving its mesh table, both solver tables, three-stage time-stepping procedure, ALE derivation, and polynomial input. The input-function subsection is last. The original word target is treated as approximate; author-provided content is not trimmed to force compliance. Necessary equation corrections and case-setting discrepancies are explicitly identified.

Author clarification: the authoritative methodology source is `/home/raji/Research/Thesis/reports/predefense/methodology_writeup.md`. It was read directly and its paragraphs, three tables, time-stepping phases, ALE equations, and input function are represented in `methodology_section.tex`. The source Markdown is unchanged.
