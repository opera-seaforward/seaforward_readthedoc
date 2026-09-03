### 2a — Why this doesn't use the tool you already know

Phase 2 built Canary_12's grid with `make_grid.py` and a `grid.ini`. That script
**cannot build a zoom grid** — it has no notion of a parent. The AGRIF logic lives in
a Python class, `CROCO`, in `code/croco_pytools/prepro/Modules/croco_class.py`, and
the only thing shipped that drives it is a Jupyter notebook,
`nb_make_grid_zoom.ipynb`.

Most of that notebook is `edit_section_widget(...)` calls — interactive widgets for
editing config values by clicking. The actual work is four method calls:

```python
croco = CROCO("some_zoom.ini")   # read the config
croco.create_grid()              # build the child's lon/lat as a 3x refinement
croco.create_mask_and_topo()     # interpolate bathymetry, build the mask, merge edges
croco.save_grid_nc()             # write croco_grd.nc.1 + AGRIF_FixedGrids.in
```

The widgets exist only to write values into the `.ini`. Write the `.ini` yourself and
you don't need Jupyter — you can call those four methods from an ordinary script,
which is what this step does.

### 2b — Set up the working directory

Don't build the AGRIF child inside `scratch/Canary_12/`. That directory holds a
working, compiled forecast configuration; the AGRIF setup needs parent and child files
side by side and will clutter it. Make a separate one:

```bash
mkdir -p ~/seaforward/forecast/scratch/Canary_AGRIF/CROCO_FILES
# the child grid is built FROM the parent, so the parent must be there first
cp ~/seaforward/forecast/scratch/Canary_12/CROCO_FILES/croco_grd.nc \
   ~/seaforward/forecast/scratch/Canary_AGRIF/CROCO_FILES/croco_grd.nc
ls -la ~/seaforward/forecast/scratch/Canary_AGRIF/CROCO_FILES/
```

That's a **copy**, deliberately. The zoom config points at it as `parent_grid`, and
the child gets written beside it as `croco_grd.nc.1`. Both grids end up in one place,
which is what the model needs at run time.

### 2c — Write the zoom config

The config goes in the **prepro directory**, because that's where you'll run the
script from:

```bash
nano ~/seaforward/code/croco_pytools/prepro/canary_zoom_agrif.ini
```

Substitute your own username, and your `imin/imax/jmin/jmax` from Step 1:

```ini
[Croco_Files]
croco_files_dir = /home/you/seaforward/forecast/scratch/Canary_AGRIF/CROCO_FILES
croco_grd_prefix = croco_grd

[Zoom_Options]
is_zoom = True
is_agrif = True
agrif_level = 1
parent_grid = /home/you/seaforward/forecast/scratch/Canary_AGRIF/CROCO_FILES/croco_grd.nc

[Grid_Zoom_Params]
north_obc = True
south_obc = True
west_obc = True
east_obc = False
merging_area = 5

[Grid_Zoom_Agrif]
coef = 3
imin = 12
imax = 74
jmin = 49
jmax = 110

[Grid_Smoothing_Params]
hmin = 50.0
hmax = 6000.0
interp_rad = 2
rfact = 0.2
smooth_meth = lsmooth

[Grid_Isolated_Waterbodies]
mask_isolated_waterbodies = False
main_water_body_x_idx = 20
main_water_body_y_idx = 20

[Grid_Input_Files]
topo_file_reader = etopo2
topo_file = /home/you/seaforward/data/DATASETS_CROCOTOOLS/Topo/etopo2.nc
shp_file = /home/you/seaforward/data/DATASETS_CROCOTOOLS/gshhs/GSHHS_shp/i/GSHHS_i_L1.shp
```

`Ctrl+O` `Enter`, `Ctrl+X`.

The one closed edge comes straight from Step 1's mask check: the child's east boundary
is 0/62 ocean, the African coast, so `east_obc = False` — exactly as the parent's own
east boundary is closed. Set yours from your own check, not from this example.

!!! warning
    **Pasting long heredocs into a terminal is unreliable.** A `cat > file << 'EOF'` block can collide with whatever you paste after it and truncate the file without saying so. Use nano as above, or a Python block. Either way, check the result with `wc -l` and `tail`.

