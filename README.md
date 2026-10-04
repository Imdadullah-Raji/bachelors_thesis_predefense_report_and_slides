# BSc thesis predefense: report and slides

**Modeling and Control of Unsteady Flows over Rapidly Maneuvering Airfoils at Ultra-Low Reynolds Number**
Imdadullah Raji (2110099), Abdullah Al Mamun (2110062) · Supervisor: Dr Md Ali
Department of Mechanical Engineering, BUET · Predefense, 30 September 2026

This repo holds the sources for our predefense report and talk. The large files (PDFs, decks, figures, videos) are on Google Drive. [`archive/README.md`](archive/README.md) explains how to get them back.

---

## 1. What it is about

<img src="docs/readme/lev.gif" width="480" align="right" alt="Leading-edge vortex rolling up on a pitching NACA0012">

When a small wing pitches up fast, a **leading-edge vortex** rolls up on top of it and the lift briefly shoots far above its static value (animation on the right). We want a **reduced-order model** of this flow: a model with only a few degrees of freedom that still captures the physics, so that it can run fast enough for real-time control.

Plan of the thesis:
1. Characterize the flow physics of a pitching NACA0012 at low Reynolds number (2D OpenFOAM simulations).
2. Find a low-dimensional representation of the flow with data-driven methods (POD, DMD, SINDy).
3. Build a reduced-order model that predicts the lift for a given pitching input.
4. Check whether that model is robust enough for flow control.

The predefense covers the literature review, the simulation methodology, and the first results. The reduced-order model and the control part are still to come.

### Results so far

**Stationary airfoil at Re = 500.** As the angle of attack increases, the wake goes from steady, to periodic shedding (onset at α ≈ 11.5°), to period-doubled shedding (between 24° and 25°).

<img src="docs/readme/regimes.png" width="560" alt="Vorticity at 10, 20 and 28 degrees: steady, period-1, period-2">

**Pitch-up maneuver** (Re = 500, K = 0.4, 0° → 30°). Peak lift is about 4.3× the static value at the same angle. After the hold, the lift relaxes back to the static value.

<img src="docs/readme/pitch_vs_static.png" width="560" alt="Dynamic lift vs static lift during pitch-up">

**Why a low-order model is plausible.** At α = 28°, four POD modes hold 89% of the fluctuation energy.

<img src="docs/readme/pod.png" width="720" alt="Four-mode POD reconstruction of the wake">

**The talk** has ~13 generated slides, plus results slides added by my thesis partner (`predefense_with_results.pptx`). Here is one of the generated slides:

<img src="docs/readme/slide_example.png" width="720" alt="Example slide: pitching airfoil and the leading-edge vortex">

### Where things are

| Path | What | Made by |
|---|---|---|
| `markdowns/` | Literature review, objectives, methodology notes. Everything else was built from these. | me |
| `slides_mds/` | Slide-by-slide spec, speaker notes and style rules for the talk | me |
| `texFiles/`, `build.sh` | LaTeX source of the report → `predefense.pdf` | Claude |
| `writeup/` | Author copy of the report (red boxes mark missing evidence) and a clean reader copy; `writeup/build.sh` builds both | Claude |
| `scripts/build_slides.py` | Builds the deck → `slides/predefense.pptx`; equation images and `mesh_motion.mp4` go to `slides/media/` | Claude |
| `scripts/speaker_notes.py` | Speaker notes → the `.pptx` notes pane and `slides/speaker_notes.pdf` | Claude (from my notes) |
| `static_case/` | Stationary-airfoil plots: `make_figures.py` → `static_case/figures/`, extracted data in `static_case/data/`, 29° vs 30° comparison | Claude |
| `scripts/render_mesh.py`, `scripts/make_mesh_figure.py` | Mesh pictures → `figs/mesh_*` | Claude |
| `scripts/make_wake_videos.py` | Wake videos → `figs/wake_video/` | Claude |
| `scripts/make_pod_video.py` | POD video → `figs/pod_video/` | Claude |
| `figs/pitch_plot_digitized/`, `scripts/make_benchmark_overlay.py` | Digitized Eldredge & Wang plot and our benchmark overlay → `figs/benchmark_overlay.*` | Claude |
| `assets/` | Pitching and stationary figures and videos copied in from my earlier analysis (also made with Claude) | Claude |
| `figs/` (Gupta, Williamson, regime map), `slides/media/ref_*` | Figures and citation images from published papers | the papers' authors |
| `reference_sources/` | The papers used to check the report's claims | the papers' authors |
| `scripts/count_words.py` | Word count → `WORD_COUNT.txt` | Claude |
| `predefense_with_results.pptx` | The final deck with results slides | my thesis partner, with Claude |
| `UNRESOLVED_BEFORE_DEFENSE.md` | Open issues and questions to expect at the defense | Claude |
| `archive/` | Git/Drive split and asset sync scripts | Claude |

