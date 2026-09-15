# Post-processing & Plotting: One Call Per Figure

`sftools.postprocess` (module `pp`) -- sigma-level-to-true-depth conversion,
staggered-grid velocity handling, Hovmoller/profile/section extraction -- and
`sftools.plotting` (module `pl`) -- coastline/land/isobath drawing, colour
scaling, quiver overlays -- are the **two modules** behind every static figure
in this repo:

```
pp.field() / pp.section() / pp.profile() / pp.hovmoller() / pp.timeseries()   <- extract
pp.uv_at_depth() / pp.speed_map() / pp.vorticity()                            <- derive dynamics from u/v
pl.plot() / pl.plot_eddy()                                                    <- draw one figure, one call
```

`01_postprocessing.ipynb` is the **D1** (downstream applications) notebook:
it takes CROCO output that **C1** already produced and turns it into the
static figures a downstream user actually looks at, using `sftools` only
where it encodes something CROCO-specific -- everything past that is a
single `pl.plot(...)` call per figure. It does not validate the run itself;
that's **V1** (`02_validation.ipynb`/`03_composite_validation.ipynb`),
which sits between C1 and D1 in the value chain for exactly that reason --
see "Validation: One Engine, Two Ways To Run It".

Because every figure in the notebook goes through the same two modules, a
map, a section and a time series of the same variable can't silently use
different depth-interpolation or grid-rotation logic from each other.

## Section map

The notebook's actual section numbering:

| Section | What it does |
| --- | --- |
| 0 | Find and select a cycle -- same `YYYYMMDD` discovery pattern as `02_validation.ipynb` Section 1, `RUN_TYPE` picks `fcst` vs `hcast` |
| Open data | `pp.open_history()` -- decodes the time axis with `YORIG`, carries the grid every `pl.plot(..., ds=ds)` call draws from |
| Parameters | The depth/section/profile/isobath settings every figure below reuses -- change once, re-run from there |
| 1 | Surface fields -- temperature, salinity, sea surface height, at `depth` |
| 2 | Dynamics -- current + speed, vorticity, combined eddy view, at `dyn_depth`, all derived from `u`/`v` |
| 3 | Vertical structure -- section and profile (salt, temp, speed, u, v), sigma levels converted to true depth internally |
| 4 | Through time -- Hovmoller diagrams (`time_lat`, `time_depth`) and time series (salt, temp, speed, u, v, SSH) |
| Saving | How to write any figure above to disk |

## Why two depths (`depth` vs `dyn_depth`)

Deliberately kept separate in Parameters: "surface fields" (SST, SSS, SSH)
want the true surface, while "dynamics" (currents, vorticity, eddy view) are
cleanest **below the wind-driven Ekman layer**, where the mesoscale signal
isn't swamped by wind-driven transport. `depth=None` gives the top sigma
level for the surface-fields section; a number gives that true depth in
metres, interpolated, blank where the sea floor is shallower than requested.

## 1. Surface fields

Temperature and salinity both go through `pp.field(ds, var, depth_m=depth,
tindex=tindex)` -> `pl.plot(..., ds=ds, isobaths=isobaths)`. SSH doesn't --
`zeta` is already 2D (elevation about the model's own reference level, not
an anomaly about zero, so it sits at whatever range it actually occupies),
so no depth selection applies; `cmap="Spectral_r"` is the diverging-but-off-
centre convention used for SSH throughout the toolkit.

## 2. Dynamics

`pp.uv_at_depth(ds, depth_m=dyn_depth, rotate=True)` does three things in
one call: interpolates each velocity column from sigma levels to
`dyn_depth`, averages `u`/`v` off CROCO's staggered Arakawa C-grid onto the
rho points, and rotates the grid-aligned components to true east/north.
`pp.speed_map()` plus that `(u, v)` pair, passed as `pl.plot(..., uv=(u,
v))`, draws speed-shaded quivers. `pp.vorticity(ds, depth_m=dyn_depth,
normalized=True)` computes relative vorticity over *f* using the grid
metrics `pm`/`pn` (1/dx, 1/dy) rather than a grid-metric-blind
`np.gradient` -- CROCO's cells aren't square.

`pl.plot_eddy(pp.field(ds, "temp", depth_m=dyn_depth), ds=ds,
overlay=(...))` is the combined view: the same temperature field at
`dyn_depth`, overlaid with either `("uv", (u, v))` (current vectors) or
`("vort", vort_da)` (vorticity contours) -- the most informative single
figure in the notebook, since it shows the water and what's moving it
together.

## 3. Vertical structure

`pp.section(ds, var, lon0, lon1, lat0, lat1)` and `pp.profile(ds, var,
plon, plat, tindex=tindex)` both convert CROCO's terrain-following sigma
levels to true depths internally, using the file's own
`Vtransform`/`hc`/`theta_s`/`theta_b` stretching parameters -- no separate
depth-conversion step needed. Section: a transect between two points, for
salt/temp/speed/u/v. Profile: one column, surface to sea floor, at a
single `(plon, plat)` point.

## 4. Through time

Two different collapses of `pp.hovmoller(ds, var, kind=...)`:
`kind="time_lat"` collapses longitude at a fixed `lon0`, so propagating
features (eddies, waves, fronts) appear as bands that *tilt* -- the slope
is their speed. `kind="time_depth"` instead collapses the water column at
one `(lon0, lat0)` point, showing stratification building or breaking down
and the mixed layer deepening.

`pp.timeseries(ds, var, lon0=plon, lat0=plat, depth_m=...)` follows one
point through the run -- where diurnal cycles, transient events and drift
show up. The surface carries the diurnal cycle and the atmosphere's
imprint directly; a point at depth usually doesn't, which is why
temperature/salinity are shown both at the surface and at `depth_m=50`.

## Saving a figure

Every figure in the notebook is a plain matplotlib figure -- add as the
last line of the cell that plots it:

```python
fig.savefig("/directory/name.png", dpi=250, bbox_inches="tight")
```

<div style="display:flex; justify-content:center; margin:10px 0 14px 0;">
   <a href="https://raw.githubusercontent.com/opera-seaforward/seaforward_readthedoc/main/docs/notebooks/01_postprocessing.ipynb" data-download-url="https://raw.githubusercontent.com/opera-seaforward/seaforward_readthedoc/main/docs/notebooks/01_postprocessing.ipynb" data-download-filename="01_postprocessing.ipynb" onmouseover="this.style.transform='scale(1.08)'; this.style.boxShadow='0 10px 24px rgba(0,0,0,0.18)';" onmouseout="this.style.transform='scale(1)'; this.style.boxShadow='none';" style="display:inline-flex; align-items:center; justify-content:center; gap:16px; min-width: 80px; padding:20px 20px; border-radius:10px; background:linear-gradient(to bottom, #ffffcc 0%, #f4f797de 100%); color:#000000; text-decoration:none; font-size:1.2rem; line-height:1.1; text-align:center; transition:transform 0.18s ease, box-shadow 0.18s ease; transform-origin:center;">
      <img src="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/icons/download.svg" alt="" aria-hidden="true" style="width:25px; height:25px; color:#000000; font-weight:bold filter:invert(1);" />
      <span>Download notebook 01_postprocessing.ipynb</span>
   </a>
</div>
