### 2a — Why this doesn't use the tool you already know

Phase 2 built IGOG_12's grid with `make_grid.py` and a `grid.ini`. That script
**cannot build a zoom grid** — it has no notion of a parent. The AGRIF logic lives in
a Python class, `CROCO`, in `code/croco_pytools/prepro/Modules/croco_class.py`, and
the only thing shipped that drives it is a Jupyter notebook,
`nb_make_grid_zoom.ipynb`.

Open that notebook and most of it is `edit_section_widget(...)` calls — interactive
widgets for editing config values by clicking. Strip those away and the actual work is
four method calls:

```python
croco = CROCO("some_zoom.ini")   # read the config
croco.create_grid()              # build the child's lon/lat as a 3x refinement
croco.create_mask_and_topo()     # interpolate bathymetry, build the mask, merge edges
croco.save_grid_nc()             # write croco_grd.nc.1 + AGRIF_FixedGrids.in
```

The widgets only exist to write values into the `.ini`. **If you write the `.ini`
yourself, you don't need Jupyter at all** — you can call those four methods from an
ordinary script. That's what this step does.

### 2b — Set up the working directory

Do **not** build the AGRIF child inside `scratch/IGOG_12/`. That directory holds a
working, compiled forecast configuration; the AGRIF setup needs parent and child files
side by side and will clutter it. Make a separate one:

```bash
mkdir -p ~/seaforward/forecast/scratch/IGOG_AGRIF/CROCO_FILES

# the child grid is built FROM the parent, so the parent must be there first
cp ~/seaforward/forecast/scratch/IGOG_12/CROCO_FILES/croco_grd.nc \
   ~/seaforward/forecast/scratch/IGOG_AGRIF/CROCO_FILES/croco_grd.nc

ls -la ~/seaforward/forecast/scratch/IGOG_AGRIF/CROCO_FILES/
```
```
-rw-r--r-- 1 you you 1792611 Jul 16 22:19 croco_grd.nc
```

That's a **copy**, deliberately. The zoom config points at it as `parent_grid`, and
the child gets written next to it as `croco_grd.nc.1`. Both grids end up in one place,
which is what the model needs at run time.

### 2c — Write the zoom config

The config goes in the **prepro directory**, because that's where you'll run the
script from:

```bash
nano ~/seaforward/code/croco_pytools/prepro/igog_zoom_agrif.ini
```

Type (or paste) this, substituting your own username and your `imin/imax/jmin/jmax`
from Step 1:

