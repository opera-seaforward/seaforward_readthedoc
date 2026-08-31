![build progress](../img/model_grid.png)

*Step 2 builds the **model grid** from bathymetry (ETOPO2) and coastline (GSHHS).*

```bash
cd ${CROCO_PYTOOLS_DIR}/prepro
python3 make_grid.py ${CONFIG_DIR}/grid.ini 2>&1 | tail -20
```

**What this does:** reads the sea-floor depth data (ETOPO2), works out which grid
points are land vs ocean (the "mask") from the coastline, and smooths the
bathymetry so the model stays stable. The scrolling `rx0`/`ry0` numbers are the
smoothing working; they settle near `0.20`. It finishes with
`Writing .../CROCO_FILES/croco_grd.nc done`.

<figure style="text-align: center; margin: 20px 0;">
  <img src="../../img/bathymetry_U1.png" alt="Workflow for building the model grid" style="max-width: 100%; height: auto;">
  <figcaption style="font-size: 1em; color: #555; margin-top: 8px; font-style: italic;">
    Building <code>model_grid.nc</code>: your domain limits and grid spacing pass through <code>grid.ini</code> to the CROCO pytools, which combine them with the GSHHS coastline and ETOPO2 bathymetry. The result feeds every later step (U2–U5, C1, V1, D1).
  </figcaption>
</figure>

Now read the **real** grid dimensions from the file it produced:

```bash
ncdump -h ${CF}/croco_grd.nc | grep -E "xi_rho|eta_rho"
```

!!! check
    For Canary_12: `xi_rho = 81`, `eta_rho = 123`.

**Write these two numbers down.** You'll need them (minus 2) for `param.h` later:

- `LLm0 = xi_rho − 2 = 79`
- `MMm0 = eta_rho − 2 = 121`

!!! warning
    **Use the numbers from the file, not the estimate.** The estimate said 79×121; the real grid is 81×123. The `− 2` removes two boundary rows CROCO adds internally.

### Look at what you built

```python
import sftools.plotting as pl

pl.grid_bathy_map(
    "forecast/scratch/Canary_12/CROCO_FILES/croco_grd.nc",
    title="Canary — Canary_12 (1/12)",
    coastline=True,
    mesh_stride=2,
    out="docs/img/canary_12_portrait.png",
)
```

![Canary_12 grid and bathymetry](../img/canary_12_portrait.png)

The left panel is the grid mesh, drawn over ocean cells only — the lines stop at
the coast, so the mesh shows the computational domain. The right panel is the
smoothed bathymetry the model will use. Check the shelf break looks continuous and
that nothing is obviously wrong before you build data on top of this grid.

`mesh_stride=2` draws every second grid line, which keeps a dense mesh legible;
run it from `~/seaforward` so `sftools` imports.