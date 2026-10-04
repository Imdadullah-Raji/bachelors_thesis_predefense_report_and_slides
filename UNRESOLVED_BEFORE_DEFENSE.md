# ⚠ UNRESOLVED — FIX BEFORE THE PREDEFENSE ⚠

Open items in the talk (`slides/predefense.pptx`) and the report. The talk
cannot go out while anything under **Blocking** is open.

---

## Blocking

### 1. The talk has no results slides
The deck runs (13 slides): cover → opening quote (Feynman) → objectives (2)
→ methodology (3) → literature review (4) → books and code → Q&A.
The literature review is complete as specified in `lit_review.md`: wake
patterns, period doubling/chaos, spanwise instability, pitching and LEV.
**There are no results slides yet.** They go between the literature review and
the books slide. References are numbered in order of appearance at build time,
so adding slides renumbers them automatically.

### 1a. Some speaker notes were drafted by me, not you
All notes now come from one file, `scripts/speaker_notes.py`, which generates
both the notes in the `.pptx` and the printed `slides/speaker_notes.pdf` (A4).
Text I wrote where the `.md` had none is **blue** in the PDF and starts with
**[drafted]** in the `.pptx`: cover, the last line of the wake-patterns slide,
the whole LEV slide, books and code, and Q&A. Your own text has grammar
corrections only, plus one number: "10 megabytes" → "about 12 megabytes"
(the actual POD file size). **To change notes from now on, edit
`scripts/speaker_notes.py`**, not the `.md` files. Then rebuild both outputs.

### 1b. Check the source of the pitching-plate figure
`assets/pitching_plate.png` is typeset in Annual Reviews style, so slide 11
cites **Eldredge & Jones (2019), Annu. Rev. Fluid Mech.** If the figure came
from Eldredge & Wang (2010), change the citation key in
`scripts/build_slides.py` (`cite('eldredge2019')` → `cite('eldredge2010')`,
and add that entry to `REFS`).

### 2. Expect this question: "Your 2D results sit past the 3D onset"
Gupta's regime map (slide 10) puts the 3D transition at about **α ≈ 18° for
Re = 500** (the α₃D ∼ Re^−0.5 curve reaches Re = 500 near 18°). Your
period-doubled cases (α = 24–30°), and the α = 26° "mode 3" video on slide 8,
lie beyond it. In a real flow those wakes would be three-dimensional. The note
on slide 7 says exactly this for Durante's results. Have an answer ready for
why 2D is still useful, e.g. as a model problem or a controlled 2D reference
for reduced-order modelling.

### 3. SINDy is missing from the report's literature review
- The talk cites Brunton, Proctor & Kutz, "Discovering governing equations
  from data by sparse identification of nonlinear dynamical systems," *PNAS*
  113(15), 3932–3937, 2016 (slide 4, reference [2]).
- **This paper is not in the report's reference list.** The report only cites
  Dawson & Brunton (arXiv 2021), who apply SINDy to the Wagner function.
- Planned: add SINDy to the "third section" of the literature review.
  **Check which section you mean:** the third subsection is §1.3 *Rapid
  motions and leading-edge vortices*. §1.4 *Reduced-order modeling* already
  discusses POD, DMD and Dawson & Brunton's SINDy work, so it is the natural
  home.
- This applies to both `texFiles/writeup.tex` and the writeup copies. The
  reader copy is generated with `scripts/make_reader_copy.py`.

---

## Speaker notes: facts not verified or not matching the data
The notes are copied into the deck word for word from `slides_mds/*.md`, which
are the source. The copies are hard-coded in `scripts/build_slides.py`, so an
edit to an `.md` also needs the matching string updated there, or send it to me.