**Not in this repo or on Drive yet:** the simulation case files and the raw data. That covers the OpenFOAM cases and meshes (`~/Research/Thesis/static_airfoil/`), the extra-angle runs (`~/Research/Thesis/downloads/Re500/`), the flow snapshots behind the POD and wake videos (`~/ddse/pod_recon/`), and my older figure folder (`~/Research/Notes/airfoil_research/Figures/`). The figure scripts read from these local paths, so they won't run elsewhere yet. I will upload these soon and link them here.

---

## 2. How all of this was made (honestly)

**I designed and planned the work and wrote the content. Claude did nearly all the hands-on building:** every figure, plot and video, the LaTeX, and the slide code. I don't know how to use python-pptx, and I didn't need to.

**What I did:**
- **Designed and planned the simulations:** the cases, the angle sweep, the pitching maneuver, and the mesh and solver choices (see the methodology). My other repos are [openfoam_cases](https://github.com/Imdadullah-Raji/openfoam_cases) and [flowkit](https://github.com/Imdadullah-Raji/flowkit).
- **Wrote the content** in `markdowns/`: the literature review, objectives and methodology. `methodology_writeup.md` is my original.
- **Wrote the talk** in `slides_mds/`: what goes on each slide, which figure or video, and my speaker notes. `slides_styles.md` has the layout rules: high contrast for a bad projector, a 7-minute talk, references at the bottom of each slide, page numbers.
- **Reviewed every output,** sent back corrections, and decided what stayed in.

**What I did not do:** I did not make any of the figures, plots or videos. I did not write the LaTeX, the slide-building code or any of the scripts in this repo.

**What Claude (Opus 5.5, in Claude Code) did:**
- **Figures, plots and videos:** all of them. Each output and its script is listed in the table above.
- **Report:** turned my markdowns and the figures into the LaTeX in `texFiles/`, and checked claims against the papers in `reference_sources/`. It fixed equations and logged every correction in `markdowns/SOURCE_NOTES.md`. It flagged missing results instead of inventing them, and made the author/reader copies in `writeup/`.
- **Slides:** wrote `scripts/build_slides.py` (~700 lines of python-pptx). The script reads my `slides_mds/`, renders the equations with LaTeX, numbers the references, embeds the videos, and writes the `.pptx`. Notes Claude drafted where mine were missing are marked `[drafted]`.
- **Bookkeeping:** `UNRESOLVED_BEFORE_DEFENSE.md`, and the git/Drive archive in `archive/`.

**What my thesis partner did:** Abdullah Al Mamun added the results slides in `predefense_with_results.pptx`, also working with a Claude agent. Those scripts aren't in this repo yet.

So the work splits like this: **the research design, the content and the judgement calls are mine. The figures, the typesetting and all the code are Claude's.**

### Workflow, if you want to do the same

1. **Write content in markdown first**, one file per section, in your own words. Get the physics right here, not in LaTeX.
2. **Write a slide spec in markdown:** one heading per slide, the content, the figure or video path, and speaker notes. Put style rules in a separate file.
3. **Ask Claude Code to build from those files**, in the same folder as your figures and data. Ask it to generate the outputs with a script (LaTeX, python-pptx), so you can rebuild after every edit instead of editing a binary deck.
4. **Make it list what it can't verify.** A "missing evidence" box in the draft or an UNRESOLVED file is worth more than a polished paragraph that's wrong.
5. **Rebuild, read the PDF and the deck, correct, repeat.** Keep editing your markdown or the script, not the output.
6. **Archive:** code to git, heavy files to cloud storage (see `archive/`).

### Rebuilding

```bash
archive/pull_assets.sh            # fetch figures/videos/PDFs from Drive first
./build.sh                        # report -> predefense.pdf   (pdflatex, detex)
python3 scripts/build_slides.py   # talk   -> slides/predefense.pptx
                                  # (python-pptx, Pillow, lxml, numpy; pdflatex, pdftocairo, ffmpeg, rsvg-convert)
```