```ini
[Croco_Files]
croco_files_dir = /home/you/seaforward/forecast/scratch/IGOG_AGRIF/CROCO_FILES
croco_grd_prefix = croco_grd

[Zoom_Options]
is_zoom = True
is_agrif = True
agrif_level = 1
parent_grid = /home/you/seaforward/forecast/scratch/IGOG_AGRIF/CROCO_FILES/croco_grd.nc

[Grid_Zoom_Params]
north_obc = True
south_obc = True
west_obc = True
east_obc = True
merging_area = 5

[Grid_Zoom_Agrif]
coef = 3
imin = 19
imax = 47
jmin = 67
jmax = 95

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

!!! warning
    ⚠️ **Pasting long heredocs into a terminal is unreliable** — a `cat > file << 'EOF'` block can collide with whatever you paste after it and truncate the file silently. Either use nano as above, or write it with a Python block (`python3 - << 'PY'`). Either way, **check the file afterwards**: `wc -l` and `tail`.

**Section by section:**

| Section | Key | Meaning |
|---|---|---|
| `[Croco_Files]` | `croco_files_dir` | where the child grid gets written |
| | `croco_grd_prefix` | base name; `agrif_level` appends the `.1` |
| `[Zoom_Options]` | `is_zoom` / `is_agrif` | both True — a zoom grid, AGRIF-style |
| | `agrif_level = 1` | first-level child → writes `croco_grd.nc.1` |
| | `parent_grid` | **must already exist** (2b) |
| `[Grid_Zoom_Params]` | `*_obc` | which edges are open. From your Step 1 mask check |
| | `merging_area = 5` | blend the child's bathymetry into the parent's over 5 child cells at each open edge, so the two grids agree on depth where they exchange data |
| `[Grid_Zoom_Agrif]` | `coef = 3` | refinement ratio — **3 or 5 only** |
| | `imin/imax/jmin/jmax` | the box, **in parent indices**, from Step 1 |
| `[Grid_Smoothing_Params]` | `hmin` | minimum depth (m) — shallower cells get raised to this |
| | `hmax` | maximum depth |
| | `rfact` | bathymetry smoothing target. Lower = smoother = more stable, but less faithful |
| | `smooth_meth` | the smoothing algorithm |
| `[Grid_Input_Files]` | `topo_file` | the bathymetry dataset |
| | `shp_file` | the coastline shapefile |

**Two things absent, and both are AGRIF constraints in disguise:**

- **No `[Sigma_Params]`.** No `N`, no `theta_s`, no `hc`. The child inherits the
  parent's vertical grid — that's the "child N must equal parent N" rule, enforced by
  giving you nowhere to type a different number.
- **No lon/lat.** No `central_lon`, no `size_x_km`. The child's position comes
  entirely from `parent_grid` + the index box. This is why Step 1 converts your
  lon/lat box to indices.

**Reuse the paths from your parent's config** rather than typing them fresh —
`topo_file` and `shp_file` should be exactly what built the parent:

```bash
grep -iE "shp_file|topo_file|topo_file_reader" ~/seaforward/forecast/configs/IGOG_12/grid.ini
```
```
topo_file_reader = etopo2
topo_file = /home/you/seaforward/data/DATASETS_CROCOTOOLS/Topo/etopo2.nc
shp_file = /home/you/seaforward/data/DATASETS_CROCOTOOLS/gshhs/GSHHS_shp/i/GSHHS_i_L1.shp
```

If those differ from what you wrote, fix the `.ini` — those are the proven paths.

**Verify the config parses** before running anything:

```bash
cd ~/seaforward/code/croco_pytools/prepro
python3 -c "
import configparser
c = configparser.ConfigParser(); c.read('igog_zoom_agrif.ini')
print('sections:', c.sections())
z = c['Grid_Zoom_Agrif']
print('box: imin=%s imax=%s jmin=%s jmax=%s coef=%s'
      % (z['imin'], z['imax'], z['jmin'], z['jmax'], z['coef']))
print('agrif:', c['Zoom_Options']['is_agrif'], 'level', c['Zoom_Options']['agrif_level'])
"
```
```
sections: ['Croco_Files', 'Zoom_Options', 'Grid_Zoom_Params', 'Grid_Zoom_Agrif',
           'Grid_Smoothing_Params', 'Grid_Isolated_Waterbodies', 'Grid_Input_Files']
box: imin=19 imax=47 jmin=67 jmax=95 coef=3
agrif: True level 1
```

**Seven sections.** If you see fewer, the file got truncated — rewrite it.

### 2d — Write the build script

Same directory:

```bash
nano ~/seaforward/code/croco_pytools/prepro/build_igog_agrif.py
```

```python
import matplotlib
matplotlib.use("Agg")            # save figures instead of opening a window
import matplotlib.pyplot as plt

from Modules.croco_class import CROCO

INI = "igog_zoom_agrif.ini"

print(f"=== loading {INI}")
croco = CROCO(INI)

# 1. the child's lon/lat, as a 3x refinement of the parent's index box
print("=== create_grid()")
croco.create_grid()
croco.plot_grid_outline_zoom()
plt.savefig("/tmp/agrif_outline.png", dpi=110, bbox_inches="tight")
plt.close("all")

# 2. bathymetry + land mask, merged into the parent at the open edges
print("=== create_mask_and_topo()")
croco.create_mask_and_topo()
croco.plot_h_zoom()
plt.savefig("/tmp/agrif_bathy.png", dpi=110, bbox_inches="tight")
plt.close("all")

# 3. write croco_grd.nc.1 + AGRIF_FixedGrids.in
print("=== save_grid_nc()")
croco.save_grid_nc()

