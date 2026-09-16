# 06 — Animation (DCC process D1, dissemination/outreach)

**SEA-FORWARD** OceanPrediction-A toolkit

Time-evolving companion to `01_postprocessing.ipynb`'s static maps: five
animations over a CROCO run, all built on a single entry point,
`sftools.animation.animate(ds, var, overlay=...)`.

| Section | Animation | Call |
| --- | --- | --- |
| 1 | Load CROCO data |  `pp.open_history(H, Yorig=YORIG)` |
| 2 | Sea Surface Temperature & wind stress | `anim.animate(ds, "temp", depth_m=depth, overlay="wind", vmin=22, vmax=29)` |
| 3 | Sea Surface Height & surface currents | `anim.animate(ds, "zeta", overlay="uv", cmap="Spectral_r")` |
| 4 | Current speed & quivers | `anim.animate(ds, "speed", depth_m=depth, overlay="uv")` |
| 5 | Zonal current (u) | `anim.animate(ds, "u", overlay="uv")` |
| 6 | Meridional current (v) | `anim.animate(ds, "v", overlay="uv")` |

## 0. Find and select a cycle

Same discovery pattern as `02_validation.ipynb` Section 1 and
`01_postprocessing.ipynb` Section 0: every run lives in a cycle directory
named `YYYYMMDD`, sibling to every other cycle under
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

## `anim.animate()` reference

``` { .text .no-copy }
anim.animate(ds, var, depth_m=None, overlay=None, uv_depth=None, isobaths=None,
            tindex_range=None, skip=4, scale=None, interval=300, figsize=(8, 7),
            cmap=None, vmin=None, vmax=None, out=None, fps=4, dpi=110)
```

Animate a 2D field through the run.

| Parameter | Meaning |
| --- | --- |
| `ds` | CROCO output opened with `pp.open_history()` or `pp.open_run()` |
| `var` | `'temp'`, `'salt'`, `'zeta'`, `'speed'`, `'u'`, `'v'`, ... |
| `overlay` | `'wind'`/`'sustr'` — surface wind-stress vectors, from the model's own `sustr`/`svstr` (N/m², **not** 10 m wind speed); `'uv'`/`'current'` — surface current vectors; `None` — no overlay |
| `isobaths` | Depths (m) to contour, e.g. `[200, 1000]` |
| `tindex_range` | `(start, end)` time-index range; default every record |
| `skip` | Vector subsampling stride (default 4) |
| `scale` | Quiver scale — smaller values give longer arrows |
| `interval` | Frame delay in ms, for the inline widget |
| `figsize` | Figure size in inches |
| `cmap`, `vmin`, `vmax` | Colour overrides. Limits are resolved **once** across the whole series, so the scale doesn't flicker between frames |
| `out` | Write to this path instead of returning a widget — `.gif` uses the pillow writer, anything else uses ffmpeg |
| `fps` | Frames per second when writing a file |
| `dpi` | Resolution when writing a file |

## Parameters

New in this revision, a small parameters cell before the animations
(previously each call used every default):

```python
depth = None   # depth_m passed to the temp/speed animations below; None = surface
dpi   = 300    # only used if/when you uncomment a save-to-file line
```

## Output directory

New in this revision — a cycle-specific folder for any animation you
choose to save to disk:

```python
out_dir = os.path.join(MAIN_DIR, CONFIG, f"animation_{CYCLE}")
os.makedirs(out_dir, exist_ok=True)
```

## 2–6. The five animations

Each cell now also carries a commented-out "save to file" line, disabled
by default — the animation plays inline in the notebook as before, and
saving is opt-in:

# SST & wind stress 
The time-evolving counterpart to the static SST +
  wind-stress map in `01_postprocessing.ipynb`: watch the cold tongue, its
  front and offshore filaments respond to the wind frame by frame instead
  of reading them off a single instant. `vmin=22, vmax=29` fixes the
  colour scale to this specific run's range rather than the default
  once-across-the-series auto-scaling.
