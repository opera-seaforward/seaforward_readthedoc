# Phase 6 — Region Gallery

This is a **reference gallery**, not a tutorial. Each card is a worked region built
with the Phase 2 recipe — a compact "what does this domain look like, and how was it
set up" reference you can scan when building your own. The *method* for every region
is the same (see **[Phase 2](../phase2/02_forecast_config.md)**); only the numbers
change.

!!! note
    **How to build a new region.** Follow Phase 2. The only per-region decisions are the **box** (lon/lat extent), the **resolution**, which **boundaries** are open or closed — read from the mask, where an edge is open if it's mostly ocean and closed if it's mostly coast — and a couple of flags: `FIX_GFS_LON` is 0 in the eastern hemisphere, 1 in the western. Everything else — the vertical grid, the config-file structure, the compile — is identical. Each card records exactly those per-region choices, so you can build a similar domain by analogy.

Every card shows the region **portrait** — grid mesh and bathymetry, from
`sftools.plotting.grid_bathy_map` — and, where a forecast has run, a **result** panel
so you can see the region in action.

### Generating a region portrait

Run this from `~/seaforward`, so `sftools` imports, pointing at the region's
`croco_grd.nc`:

```python
import sftools.plotting as pl

pl.grid_bathy_map(
    "forecast/scratch/IGOG_12/CROCO_FILES/croco_grd.nc",
    title="Gulf of Guinea — IGOG 1/12",
    coastline=True,        # real coastline via cartopy; falls back to the land mask
    mesh_stride=2,         # draw every 2nd grid line, to thin a dense mesh
    out="docs/img/igog_12_portrait.png",
)
```

- **Left panel** — the grid mesh over the coastline, drawn on **ocean cells only**, so
  the mesh stops at the coast rather than covering the land in grid lines.
- **Right panel** — smoothed bathymetry (`h`) on a shelf-friendly stepped scale:
  0, 20, 50, 100, 200, 300, 500, 1000, 2000, 3000 m.
- `mesh_stride=N` thins the mesh — 2 or 3 for fine grids, so the lines stay legible.
- `out=` saves a PNG; omit it to get the figure object back.

### Adding a result panel

Once a forecast exists, one more call gives the "region in action" figure:

```python
import sftools.postprocess as pp, sftools.plotting as pl

ds = pp.open_history(
    "forecast/model-runs/IGOG_12/<DATE>/fcst/CROCO_FILES/croco_his.nc", Yorig=2000)

pl.plot(pp.field(ds, "temp"), out="docs/img/igog_12_sst.png")                # surface
pl.plot(pp.field(ds, "temp", depth_m=100), out="docs/img/igog_12_t100.png")  # at 100 m
```

`pp.field()` gives the surface by default and a true depth in metres when you pass
`depth_m`, with blanks where the sea floor is shallower than you asked for. The full
set of options — colour limits, isobath overlays, current vectors — is in
[Surface fields](../phase5/surface.md).

Drop the PNGs into `docs/img/` with the names the cards reference —
`<config>_portrait.png` and `<config>_sst.png` — and they render in the gallery.