# Sources and editorial decisions

## Starting material

The requested resource index was found at `/home/raji/Research/Notes/airfoil_research/predef_writeup_Resource_locations.md` (one directory above the supplied path). Its required BUET sections are all represented: title, background, objectives, methodology, possible outcomes, results, societal obligations, sustainability, complex engineering mapping, and references.

The wording and organization use the background, Objectives, Predefense Methodology, and Results and Validation notes in `/home/raji/Research/Notes/airfoil_research/Thesis_Predefense/`. Existing prose is lightly edited where retained. Empty material is supplied as original bridging discussion or explicitly identified future work.

## Local scientific evidence

- Stationary numerical values: `static_case/data/angle_statistics.csv` and `comparison_29_30.json`; processing definitions in `static_case/README.md`. These refined whole-orbit values take precedence over older coarse-spectrum reports in `/home/raji/nabil_figures/data_and_reports/airfoil_re500/`.
- Hopf estimate: `/home/raji/Research/Thesis/static_airfoil/FINDINGS.md`, section 19.
- Mesh/methodology: the pre-existing methodology files here and current case dictionaries. The current `/home/raji/nabil_pitch_re500/K04/system/controlDict` specifies deltaT 0.0002. The generator default is different, so the report cites the current dictionary and does not claim a uniform timestep throughout all restarts.
- Motion and coordinate conventions: `/home/raji/nabil_pitch_re500/make_pitch_case.py`, `eldredge_ramp.py`, and K04 dictionaries.
- Pitching figure interpretation: `/home/raji/nabil_figures/README.txt` and supplied plot annotations. The early hold value is identified as a supplied selected statistic, not a independently established asymptotic mean.
- Plate response: `/home/raji/nabil_figures/data_and_reports/plate_re1000/STATIC_REPORT.md` and `eldredge_validated.png`. No published-curve overlay or quantified validation error was present in that figure.
- Vorticity fields: `/home/raji/Research/Notes/airfoil_research/Figures/pod_regimes_vorticity.png`. The embedded labels specify 10°, 20°, 28°; do not confuse these with the 11°, 20°, 26° surface-analysis specimens.

## Corrections to preliminary statements

- A linear growth-rate crossing does not alone establish supercriticality; the report says Hopf onset.
- Chord-based carrier Strouhal decreases; it is not constant. A height-based Strouhal uses a different length scale.
- At 26°, subharmonic amplitude/carrier amplitude is 0.949, not greater than one. Amplitude ratios are not power ratios.
- The 29°–30° jump is pressure-associated and remains period two in the analyzed records; no new bifurcation is claimed.
- The stationary efficiency maximum is near 14°, not 15°. The figure averages instantaneous lift/drag, rather than dividing their separate means.
- Mesh angular velocity is the derivative of angle. The momentum diffusion coefficient is kinematic viscosity when density has been divided out.
- POD-pattern filenames do not establish that POD analysis has been completed. The selected image contains ordinary vorticity snapshots.
- Classical apparent-mass subtraction is called a diagnostic residual at large separated incidence, rather than exact circulation isolation.
- Re500 quarter-chord NACA0012, Re1000 leading-edge flat plate, and older Re1000 smootherstep NACA0012 tests are separate campaigns.
- No grid independence, finished ROM, or successful feedback control is fabricated.

## Verified external references

The report bibliography contains direct DOI links. Primary bibliographic checks used:

- Eldredge & Jones: https://www.annualreviews.org/content/journals/10.1146/annurev-fluid-010518-040334
- Kurtuluş: https://journals.sagepub.com/doi/10.1177/1756829316653700
- Brunton, Rowley & Williams: https://collaborate.princeton.edu/en/publications/reduced-order-unsteady-aerodynamic-models-at-low-reynolds-numbers/
- Gupta et al.: https://research.monash.edu/en/publications/two-and-three-dimensional-wake-transitions-of-a-naca0012-airfoil/
- Dawson & Brunton: https://arxiv.org/abs/2104.15122
- Brunton & Kutz: https://doi.org/10.1017/9781108380690
- Katz & Plotkin: https://doi.org/10.1017/CBO9780511810329
- Brunton, Noack & Koumoutsakos: https://www.annualreviews.org/content/journals/10.1146/annurev-fluid-010719-060214
- Eldredge & Wang and Durante et al.: PDFs downloaded from `gdrive-altair:/papers` into `reference_sources/`, inspected directly.

The revised background closely follows the original prose and structure. The flight-regime and Gupta figures are included. Williamson illustrations are excluded at the user’s request, while the Williamson reference and mode comparison are retained. Weller et al. (1998) is cited in the OpenFOAM methodology. Supplemental prose in the proposed-outcomes section was trimmed to preserve the requested word budget. The Strogatz edition and Durante final citation fields remain explicit placeholders rather than guesses.

Additional reference checks: Weller et al. author-hosted article (ResearchGate, Hrvoje Jasak), DOI 10.1063/1.168744; Williamson publisher page https://www.annualreviews.org/content/journals/10.1146/annurev.fl.28.010196.002401; Alam institutional record https://research.polyu.edu.hk/en/publications/the-ultra-low-reynolds-number-airfoil-wake/; Barkley and Henderson bibliographic entry in the supplied Gupta paper. Original mode-angle ranges were omitted because the preliminary list gives incomplete intervals. Grammar, spelling, potential-flow qualifications, and the historical attribution of mode classifications were corrected without replacing the user’s progression.

Cover metadata supplied by `/home/raji/Research/Notes/airfoil_research/Top Page info.md`: Imdadullah Raji (2110099), Abdullah al Mamun (2110062), Department of Mechanical Engineering, Bangladesh University of Engineering and Technology, supervisor Dr Md Ali, date 30 September 2026. No degree or supervisor rank was inferred.

Methodology revision: restored the source wording, all three technical tables, ALE chain rule and momentum equation, and smootherstep input. Only grammar, vector notation, angular velocity (dot alpha), viscosity/pressure convention, and negative-time clamping were corrected. The input subsection and its figure are last. Source v13 identification and older pitching tolerances are retained as explicit reconciliation items; the current Eldredge case is distinguished from the original prescribed-step case. No trimming was performed to enforce the former word target.

Author clarification: the authoritative methodology source is `/home/raji/Research/Thesis/reports/predefense/methodology_writeup.md`. It was read directly and its paragraphs, three tables, time-stepping phases, ALE equations, and input function are represented in `methodology_section.tex`. The source Markdown is unchanged.
