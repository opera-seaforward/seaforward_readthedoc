# 06 — Animation (DCC process D1, dissemination/outreach)

**SEA-FORWARD** OceanPrediction-A toolkit

Time-evolving companion to `01_seaforward_postprocess_plot.ipynb`'s static
maps: five animations over a CROCO run, all built on a single entry point,
`sftools.animation.animate(ds, var, overlay=...)`.

| Section | Animation | Call |
| --- | --- | --- |
| 2 | Sea Surface Temperature & wind stress | `anim.animate(ds, "temp", overlay="wind")` |
| 3 | Sea Surface Height & surface currents | `anim.animate(ds, "zeta", overlay="uv")` |
| 4 | Current speed & quivers | `anim.animate(ds, "speed", overlay="uv")` |
| 5 | Zonal current (u) | `anim.animate(ds, "u", overlay="uv")` |
| 6 | Meridional current (v) | `anim.animate(ds, "v", overlay="uv")` |


## 0. Find and select a cycle

Same discovery pattern as `02_validation.ipynb` Section 1 and
`01_seaforward_postprocess_plot.ipynb` Section 0: every run lives in a
cycle directory named `YYYYMMDD`, sibling to every other cycle under
`<MAIN_DIR>/<CONFIG>/`. `RUN_TYPE` distinguishes a forecast cycle
(`fcst/CROCO_FILES/croco_his.nc`) from a hindcast cycle
(`hcast/CROCO_FILES/croco_his.nc`) — this notebook's original example
pointed at a hindcast run, so `RUN_TYPE` defaults to `"fcst"` here but the
environment variable lets you pick either. Every available cycle under
`MAIN_DIR/CONFIG` for that `RUN_TYPE` is listed; pick one with `CYCLE` (or
the `SEAFORWARD_CYCLE` environment variable).

```python
CONFIG   = os.environ.get("SEAFORWARD_CONFIG", "Canary_12")
RUN_TYPE = os.environ.get("SEAFORWARD_RUN_TYPE", "fcst")   # "fcst" or "hcast"
MAIN_DIR = os.path.expanduser(
    os.environ.get("SEAFORWARD_MAIN_DIR",
                   f"~/seaforward/{'forecast' if RUN_TYPE == 'fcst' else 'hindcast'}/model-runs"))
```

`Yorig` follows the same convention as every other notebook: 1993 for
hindcast (GLORYS reanalysis time origin), 2000 for forecast (Copernicus
Marine Forecast / Mercator anfc).

## 1. Load the CROCO dataset

```python
ds = pp.open_history(H, Yorig=YORIG)
```

## 2–6. The five animations

```python
anim.animate(ds, "temp", overlay="wind")   # SST & wind stress
anim.animate(ds, "zeta", overlay="uv")     # SSH & surface currents
anim.animate(ds, "speed", overlay="uv")    # current speed & quivers
anim.animate(ds, "u", overlay="uv")        # zonal current
anim.animate(ds, "v", overlay="uv")        # meridional current
```

- **SST & wind stress** — the time-evolving counterpart to the static SST +
  wind-stress map in `01_seaforward_postprocess_plot.ipynb`: watch the cold
  tongue, its front and offshore filaments respond to the wind frame by
  frame instead of reading them off a single instant.
- **SSH & currents** — SSH is the pressure field the geostrophic flow
  follows; watching the highs/lows migrate alongside the current vectors is
  the quickest way to see eddies form, drift and decay over the run.
- **Current speed & quivers** — a quiver of current vectors over a
  speed-shaded background, highlighting where the flow is fastest (jets,
  eddy cores) as it evolves.
- **Zonal (u) / meridional (v) current** — isolates each component;
  compare the two to see which dominates the circulation at a given
  time/place.

## Notes

- **DCC linkage (FR-12):** animation is a D1 (downstream/dissemination)
  product — it consumes validated C1 output (ideally already checked by
  `02_validation.ipynb`, DCC process V1) and produces outreach/diagnostic
  material, not a new analysis result in its own right.
- **Runtime:** animating a full-size regional run with many time steps
  takes noticeably longer than a single static plot from
  `01_seaforward_postprocess_plot.ipynb` — each frame is a fresh render.

<div style="display:flex; justify-content:center; margin:10px 0 14px 0;">
   <a href="https://raw.githubusercontent.com/opera-seaforward/seaforward_readthedoc/main/docs/notebooks/06_animation.ipynb" data-download-url="https://raw.githubusercontent.com/opera-seaforward/seaforward_readthedoc/main/docs/notebooks/06_animation.ipynb" data-download-filename="06_animation.ipynb" onmouseover="this.style.transform='scale(1.08)'; this.style.boxShadow='0 10px 24px rgba(0,0,0,0.18)';" onmouseout="this.style.transform='scale(1)'; this.style.boxShadow='none';" style="display:inline-flex; align-items:center; justify-content:center; gap:16px; min-width: 80px; padding:20px 20px; border-radius:10px; background:linear-gradient(to bottom, #ffffcc 0%, #f4f797de 100%); color:#000000; text-decoration:none; font-size:1.2rem; line-height:1.1; text-align:center; transition:transform 0.18s ease, box-shadow 0.18s ease; transform-origin:center;">
      <img src="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/icons/download.svg" alt="" aria-hidden="true" style="width:25px; height:25px; color:#000000; font-weight:bold filter:invert(1);" />
      <span>Download notebook 06_animation.ipynb</span>
   </a>
</div>