print("\nDONE — check /tmp/agrif_outline.png and /tmp/agrif_bathy.png")
```

`Ctrl+O` `Enter`, `Ctrl+X`.

**Three things in that script are not optional:**

1. **`matplotlib.use("Agg")` must come before `import matplotlib.pyplot`.** The
   notebook uses `%matplotlib widget`, which needs a browser. In a script there's no
   display, so plotting would fail. `Agg` renders to a file instead. The order
   matters — set the backend before pyplot is imported.
2. **`from Modules.croco_class import CROCO`** is a *relative* package import. It only
   resolves if your working directory is `prepro/`. Run the script from anywhere else
   and you get `ModuleNotFoundError: No module named 'Modules'`.
3. **The plot calls are worth keeping.** They're your only check that the child landed
   where you intended, before you spend time on ICs and compiling.

### 2e — Run it

Two requirements: the right directory, and the right conda environment.

```bash
cd ~/seaforward/code/croco_pytools/prepro     # REQUIRED for the Modules import
conda activate seaforward                     # the env that built the parent's grid
python build_igog_agrif.py 2>&1 | tail -20
```

Expected output:

```
=== loading igog_zoom_agrif.ini
=== create_grid()
Reading CROCO grid: .../IGOG_AGRIF/CROCO_FILES/croco_grd.nc
=== create_mask_and_topo()
Reading topography file: .../DATASETS_CROCOTOOLS/Topo/etopo2.nc
Single region dataset imin/imax= 5575 5719
Interpolating topography to CROCO grid
Finished interpolating
Matching Parent and Child mask close to boundary
Processing mask to close narrow bay and narrow land (1 point wide)
=== save_grid_nc()
Writting .../IGOG_AGRIF/CROCO_FILES/croco_grd.nc.1 done
Create an AGRIF_FixedGrids.in file
DONE — check /tmp/agrif_outline.png and /tmp/agrif_bathy.png
```

Two lines there are AGRIF-specific and worth noticing:

- **`Matching Parent and Child mask close to boundary`** — the `merging_area` at work,
  reconciling the two grids' land/sea at the interface.
- **`Create an AGRIF_FixedGrids.in file`** — the tool writes this for you. You do not
  hand-author it.

!!! warning
    ⚠️ **If you see `==> North limits displacement +1`** (or East/West/South) — the tool has moved your box. Read the displacement section below before going further.

### 2f — What you should now have

```bash
ls -la ~/seaforward/forecast/scratch/IGOG_AGRIF/CROCO_FILES/
```
```
-rw-r--r-- 1 you you     204 AGRIF_FixedGrids.in    <- the child-in-parent definition
-rw-r--r-- 1 you you 1792611 croco_grd.nc           <- the parent (you copied it)
-rw-r--r-- 1 you you  906378 croco_grd.nc.1         <- THE CHILD GRID
```

Note the naming: **`croco_grd.nc.1`** — the `.1` suffix, from `agrif_level = 1`. This
is CROCO's AGRIF convention and it carries through everything (`croco_ini.nc.1`,
`croco.in.1`, `croco_his.nc.1`). It is *not* `1_croco_grd.nc`.

Look at the two figures before continuing:

![AGRIF child placement](img/agrif_child_placement.png)

*`/tmp/agrif_bathy.png` — the child (red box) over São Tomé and Príncipe, inside the IGOG_12 parent. All four edges sit in 2000–3000 m of open water; the islands are safely interior. This is the picture you want: box in the right place, edges in deep water, features of interest inside.*

Viewing figures from WSL, if interop is off:

```bash
cp /tmp/agrif_outline.png /tmp/agrif_bathy.png /mnt/c/temp/
# then open them from Windows
```
or
```bash
explorer.exe "$(wslpath -w /tmp/agrif_bathy.png)"
```

### `AGRIF_FixedGrids.in`

```
    1
    20    48    68    96    3    3    3    3
    0
# number of children per parent
# imin imax jmin jmax spacerefx spacerefy timerefx timerefy
# [all coordinates are relative to each parent grid!]
```

Read it as: one child, occupying parent cells i=20–48, j=68–96, refined **3×** in
space and taking **3** sub-steps per parent step. (The indices are one higher than
requested — Fortran is 1-based.)

For comparison, somisana's `sa_eez_01` runs three children off one parent:

```
    3
    94    305    60    110    3    3    3    3
    420    530    75    109    3    3    3    3
    648    768    70    103    3    3    3    3
```

### ⚠️ The displacement loop

`easygrid.py` **silently moves your box**. Watch for messages like:

```
==> North limits displacement +1
==> North limits displacement +1
```

The rule (`Modules/easygrid.py`, ~line 490) compares the outermost two rows/columns
of the child's mask:

```python
northchk = abs(maskr_coarse[-2, :] - maskr_coarse[-1, :])
if sum(northchk) != 0:
    inputs.jmax = inputs.jmax + 1
    print("==> North limits displacement +1")
