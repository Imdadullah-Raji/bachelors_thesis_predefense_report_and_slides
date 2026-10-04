# Fixed-angle Re500 predefense figures

Implements the **steady cases** section of `Research/Notes/airfoil_research/Thesis_Predefense/Report graphs.md`. Here “steady cases” means fixed incidence, including the unsteady wake at fixed incidence. Pitching figures and the crossed-out velocity streamline item are outside this set.

## Deliverables

- `print_ready_A4.pdf`: four A4 pages with seven main figures and captions; print at 100%.
- `steady_case_figures.pdf`: eleven figure-only pages, including individual lift, drag, and efficiency panels and both lift-range alternatives.
- `lift_alternatives_A4.pdf`: the two lift presentations on one A4 page. `figures/01_lift.pdf` uses dotted means and solid minimum/maximum curves; `figures/01_lift_errorbars.pdf` uses solid means and asymmetric min-to-max bars. Bars describe the oscillation range, not statistical uncertainty. Both versions use the same windows and numerical data.
- `figures/`: individual vector PDFs (embedded TrueType fonts) and 600-dpi PNGs. Three-panel figures are approximately 180 mm wide, with 9–10 pt principal labels.
- `data/angle_statistics.csv`: angle sweep, time windows, orbit counts, source paths, and stationarity diagnostics.
- `data/steady_solver_statistics.json`: recomputed steady-solver tail statistics, including rejected nonconverged cases.
- `data/spectrum_*.csv`, `data/surface_*.csv`, and `data/surface_windows.json`: numerical spectra and surface distributions with their averaging windows.
- `comparison_29_30_A4.pdf`: focused comparison of the 29° and 30° lift spectra, surface pressures, pressure difference, and phase-folded lift. Its source figure is `figures/07_29_vs_30.pdf`; calculation details are in `data/comparison_29_30.json`. Both angles remain period two. The observed force jump is accounted for approximately by the change in pressure loading, without resolving whether another branch or bifurcation exists.

## Sources and definitions

Even angles 12–30: `static_airfoil/re500_aoa*/postProcessing`. Odd angles 1–29: `downloads/Re500/postProcessBundleOddAngles/re500_aoa*`, extracted from the downloaded ZIP. The archive's force/surface folders have no intermediate `postProcessing` directory. The steady-solver branch uses `static_airfoil/steady_aoa*/postProcessing`.

Each force file's header is checked for `magUInf=1`, `lRef=1`, and `Aref=0.1`. These make frequency in inverse simulation-time units numerically equal to chord-based Strouhal number. Re500 for the odd cases follows the supplied archive/campaign identity; the ZIP does not supply viscosity or complete solver dictionaries for an independent Reynolds-number audit.

1. Restart files are loaded in **numerical** restart-time order. A later segment supersedes older samples at and beyond its first recorded time; exact duplicate times are removed.
2. Even-angle averaging starts use `.phase2` metadata, or the documented campaign starts for 20° and 30°. Odd-angle candidates use the latest restart segment. These are not automatically assumed converged: the resulting windows undergo the checks below.
3. For shedding states, the existing campaign `spectral_structure` routine separates carrier and orbit frequencies. A recurrence-error minimization refines the orbit period. Means use an even integer number of complete orbits from the end of the candidate interval, with boundary values interpolated and trapezoidal time weights. Ratios are averaged as instantaneous `CL/CD`; this is distinct from `mean(CL)/mean(CD)`.
4. First-half versus second-half mean-lift and amplitude changes must each be below 1%; normalized orbit recurrence RMS must be below 2%. The supplied selected windows pass these checks. This checks finite-record stationarity; it does not establish grid independence or uniqueness of an attractor. The CSV includes the errors and selected windows. Quiescent records are identified by lift peak-to-peak below 0.001 and have no assigned physical shedding frequency (CSV frequency fields use zero as a sentinel).
5. The carrier is not chosen simply as the tallest spectral peak: the subharmonic can dominate a period-two case. The CSV additionally reports recurrence error after a carrier period and the amplitude ratio `A(fc/2)/A(fc)` from an eight-component harmonic least-squares fit. These distinguish period-one repetition from period-two repetition.
6. Displayed Fourier spectra are mean-subtracted, uniformly resampled, single-sided Hann-windowed amplitude spectra, corrected for coherent gain. They are **amplitude**, not power spectral density. The frequency spacing is set by the recorded duration; resampling does not improve physical frequency resolution. At 24° a small residual subharmonic remains, so the figure does not assert a literally absent half-frequency component.
7. Surface means use snapshots bracketing the selected interval, coordinate alignment, endpoint interpolation, and trapezoidal time weights. The oscillatory surface intervals span complete orbits and reject large sampling gaps. The pre-shedding specimen is the terminal steady physical state at 11°; the other specimens are 20° and 26°. The plotted pressure coefficient is read from the sample and checked against `Cp=2p`.
8. Wall shear is the **signed tangential traction on the wall**, normalized by `rho U_inf^2`. Following the established campaign sign convention, the stored OpenFOAM wallShearStress vector is negated, then projected onto the local surface tangent directed toward increasing x on each side. Tangents are computed from the sampled geometry. The vertical blunt trailing-edge face (`x/c=1`) is excluded; the upper and lower airfoil surfaces are retained. The inset displays the upper-surface values on a magnified linear scale.
9. Delay portraits use `tau=1/(4 fc)`, draw the last four complete orbits, and include sufficient preceding history for the delayed coordinates. The 3D view is supplied for 26° as an alternative to the three-panel 2D comparison.

## Interpretation limits

- The data support **period one at 24° and period two at 25°**. The hatched band is the sampled bracket `(24°,25°]`; no exact bifurcation point has been inferred. Different initial conditions could require further investigation near the transition.
- SIMPLE histories at 22° and 24° oscillate in iteration space and are not converged steady solutions. They are recorded in the diagnostics but excluded from the steady branch.
- The supplied 29° and 30° runs have a visible jump in mean forces. The figures preserve that observation without smoothing or attributing it to an additional bifurcation. These plots alone cannot determine its cause.
- No velocity-field streamlines or pitching results are synthesized from force/surface data.

## Reproduction

From the thesis workspace:

```bash
/home/raji/miniconda3/envs/research/bin/python reports/predefense/static_case/make_figures.py
cd reports/predefense/static_case
pdflatex -interaction=nonstopmode -halt-on-error print_ready_A4.tex
pdflatex -interaction=nonstopmode -halt-on-error lift_alternatives_A4.tex
/home/raji/miniconda3/envs/research/bin/python compare_29_30.py
pdflatex -interaction=nonstopmode -halt-on-error comparison_29_30_A4.tex
```

The ZIP must already be extracted under `downloads/Re500/`. Original simulation files and the remote archives are not modified by the plotting script.