| Slide | Note says | What was found |
|---|---|---|
| Wake patterns | "She studied a NACA0010 airfoil" | **Wrong airfoil.** Her own panels are labelled NACA0012 (mode 2) and NACA0002 (mode 3), and Durante et al. describe the work as "Kurtulus (2016), where a NACA0002 profile was compared with the former NACA0012". NACA0010 appears in Durante's review of a *different* study. |
| Period doubling | "a small and large peak near $\alpha=$" | **The angle was blank.** The deck notes say **α = 22°**, where Durante first shows two peaks and two Poincaré points (their Fig. 4 and Fig. 6). Confirm. |
| 2 Introduction | "a calculation that took 2 hours on 6 cores" | **Not verified.** Check the run log of the intro case. |
| Reduced-order models | "this POD takes only 10 megabytes" | The POD file `pod_re500_aoa28_20.nc` is **12 MB** (20 modes); the case directory is 16 GB. The slide bullet says 12 MB. |
| Reduced-order models | "fractions of milliseconds … 19 µs on a single core" | Measured: ≈ **19 µs** for a 4-mode field reconstruction on one core. Matches. |
| 5 Numerical solver | *(fixed)* "no scales to resolve" | You rewrote it: "the smallest scale to resolve is the boundary layer thickness δ". The deck notes now match. |

---

## Decisions I made that you should confirm

- **Feynman quote wording.** The slide uses Feynman's text: "The test of
  science is its ability to predict. Had you never visited the earth, could you
  predict the thunderstorms, the volcanos, the ocean waves, the auroras, and
  the colorful sunset?" `objective.md` has "Test" capitalised, "volcanoes",
  and no question mark.
- **Brunton & Kutz edition.** The books slide lists the **2nd edition
  (2022)** as `slides_styles.md` asks. The report cites the **1st edition
  (2019)**. Make them agree.
- **POD video uses 4 modes, not 2.** At α = 28° the wake is period-doubled:
  2 modes hold 50 % of the fluctuation energy, 4 modes hold 89 %. The video
  shows 2 periods in 20 s. *T* on the traces is the fitted 5.33 period of the
  full orbit.
- **The intro video is used unchanged.** It is low-resolution (608 × 368) and
  uses a colour palette that differs from the report's. It can be re-rendered
  in the report style if needed.
- **The wake-mode slide pairs our Re = 500 runs with Kurtuluş's Re = 1000
  modes:** α = 14° is shown as mode 2 and α = 26° as mode 3 (period-2), as
  `lit_review.md` asks. The Reynolds number differs, and the slide says so.
- **Kurtuluş figures are unchanged apart from trimming** the white page
  border and a sliver of a neighbouring panel. Their green colour map is
  kept, as you asked.
- **The Durante slide shows four regimes, not three.** Columns: period 1
  (α = 13°), period 2 (22°), period 3 (25°) and chaotic (27°). Rows: lift
  history, spectrum, phase portrait. There are 12 panels, each cropped
  unchanged from their Figs 4–6, 8–10 and 12–14. The period-3 column is there
  because your note mentions it. Drop it if the slide is too busy.
- **The Durante reference has no volume number.** The PDF is the preprint.
  The slide gives the article number from the DOI (105285), like the report.
  The report's entry should get the volume too.
- **The cover has no date.** `objective.md` lists none. The report's title page
  says 30 September 2026.

---

## Carried over from the report work

- `texFiles/writeup.tex` (your original report) still has the old flat-plate
  benchmark figure and its `\todo`. Only the writeup copies have the new
  overlay with peak values.
- Everything else missing from the report is listed in the **Gap register**
  at the end of `writeup/predefense_author.pdf`.

---

## Rebuild commands (run from `predefense/`)

```bash
conda run -n talkbuild python scripts/build_slides.py      # the deck
conda run -n talkbuild python scripts/speaker_notes.py     # printed notes (A4 PDF)
conda run -n flowkit   python scripts/make_pod_video.py    # POD video (~3 min)
conda run -n flowkit   python scripts/make_wake_videos.py  # α = 14°, 26° wake videos (~4 min)
bash writeup/build.sh                                 # author + reader reports
```