**Section by section:**

| Section | Key | Meaning |
|---|---|---|
| `[Croco_Files]` | `croco_files_dir` | where the child grid gets written |
| | `croco_grd_prefix` | base name; `agrif_level` appends the `.1` |
| `[Zoom_Options]` | `is_zoom` / `is_agrif` | both True — a zoom grid, AGRIF-style |
| | `agrif_level = 1` | first-level child, so it writes `croco_grd.nc.1` |
| | `parent_grid` | must already exist, from 2b |
| `[Grid_Zoom_Params]` | `*_obc` | which edges are open, from your Step 1 mask check |
| | `merging_area = 5` | blend the child's bathymetry into the parent's over 5 child cells at each open edge, so the two agree on depth where they exchange data |
| `[Grid_Zoom_Agrif]` | `coef = 3` | the refinement ratio |
| | `imin/imax/jmin/jmax` | the box, in parent indices, from Step 1 |
| `[Grid_Smoothing_Params]` | `hmin` | minimum depth in metres — shallower cells are raised to this |
| | `hmax` | maximum depth |
| | `rfact` | bathymetry smoothing target; lower is smoother and more stable, but less faithful |
| | `smooth_meth` | the smoothing algorithm |
| `[Grid_Input_Files]` | `topo_file` | the bathymetry dataset |
| | `shp_file` | the coastline shapefile |

**Two things are absent, and both are constraints in disguise:**

- **No `[Sigma_Params]`.** No `N`, no `theta_s`, no `hc`. The child inherits the
  parent's vertical grid, enforced by giving you nowhere to type a different number.
- **No lon/lat.** No `central_lon`, no `size_x_km`. The child's position comes
  entirely from `parent_grid` plus the index box — which is why Step 1 converts your
  lon/lat box to indices.

**Reuse the paths from the parent's config** rather than typing them fresh.
`topo_file` and `shp_file` should be exactly what built the parent:

```bash
grep -iE "shp_file|topo_file|topo_file_reader" ~/seaforward/forecast/configs/Canary_12/grid.ini
```

**Verify the config parses** before running anything:

```bash
cd ~/seaforward/code/croco_pytools/prepro
python3 << 'PYEOF'
import configparser
c = configparser.ConfigParser(); c.read('canary_zoom_agrif.ini')
print('sections:', c.sections())
z = c['Grid_Zoom_Agrif']
print('box: imin=%s imax=%s jmin=%s jmax=%s coef=%s'
      % (z['imin'], z['imax'], z['jmin'], z['jmax'], z['coef']))
print('agrif:', c['Zoom_Options']['is_agrif'], 'level', c['Zoom_Options']['agrif_level'])
PYEOF
```

```text
sections: ['Croco_Files', 'Zoom_Options', 'Grid_Zoom_Params', 'Grid_Zoom_Agrif',
           'Grid_Smoothing_Params', 'Grid_Isolated_Waterbodies', 'Grid_Input_Files']
box: imin=12 imax=74 jmin=49 jmax=110 coef=3
agrif: True level 1
```

Seven sections. Fewer means the file was truncated — rewrite it.

### 2d — Write the build script

Same directory:

```bash
nano ~/seaforward/code/croco_pytools/prepro/build_canary_agrif.py
```

```python
import matplotlib
matplotlib.use("Agg")            # save figures instead of opening a window
import matplotlib.pyplot as plt
from Modules.croco_class import CROCO

INI = "canary_zoom_agrif.ini"

print(f"=== loading {INI}")
croco = CROCO(INI)

# 1. the child's lon/lat, as a 3x refinement of the parent's index box
print("=== create_grid()")
croco.create_grid()
croco.plot_grid_outline_zoom()
plt.savefig("/tmp/can_outline.png", dpi=110, bbox_inches="tight")
plt.close("all")

# 2. bathymetry + land mask, merged into the parent at the open edges
print("=== create_mask_and_topo()")
croco.create_mask_and_topo()
croco.plot_h_zoom()
plt.savefig("/tmp/can_bathy.png", dpi=110, bbox_inches="tight")
plt.close("all")

# 3. write croco_grd.nc.1 + AGRIF_FixedGrids.in
print("=== save_grid_nc()")
croco.save_grid_nc()

print("\nDONE — check /tmp/can_outline.png and /tmp/can_bathy.png")
```