```python
anim.animate(ds, "temp", depth_m=depth, overlay="wind", vmin=22, vmax=29)
#### to save animation
# z = [0 if depth is None else depth]
# anim.animate(ds, "temp", depth_m=depth, overlay="wind",
#              out=f"{out_dir}/temp_animation_{z[0]}m_cycle-{CYCLE}.gif")
```

# SSH & currents
SSH is the pressure field the geostrophic flow
  follows; watching the highs/lows migrate alongside the current vectors is
  the quickest way to see eddies form, drift and decay over the run.
  `cmap="Spectral_r"` matches the diverging-but-off-centre SSH convention
  used throughout the toolkit (see `01_postprocessing.ipynb`'s Surface
  Fields section).
```python
anim.animate(ds, "zeta", overlay="uv", cmap="Spectral_r")
#### to save animation
# anim.animate(ds, "zeta", overlay="uv", out=f"{out_dir}/SSH_animation_cycle-{CYCLE}.gif")
```
# Current speed & quivers
A quiver of current vectors over a speed-shaded background, highlighting where the flow is fastest (jets, eddy cores) as it evolves
```python
anim.animate(ds, "speed", depth_m=depth, overlay="uv")
#### to save animation
# z = [0 if depth is None else depth]
# anim.animate(ds, "speed", depth_m=depth, overlay="uv",
#              out=f"{out_dir}/speed_animation_{z[0]}m_cycle-{CYCLE}.gif")
```

# Zonal (u) / meridional (v) current 
Isolates each component; compare the two to see which dominates the circulation at a given time/place.

**u**
```python
anim.animate(ds, "u", depth_m=depth, overlay="uv")
#### to save animation
# z = [0 if depth is None else depth]
# anim.animate(ds, "u", depth_m=depth, overlay="uv",
#              out=f"{out_dir}/u_animation_{z[0]}m_cycle-{CYCLE}.gif")
```
**v**
```python
anim.animate(ds, "v", depth_m=depth, overlay="uv")
#### to save animation  -- see warning below, this line is currently broken
# z = [0 if depth is None else depth]
# anim.animate(ds, "v", depth_m=depth, overlay="uv",
#      out=f"{out_dir}/v_animation_{z[0]}m_cycle-{CYCLE}.gif")
```

## Notes

- **DCC linkage (FR-12):** animation is a D1 (downstream/dissemination)
  product — it consumes validated C1 output (ideally already checked by
  `02_validation.ipynb`, DCC process V1) and produces outreach/diagnostic
  material, not a new analysis result in its own right. See
  [sea-forward.readthedocs.io](https://sea-forward.readthedocs.io/en/latest/)
  for the full Upstream -> C1 -> V1 -> D1 value chain this notebook sits at
  the end of.
- **Runtime:** animating a full-size regional run with many time steps
  takes noticeably longer than a single static plot from
  `01_postprocessing.ipynb` — each frame is a fresh render.

<div style="display:flex; justify-content:center; margin:10px 0 14px 0;">
   <a href="https://raw.githubusercontent.com/opera-seaforward/seaforward_readthedoc/main/docs/notebooks/06_animation.ipynb" data-download-url="https://raw.githubusercontent.com/opera-seaforward/seaforward_readthedoc/main/docs/notebooks/06_animation.ipynb" data-download-filename="06_animation.ipynb" onmouseover="this.style.transform='scale(1.08)'; this.style.boxShadow='0 10px 24px rgba(0,0,0,0.18)';" onmouseout="this.style.transform='scale(1)'; this.style.boxShadow='none';" style="display:inline-flex; align-items:center; justify-content:center; gap:16px; min-width: 80px; padding:20px 20px; border-radius:10px; background:linear-gradient(to bottom, #ffffcc 0%, #f4f797de 100%); color:#000000; text-decoration:none; font-size:1.2rem; line-height:1.1; text-align:center; transition:transform 0.18s ease, box-shadow 0.18s ease; transform-origin:center;">
      <img src="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/icons/download.svg" alt="" aria-hidden="true" style="width:25px; height:25px; color:#000000; font-weight:bold filter:invert(1);" />
      <span>Download notebook 06_animation.ipynb</span>
   </a>
</div>
