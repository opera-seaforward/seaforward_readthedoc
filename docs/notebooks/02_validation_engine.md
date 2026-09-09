# Validation: One Engine, TWo Ways To Run It

`sftools.validation` -- contents the GODAE OceanView scorecard (bias, RMSD, unbiased RMSD, correlation, two scatter-index variants, std-ratio) plus optional class-4 in-situ scoring per depth layer -- is now the **single
statistics engine** behind every validation surface in this repo:

```
sftools.validation.godae_scorecard_croco_vs_glorys()   <- grid vs reference, one variable
sftools.validation.compare_timeseries()           <- grid vs reference time series, for single point or full domain
```

...used identically by:

1. **`02_validation.ipynb`** (interactive, single cycle, Sections 2-4) —
   builds the same scorecard, draws the Taylor diagram, and (Section 8,
   optional) scores against in-situ obs.
2. **`03_composite_validation.ipynb`** (interactive, multi-cycle) — the
   same single-cycle building blocks from `sftools.validation`, called
   through `sftools.validation_composite` (module `vc`) to merge several
   cycles by **forecast lead time** rather than calendar date — see
   "Composite (multi-cycle) validation".

Because all two go through the same statistics engine, they can't silently disagree with each other. One correctness note worth knowing: CROCO's `zeta` has no absolute geoid reference, so the SSH comparison is done on **anomalies** (domain mean removed from both fields) rather than raw levels — otherwise an arbitrary offset between CROCO's and the reference's reference level would show up as spurious "bias" that isn't a real skill difference.

## 02_validation.ipynb — section map

The notebook's actual section numbering:

| Section | What it does |
| --- | --- |
| 1 | Load model output, grid/time sanity check, numerical-stability check |
| 1b | Reference-product availability (Copernicus Marine: forecast parent, OSTIA, ODYSSEA, SMOS) — a metadata-only check, nothing is skipped here yet |
| 1c | Downloads the reference products for this cycle into `downloaded_data/` |
| 2 | Bias maps — CROCO vs Copernicus Marine Forecast parent (SST, SSH, currents, SSS) |
| 2b / 2b-bis | Vertical profile & error-vs-depth, point and full-domain |
| 2c | Depth-resolved comparison at 4 levels (surface, 120 m, 300 m, 1000 m) |
| 3 | Scatter plots, pointwise CROCO vs parent |
| 4 | GODAE scorecard + Taylor diagram |
| **5** | **Automated pass/fail summary (V1)** — reads directly from the Section 4 scorecard, so it can't drift out of sync with the Taylor diagram or with `run_validation.py`'s own report |
| 6 / 6b / 6c | Time series and domain-wide bias boxplots, vs parent and vs satellite |
| 7 / 7b | Satellite SST (OSTIA, ODYSSEA) and SSS (SMOS) validation |
| **8** | **In-situ validation (optional)** — off by default; a cycle/region with no matching in-situ profiles isn't a failure, the section just reports "nothing to score" and moves on |
| 9 | Self-contained HTML summary report (`index.html`) |



!!! note
- Every reference-product comparison in Sections 2 onward is
**availability-guarded**: if `AVAIL['mercator_forecast']` (or the relevant
satellite flag) is `False`, that section is skipped and says why, rather
than raising an error — a temporary CMEMS outage or missing credentials is
not a V1 validation failure.



<div style="display:flex; justify-content:center; margin:10px 0 14px 0;">
   <a href="https://raw.githubusercontent.com/opera-seaforward/seaforward_readthedoc/main/docs/notebooks/02_validation.ipynb" data-download-url="https://raw.githubusercontent.com/opera-seaforward/seaforward_readthedoc/main/docs/notebooks/02_validation.ipynb" data-download-filename="02_validation.ipynb" onmouseover="this.style.transform='scale(1.08)'; this.style.boxShadow='0 10px 24px rgba(0,0,0,0.18)';" onmouseout="this.style.transform='scale(1)'; this.style.boxShadow='none';" style="display:inline-flex; align-items:center; justify-content:center; gap:16px; min-width: 80px; padding:20px 20px; border-radius:10px; background:linear-gradient(to bottom, #ffffcc 0%, #f4f797de 100%); color:#000000; text-decoration:none; font-size:1.2rem; line-height:1.1; text-align:center; transition:transform 0.18s ease, box-shadow 0.18s ease; transform-origin:center;">
      <img src="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/icons/download.svg" alt="" aria-hidden="true" style="width:25px; height:25px; color:#000000; font-weight:bold filter:invert(1);" />
      <span>Download notebook 02_validation.ipynb</span>
   </a>
</div>