`Ctrl+O` `Enter`, `Ctrl+X`.

Three things in that script are load-bearing:

1. **`matplotlib.use("Agg")` must come before `import matplotlib.pyplot`.** The
   notebook uses `%matplotlib widget`, which needs a browser. A script has no display,
   so plotting would fail; `Agg` renders to a file instead. The order matters — set
   the backend before pyplot is imported.
2. **`from Modules.croco_class import CROCO`** is a relative package import. It
   resolves only if your working directory is `prepro/`. Anywhere else gives
   `ModuleNotFoundError: No module named 'Modules'`.
3. **The plot calls** are your only check that the child landed where you intended,
   before you spend time on initial conditions and compiling.

### 2e — Run it

Two requirements: the right directory, and the right conda environment.

```bash
cd ~/seaforward/code/croco_pytools/prepro     # required for the Modules import
conda activate seaforward                     # the env that built the parent's grid
python build_canary_agrif.py 2>&1 | tail -20
```

```text
=== loading canary_zoom_agrif.ini
=== create_grid()
Reading CROCO grid: .../Canary_AGRIF/CROCO_FILES/croco_grd.nc
=== create_mask_and_topo()
Reading topography file: .../DATASETS_CROCOTOOLS/Topo/etopo2.nc
Bounding indices of the relevant part to be extracted from the entire dataset:
 imin,imax = 4763 4928 out of 10800 jmin,jmax = 3236 3397 out of 5400
Interpolating topography to CROCO grid
Finished interpolating
Matching Parent and Child mask close to boundary
Processing mask to close narrow bay and narrow land (1 point wide)
=== save_grid_nc()
Writting .../Canary_AGRIF/CROCO_FILES/croco_grd.nc.1 done
Create an AGRIF_FixedGrids.in file
DONE — check /tmp/can_outline.png and /tmp/can_bathy.png
```

Two lines there are AGRIF-specific:

- **`Matching Parent and Child mask close to boundary`** — the `merging_area` at work,
  reconciling the two grids' land and sea at the interface.
- **`Create an AGRIF_FixedGrids.in file`** — the tool writes this for you. You do not
  hand-author it.

### 2f — What you should now have

```bash
ls -la ~/seaforward/forecast/scratch/Canary_AGRIF/CROCO_FILES/
```

```text
AGRIF_FixedGrids.in    <- the child-in-parent definition
croco_grd.nc           <- the parent (you copied it)
croco_grd.nc.1         <- the child grid
```

Note the naming: **`croco_grd.nc.1`**, the `.1` from `agrif_level = 1`. This is
CROCO's AGRIF convention and it carries through everything — `croco_ini.nc.1`,
`croco.in.1`, `croco_his.nc.1`. It is not `1_croco_grd.nc`.

Look at `/tmp/can_outline.png` and `/tmp/can_bathy.png` before going further. They are
your check that the box landed where you meant it to.

### `AGRIF_FixedGrids.in`

```bash
cat ~/seaforward/forecast/scratch/Canary_AGRIF/CROCO_FILES/AGRIF_FixedGrids.in
```

```text
    1
    13    75    50    111    3    3    3    3
    0
# number of children per parent
# imin imax jmin jmax spacerefx spacerefy timerefx timerefy
# [all coordinates are relative to each parent grid!]
```

One child, refined 3× in space and taking 3 sub-steps per parent step. The format
supports several children off one parent — more rows, each with its own box and ratio.

Compare against what was requested — `12 74 49 110`. Every index is exactly one
higher, which is the Fortran 1-based offset and nothing more. **The box was not
moved.**

### The displacement loop

`easygrid.py` sometimes moves your box, and says so only in passing:

```text
==> North limits displacement +1
```

The rule (`Modules/easygrid.py`, around line 490) compares the outermost two rows or
columns of the child's mask:

```python
northchk = abs(maskr_coarse[-2, :] - maskr_coarse[-1, :])
if sum(northchk) != 0:
    inputs.jmax = inputs.jmax + 1
    print("==> North limits displacement +1")
```

If a coastline crosses near the edge, it shifts that edge outward and retries, looking
for one whose mask is uniform in the boundary-normal direction. It can march several
cells before it settles.

**It didn't fire here**, and the reason is worth understanding: the Canary coast runs
roughly north–south, *parallel* to the child's east edge, and that edge is already
uniformly land. The north and south edges each carry land only at their eastern end,
contiguous rather than crossing. There was nothing for the loop to hunt.

A coast running *diagonally* across an edge the tool is trying to open is what makes
it march — and it does not check whether the destination makes sense. A solid-land
edge is perfectly uniform, so it passes the test whether or not you meant that edge to
be open. Setting `north_obc = False` does not stop it either: the loop runs on mask
geometry, before the obc flags are considered.

Always compare what you asked for against what `AGRIF_FixedGrids.in` says.

### Verify the child grid

```bash
cd ~/seaforward/forecast/scratch/Canary_AGRIF/CROCO_FILES
python3 << 'PYEOF'
import xarray as xr, numpy as np
g = xr.open_dataset('croco_grd.nc.1')
print('grid: %d x %d' % (g.sizes['xi_rho'], g.sizes['eta_rho']))
print('lon: %.2f to %.2f E'   % (float(g.lon_rho.min()), float(g.lon_rho.max())))
print('lat: %.2f to %.2f N'   % (float(g.lat_rho.min()), float(g.lat_rho.max())))
print('depth: %.0f to %.0f m' % (float(g.h.min()), float(g.h.max())))
print('ocean: %.1f%%'         % (float(g.mask_rho.mean()) * 100))
dx = 1 / g.pm.values          # pm, pn are INVERSE grid spacings
print('dx: %.2f - %.2f km' % (dx.min()/1000, dx.max()/1000))
m = g.mask_rho.values
for n, r in [('south', m[0,:]), ('north', m[-1,:]), ('west', m[:,0]), ('east', m[:,-1])]:
    print('  %-6s %4d/%4d ocean' % (n, int(r.sum()), len(r)))
PYEOF
```

```text
grid: 188 x 185
lon: -21.09 to -15.82 E
lat: 18.02 to 23.10 N
depth: 48 to 4355 m
ocean: 88.1%
dx: 2.88 - 2.88 km
  south   184/ 188 ocean
  north   175/ 188 ocean
  west    185/ 185 ocean
  east      0/ 185 ocean
```

The edges match the config: east solid land and correctly closed, west fully open,
north and south mixed where they meet the coast.

Note the spacing: **2.88 km, not 3.06 km.** Same 1/36° grid, but a degree of longitude
is shorter at 20°N than at the equator. Always read `pm` and `pn` rather than assuming.

| | Parent Canary_12 | AGRIF child |
|---|---|---|
| Resolution | 1/12° ≈ 9.2 km | **1/36° ≈ 2.88 km** |
| Grid | 81 × 123 × 50 | 188 × 185 × 50 |
| dt | 300 s | 100 s |

### Grid stiffness

When the model runs it reports, for each grid:

```text
 Maximum grid stiffness ratios:   rx0 = 0.20006   rx1 = 14.836     <- parent
 Maximum grid stiffness ratios:   rx0 = 0.20000   rx1 = 14.837     <- child
```

`rx1`, the Haney number, measures how steeply the sigma layers tilt. High values risk
spurious pressure-gradient forces; these are on the high side and the run is stable
throughout.

The child's `rx1` is **essentially unchanged from its parent's** — 14.837 against
14.836. That is worth noting, because refining a grid does not automatically make it
stiffer: it depends on what the finer grid resolves. Over Canary's shelf break the
extra resolution did not sharpen the slope enough to matter, while elsewhere it can.
Phase 9's Agulhas child, built at a lower `rfact`, came out *lower* than its parent.

`rx0` landed on the requested `rfact = 0.2` for both grids.