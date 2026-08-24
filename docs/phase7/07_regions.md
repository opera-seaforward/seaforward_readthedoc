# SEA-FORWARD — Region Gallery

This is a **reference gallery**, not a tutorial. Each card is a worked region built
with the Phase 2 recipe — a compact "what does this domain look like and how was it
set up" reference you can scan when building your own. The *method* for every region
is the same (→ **[Phase 2: Building a Forecast Configuration](../phase2/02_forecast_config.md)**);
only the numbers change.

!!! note
    **How to build a new region.** Follow Phase 2. The only per-region decisions are: the **box** (lon/lat extent), the **resolution**, which **boundaries** are open vs closed (read from the mask — an edge is *open* if it's mostly ocean, *closed* if it's mostly coast), and a couple of flags (`FIX_GFS_LON` = 0 in the eastern hemisphere, 1 in the western). Everything else — the vertical grid, the config-file structure, the compile — is identical. Each card below records exactly those per-region choices so you can build a similar domain by analogy.

Every card shows the region **portrait** (grid mesh + bathymetry, from `sftools.plotting.grid_bathy_map`) and, where a forecast has run, a **result** panel (SST or surface currents) so you can see the region in action.

### Generating a region portrait

Every card's grid+bathymetry figure comes from one call. Run it from `~/seaforward`
(so `sftools` imports), pointing at the region's `croco_grd.nc`:

```python
import sftools.plotting as pl

pl.grid_bathy_map(
    "forecast/scratch/IGOG_12/CROCO_FILES/croco_grd.nc",
    title="Gulf of Guinea — IGOG 1/12",
    coastline=True,        # real coastline + gridlines (needs cartopy; falls back to the land mask)
    mesh_stride=2,         # draw every 2nd grid line (thins a dense mesh)
    out="docs/img/igog_12_portrait.png",
)
```

- **Left panel** = the model grid mesh over the coastline, drawn over **ocean cells
  only** (the mesh stops at the coast, so land isn't covered in grid lines).
- **Right panel** = smoothed bathymetry (`h`) on a shelf-friendly stepped scale
  (0/20/50/100/200/300/500/1000/2000/3000 m).
- `coastline=True` overlays a real coastline via cartopy if available; otherwise the
  land mask shows the coast.
- `mesh_stride=N` thins the mesh (use 2–3 for fine grids so the lines stay legible);
  `out=` saves a PNG (omit to get the figure object back).

To add a **result** panel once a forecast exists (the "region in action" figure):

```python
import sftools.postprocess as pp, sftools.plotting as pl
# open the history file first (field_map takes a dataset, not a path)
ds  = pp.open_history(
    "forecast/model-runs/IGOG_12/<DATE>/fcst/CROCO_FILES/croco_his.nc", Yorig=2000)

# --- surface field (σ-level index; level=-1 = surface) ---
sst = pp.field_map(ds, var="temp", tindex=-1, level=-1)
pl.plot_map(sst, cmap="RdYlBu_r", out="docs/img/igog_12_sst.png")

# --- OR a field at a true DEPTH in metres (e.g. temperature at 100 m) ---
t100 = pp.field_at_depth(ds, var="temp", depth_m=100, tindex=-1)
pl.plot_map(t100, cmap="RdYlBu_r", out="docs/img/igog_12_t100.png")
```

!!! important
    **Surface vs depth.** `field_map` slices at a **σ-level** (`level=-1` is the surface layer, ≈ 0 m). `field_at_depth` interpolates to a **true depth in metres** — points where the seafloor is shallower than `depth_m` return NaN (blank), which is the physically correct "no water at this depth here". Use `field_map(level=-1)` for a surface SST card, `field_at_depth` for a subsurface view.

Drop the PNGs into `docs/img/` with the names the cards reference (`<config>_portrait.png`, `<config>_sst.png`) and they render in the gallery.
