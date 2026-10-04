# Digitized pitch plot

Source: [`../pitch_plot_tobedigitized.png`](../pitch_plot_tobedigitized.png), a 1117 × 1063 raster image. `curves.csv` contains all eight pitch rates (`K = 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1`) in each of its three panels. `redrawn.png` plots the extracted coordinates. The original image is untouched.

The CSV columns are `panel`, `K`, `x`, `coefficient`, and `source`. For panels `a_lift_time` and `b_drag_time`, `x = tU/c`. For panel `c_lift_rescaled_time`, `x = K(tU/c − 1)`. `coefficient` is `C_L` in (a) and (c), and `C_D` in (b).

`source=observed` means that the colour of the curve was present in that image column. `interpolated` fills gaps in a curve. `common_baseline` is the nearly coincident part before the coloured traces separate; the early drag baseline is taken from the visible grey trace. `shared_endpoint` joins overlapping lift curves in panel (c) to their common visible endpoint. These reconstructed portions deserve the most caution.

The axes were calibrated from the labelled ticks. One source pixel corresponds to about 0.011 in `tU/c` and 0.049 in `C_L` for (a), 0.011 in `tU/c` and 0.021 in `C_D` for (b), and 0.0017 in rescaled time and 0.044 in `C_L` for (c). CSV decimals support interpolation; they do not imply that level of measurement accuracy. The curves are approximate raster digitizations, especially near overlaps and cropped endpoints.

As a cross-check, panel (c) repeats panel (a) after the printed time transformation. Across the eight rates, the median absolute differences between corresponding extracted lift values are 0.000–0.012 in `C_L`; the respective peak values agree within 0.06.

Reproduce with:

```bash
conda run -n plot-digitizer python digitize.py
```

## Simulation peak overlay

`plate_summary_nabla.csv` is a local copy of `/home/nabil/Thesis/all_figures/data_tables/plate_summary.csv` from `ssh nabla` (copied on 2026-09-29). The file contains summary peaks, not full simulation time histories. Its `s_Cl` and `s_Cd` coordinates use `s = K(tU/c − 1)`, as confirmed by the remote validation code. `Cd_max` is the pitch-up peak; the separate `startup_Cd` transient is excluded from Figure 3's peak comparison.

`summary_overlay.png` and `summary_overlay.pdf` place its lift and drag peak markers on the paper's original plotted curves. For this primary overlay, the curves are taken from `eldredge_fig3_vector.npz`, copied from the remote thesis's PDF-vector digitization. This source preserves the plotted polyline detail and avoids the peak-time ambiguity of the raster image. `summary_overlay_raster.png` shows the same markers over the local raster extraction above.

`peak_comparison.csv` compares simulation peaks with maxima of the vector-extracted paper curves. Percentage differences use `100 × (simulation/paper − 1)`. Lift values range from 2.69% to 7.78% below the paper; drag values range from 3.80% below to 0.52% above. Peak locations are expressed in rescaled time `s` for both quantities. The other summary columns are not plotted as time histories in Figure 3, so they are not assessed in this peak comparison.

Reproduce the overlays and comparison table with:

```bash
conda run -n plot-digitizer python overlay_summary.py
```
