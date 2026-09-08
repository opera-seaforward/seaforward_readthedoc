# 03 — Composite Validation (multi-cycle, DCC process V1)

**SEA-FORWARD** · OPERA Capacity Development · OceanPrediction-A toolkit

`02_validation.ipynb` validates **one** forecast cycle, indexed by calendar
date. `03_composite_validation.ipynb` instead **merges several cycles**
into one composite analysis, indexed by **forecast lead time** rather than
calendar date:

```
cycle 20260701's days -> sp1, sp2, fcst1, fcst2, fcst3, ...
cycle 20260706's days -> sp1, sp2, fcst1, fcst2, fcst3, ...
cycle 20260711's days -> sp1, sp2, fcst1, fcst2, fcst3, ...
                              |
                              v
              composite, one figure/score per lead
```

`sp1`, `sp2`, ... label the model **spin-up** days (the first
`SPINUP_DAYS` calendar days of each cycle); `fcst1`, `fcst2`, ... label
forecast lead day 1, 2, ... A cycle that doesn't reach a given lead (a
shorter forecast) is simply skipped for that lead — not raised as an
error — so cycles of different length can be composited together.

## Setup

Same imports as `02_validation.ipynb`, plus the composite-only module:

```python
import sftools.postprocess as pp
import sftools.validation as val               # single-cycle building blocks
import sftools.validation_composite as vc       # composite (multi-cycle, lead-time) layer
from sftools.download import cmems
import _paths
```

## 0. Cycles to composite

Pick **at least two** cycle directories (`YYYYMMDD`) under
`MAIN_DIR/CONFIG`. Leave `SEAFORWARD_CYCLES` unset and the in-notebook
list empty to composite **every** available cycle automatically.

`COMPOSITE_DIR` is named with a short uuid rather than the (potentially
very long) cycle list itself; the actual list of cycles a given composite
run covers is written to `validated_cycles.txt` inside that directory. The
uuid is only minted once per distinct set of cycles — every existing
`validation_composite_*` folder is checked first and reused if the cycle
set matches, so re-running the notebook on the same cycles doesn't create
a new directory each time.

## 1b – 1c. Availability and per-cycle downloads

Identical, shared, platform-level availability check to
`02_validation.ipynb` Section 1b (`mercator_forecast`, `ostia_l4`,
`odyssea_l3s`, `smos_l4_sss`). Section 1c then loops the exact per-cycle
resolve/download logic of `02_validation.ipynb` Section 1c over every
cycle in `CYCLES`, and labels each calendar day within each cycle with its
lead-time label (`vc.label_cycle_days`). The result, `cycles_info`, is a
list of one dict per cycle and is what every later section iterates over.

## Section map

| Section | Composite counterpart of (`02_validation.ipynb`) | What it does |
| --- | --- | --- |
| 2 | Section 2 | Composite bias maps by lead time — one 2×2 figure per lead (`sp1`, `sp2`, `fcst1`, ...), pixel-averaged across every cycle reaching that lead: composite-mean CROCO, composite-mean Copernicus, mean bias |
| 3 | Section 3 | Composite scatter plots by lead time — points **pooled** (concatenated) across every contributing cycle |
| 4 | Section 4 | Composite GODAE scorecard (`vc.godae_scorecard_composite`) + Taylor diagram, one per lead, points pooled across cycles |
| 5 | Section 5 | Automated pass/fail summary, composite, forecast leads only — spin-up exclusion is just `report['lead'].isin(FCST_LEADS)` since spin-up is already a separate set of lead labels rather than the first N calendar days |
| 5b | Section 6b | Composite domain-wide bias boxplot by lead time (spin-up included, so the transient is visible), via `vc.composite_domain_diff` plotted with the same `sftools.validation.bias_boxplot` the single-cycle notebook uses |
| 5c | Section 6c | Composite CROCO-vs-satellite domain-wide bias boxplot by lead time (OSTIA/ODYSSEA grouped, SMOS separate), via `vc.composite_domain_diff_satellite` |
| 5d | Section 6 | Composite point + full-domain mean ± 1 std time series by lead, CROCO vs parent and vs satellite |
| 5e | Section 2b | Composite vertical profiles (point and full-domain), mean ± 1 std across every cycle reaching `PROFILE_LEAD`, for temp/salt/speed |
| 6 | Section 7 | Composite satellite SST validation map (OSTIA, ODYSSEA), one figure per lead |
| 6b | Section 7b | Composite satellite SSS validation (SMOS), one figure per lead |
| 7 | Section 9 | Composite self-contained HTML summary, via `vc.build_html_summary_composite` — a thin wrapper around the same `val.build_html_summary` the single-cycle notebook uses, so report layout/lightbox/grouping code is never duplicated |

## Merging rule

Everything in this notebook merges cycles by **lead label**, not calendar
date. `sp1`/`sp2` = model spin-up (first `SPINUP_DAYS` day(s) of every
cycle); `fcst1`, `fcst2`, ... = forecast lead day 1, 2, ... A cycle that
doesn't reach a given lead is skipped for that lead only, so cycles of
different length composite together cleanly.

!!! note
    In-situ validation (Section 8 of `02_validation.ipynb`) is **not yet
    ported** to the composite notebook — the composite HTML report has no
    in-situ section. Use the single-cycle notebook per cycle if you need
    in-situ scoring.

<div style="display:flex; justify-content:center; margin:10px 0 14px 0;">
   <a href="https://raw.githubusercontent.com/opera-seaforward/seaforward_readthedoc/main/docs/notebooks/03_composite_validation.ipynb" data-download-url="https://raw.githubusercontent.com/opera-seaforward/seaforward_readthedoc/main/docs/notebooks/03_composite_validation.ipynb" data-download-filename="03_composite_validation.ipynb" onmouseover="this.style.transform='scale(1.08)'; this.style.boxShadow='0 10px 24px rgba(0,0,0,0.18)';" onmouseout="this.style.transform='scale(1)'; this.style.boxShadow='none';" style="display:inline-flex; align-items:center; justify-content:center; gap:16px; min-width: 80px; padding:20px 20px; border-radius:10px; background:linear-gradient(to bottom, #ffffcc 0%, #f4f797de 100%); color:#000000; text-decoration:none; font-size:1.2rem; line-height:1.1; text-align:center; transition:transform 0.18s ease, box-shadow 0.18s ease; transform-origin:center;">
      <img src="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/icons/download.svg" alt="" aria-hidden="true" style="width:25px; height:25px; color:#000000; font-weight:bold filter:invert(1);" />
      <span>Download notebook 03_composite_validation.ipynb</span>
   </a>
</div>