```

If a coastline crosses near the edge, it shifts the edge outward and retries. It is
looking for an edge whose mask is uniform in the boundary-normal direction.

**It never checks whether the destination is viable.** A solid-land edge is perfectly
uniform, so it passes. In the coastal example below, a requested `jmax = 124`
(4.21°N) marched to **133** (4.94°N) — onto the continent — and the tool reported
success. Setting `north_obc = False` did **not** stop it; the loop runs on mask
geometry, before the obc flags are considered.

**Always compare what you asked for against what `AGRIF_FixedGrids.in` says, and re-check the child grid's edges after building.**

### Verify the child grid before going further

Three checks. First, **did the tool build what you asked for?**

```bash
cd ~/seaforward/forecast/scratch/IGOG_AGRIF/CROCO_FILES
cat AGRIF_FixedGrids.in
```
```
    1
    20    48    68    96    3    3    3    3     <- requested 19/47/67/95, +1 for Fortran
    0
```

If those numbers differ from your request by more than the +1 Fortran offset, the
displacement loop moved your box. Go back and look at why.

Second, **dimensions and geography**:

```bash
ncdump -h croco_grd.nc.1 | grep -E "xi_rho|eta_rho"
```
```
        xi_rho = 86 ;
        eta_rho = 86 ;
```

```python
import xarray as xr
g = xr.open_dataset('croco_grd.nc.1')
print('lon: %.3f to %.3f E'   % (float(g.lon_rho.min()), float(g.lon_rho.max())))
print('lat: %.3f to %.3f N'   % (float(g.lat_rho.min()), float(g.lat_rho.max())))
print('depth: %.0f to %.0f m' % (float(g.h.min()), float(g.h.max())))
print('ocean: %.1f%%'         % (float(g.mask_rho.mean()) * 100))
```
```
lon: 5.554 to 7.892 E
lat: -0.471 to 1.874 N
depth: 50 to 3722 m
ocean: 98.6%
```

The 86×86 is the 3× refinement of the 29×29 parent box. The 50 m floor is `hmin`
biting at the island shores. The 1.4% land is São Tomé and Príncipe — interior, where
you want them.

Third, **the actual resolution** — confirm the refinement is what you think:

```python
import xarray as xr, numpy as np
g = xr.open_dataset('croco_grd.nc.1')
dx = 1 / g.pm.values      # pm, pn are INVERSE grid spacings
dy = 1 / g.pn.values
print('child dx: %.2f - %.2f km' % (dx.min()/1000, dx.max()/1000))
print('child dy: %.2f - %.2f km' % (dy.min()/1000, dy.max()/1000))
```
```
child dx: 3.05 - 3.06 km
child dy: 3.06 - 3.07 km
```

Exactly 1/36° — three times the parent's 1/12° (≈9.2 km). The small spread is the
cos(lat) convergence across the box.

| | Parent IGOG_12 | AGRIF child |
|---|---|---|
| Resolution | 1/12° ≈ 9.2 km | **1/36° ≈ 3.06 km** |
| Grid | 105 × 141 × 50 | 86 × 86 × 50 |
| dt | 300 s | 100 s |

Note the contrast with the Phase 7 offline nest, which went 1/12° → 1/25° (a 2.08×
jump). AGRIF's integer-ratio constraint takes that freedom away — 3× or 5×, nothing
else. That is the price of the tighter coupling.

Finally, watch for the **grid stiffness** number when the model first runs:

```
Maximum grid stiffness ratios:   rx0 = 0.347   rx1 = 18.39
```

`rx1` (the Haney number) measures how steeply the sigma layers tilt. Above ~10 you
start getting spurious pressure-gradient forces; 18.4 is high but survivable. It's
high here *because* the refinement resolves São Tomé's flanks more sharply than the
parent does — the island you nested for is what stresses the coordinate. If the child
blows up **mid-run** (as opposed to at step zero), this is the first suspect; the fix
is a stronger `rfact` in `[Grid_Smoothing_Params]`.

`rx0 = 0.347` is above the requested `rfact = 0.2` because `merging_area` blends the
parent's bathymetry back in at the edges, partly undoing the smoothing.