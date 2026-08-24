The validation module compares a CROCO run against the **parent** product it was
downscaled from — GLORYS for hindcasts, Mercator for forecasts. The comparison
is done **on the CROCO grid**: the parent is regridded onto CROCO's curvilinear
grid, so every CROCO point has a matching parent value and the fine grid is the
reference.

### Parent variable mapping

The parent (CMEMS: GLORYS / Mercator) uses these names, mapped internally:

| SEA-FORWARD | CMEMS |
| --- | --- |
| `temp` | `thetao` |
| `ssh` | `zos` |
| `salt` | `so` |
| `u` | `uo` |
| `v` | `vo` |

Coordinates are `longitude`, `latitude`, `depth`, `time`.

### Snapshot maps: CROCO vs parent

Three-panel figures (CROCO | parent | difference) plus statistics. `date` selects the parent field **and** the matching CROCO record, so both sides are on the same day.

```python
val.compare_sst(F, MERC, date="2026-07-11", Yorig=2000)
val.compare_ssh(F, MERC, date="2026-07-11", Yorig=2000)
val.compare_currents(F, MERC, date="2026-07-11", Yorig=2000)
```

Each returns `(figure, stats)` where `stats` is a dict with `bias`, `rmse`,
`crmse` (centred RMSE), `corr`, the domain means and extremes, and `n`.

**Optional keywords (most compare functions):**

- `depth_m=50` — compare at a true depth instead of the surface (temperature and
  currents; SSH is 2-D). CROCO is interpolated from sigma; the parent is taken
  at its nearest depth level.
- `daily_mean=True` — average CROCO's sub-daily records for the day before
  comparing, matching the parent's daily averaging (see the note on the diurnal
  cycle below).
- `margin_deg=0.5` — trim the sponge band from both sides for honest interior
  statistics.

```python
val.compare_sst(F, MERC, date="2026-07-11", Yorig=2000,
                depth_m=50, daily_mean=True, margin_deg=0.5)
```

### SST with wind

The upwelling diagnostic — SST shaded with the 10 m wind (from GFS/GFS
`for_croco` files) on top:

```python
val.sst_with_wind(F, GFS_dir="forecast/scratch/Canary_12/downloaded_data/GFS/for_croco",
                  date="2026-07-11")
```

### Profiles, sections and time series vs the parent

Overlay CROCO and the parent on one plot:

```python
# vertical profile at a point (two lines vs depth)
val.compare_profile(F, MERC, "temp", -19, 21, date="2026-07-11", Yorig=2000)

# side-by-side vertical sections (CROCO | parent, shared colour scale)
val.compare_section(F, MERC, "temp", -21, 21, -16, 21, date="2026-07-11", Yorig=2000)

# time series at a point (surface or depth)
val.compare_timeseries(F, MERC, "temp", -19, 21, Yorig=2000)
val.compare_timeseries(F, MERC, "temp", -19, 21, Yorig=2000, depth_m=50)
```

These use the parent's 3-D fields, so the profiles and sections span the whole
water column.

### Error growth along a cycle

SEA-FORWARD runs in 5-day cycles. `cycle_error_growth` tracks the CROCO-vs-parent
statistics **as a function of lead time** — how the run drifts from the parent
over its 5 days:

```python
g = val.cycle_error_growth(H, G, fields=("sst", "ssh", "speed"),
                           Yorig=1993, daily_mean=True)
val.plot_error_growth(g, metric="rmse")     # or "bias", "crmse", "corr"
```

`combined_error_growth` overlays all cycles of a run (one line per cycle plus the
mean), one subplot per field:

```python
def parent_for(tag):
    # cross-year cycles need the right GLORYS month per cycle
    if tag.startswith("202601"):
        return "hindcast/scratch/Canary_12/downloaded_data/GLORYS/2026_01.nc"
    return "hindcast/scratch/Canary_12/downloaded_data/GLORYS/2025_12.nc"

val.combined_error_growth("hindcast/model-runs/Canary_12", parent_for,
                          phase="hcast", fields=("sst", "ssh", "speed"),
                          metric="rmse", Yorig=1993, daily_mean=True)
```

`parent_for` is a function returning the correct parent file for each cycle. A
cycle that crosses the year boundary (e.g. Dec 30 → Jan 4) spans two GLORYS
monthly files; give it the file covering most of its days, or provide both.

Error growth also takes `depth_m=` to track the drift at a chosen depth.

### Error vs depth

Sweep several depths and plot the CROCO-vs-parent error against depth:

```python
fig, stats = val.error_vs_depth(H, G, field="speed",
                                depths=(0, 50, 100, 200, 500),
                                Yorig=1993, metric="rmse")
```

The error is typically largest at the surface (wind-driven Ekman currents and
surface-intensified eddies, where the high-resolution model adds the most) and
decreases with depth (slow, smooth, large-scale geostrophic flow, where CROCO
tracks the parent closely).

### Statistics helper

```python
val.domain_statistics(model_2d, ref_2d)   # bias, rmse, crmse, corr, means, extremes
```

### Comparing two CROCO runs (resolution / nesting)

Everything above compares CROCO against a **Mercator/GLORYS parent** (validation).
A different question is: how does a *finer* CROCO run compare to a *coarser* one —
e.g. a 1/25° nested child vs its 1/12° parent (Phase 6)? For that, both inputs are
**CROCO** files, so the parent-name mapping above doesn't apply. Use the dedicated
`compare_*_resolution` helpers, which read **both** files as CROCO:

```python
CHILD  = ".../Canary_25/CROCO_FILES/croco_his.nc"   # fine  (1/25°)
PARENT = ".../Canary_12/.../croco_his.nc"           # coarse (1/12°)

# side-by-side maps, shared colour scale (their own grids, not a cell-by-cell diff)
val.compare_resolution(CHILD, PARENT, var="temp",   Yorig=2000)   # SST
val.compare_resolution(CHILD, PARENT, var="vort_f", Yorig=2000)   # vorticity/f — eddies
val.compare_resolution(CHILD, PARENT, var="speed",  Yorig=2000)   # surface currents

# add a real coastline + gridlines (needs cartopy; falls back to the land mask)
val.compare_resolution(CHILD, PARENT, var="temp", Yorig=2000, coastline=True)

# add a third "difference" panel: child − (parent regridded onto the child grid),
# i.e. what the finer run ADDS relative to the coarser one (needs scipy)
val.compare_resolution(CHILD, PARENT, var="temp", Yorig=2000, diff=True)

# vertical profile / section between two CROCO runs
val.compare_profile_resolution(CHILD, PARENT, "temp", -19, 21, Yorig=2000)
val.compare_section_resolution(CHILD, PARENT, "speed", -21,21, -17,22.5, Yorig=2000)
```

!!! important
    **`_resolution` vs plain `compare_`.** The plain `compare_sst`/`compare_currents` `compare_profile`/`compare_section` expect the second argument to be a **Mercator-format** file (`thetao/so/uo/vo`, a `depth` axis). If you pass a CROCO `croco_his.nc` there you get `KeyError: 'thetao' not in ...`. For **two CROCO runs** (nesting) use the `_resolution` variants, which take `tindex` (a record number, default `-1`), **not** `date`, and `Yorig` matching the runs' track (forecast = 2000).

- **Why side-by-side, not a raw difference, by default.** The child and parent are on **different grids** (150×238 vs 81×123), so subtracting them cell-by-cell is undefined — the same array index is a different location on each grid. `diff=True` handles this by first interpolating the parent onto the child grid, *then* differencing; the result shows, at full child resolution, where the fine dynamics push the solution away from the smooth parent (sharp red/blue dipoles at the fronts
and eddies the child resolves, near-zero in the smooth interior).

- **What a good resolution comparison looks like** (see also Phase 6): the child and parent share the **same large-scale pattern** (the nesting is consistent), but the child **resolves finer structure** the parent smooths — sharper SST fronts, tighter jets, and especially in `vort_f`, smaller and more numerous eddies and thin filaments. That extra structure *is* the value the finer grid adds.