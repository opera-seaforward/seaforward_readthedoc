### 3a — What the child needs, and what it doesn't

The child is a full CROCO grid running its own dynamics. Like any CROCO run it needs
a **starting ocean state** — temperature, salinity, velocity and sea surface at every
cell, at the moment the run begins.

But unlike a standalone run, it does **not** need boundary conditions:

| File | Parent | AGRIF child | Why |
|---|---|---|---|
| grid | `croco_grd.nc` | `croco_grd.nc.1` | built in Step 2 |
| initial condition | `croco_ini.nc` | **`croco_ini.nc.1`** | **this step** |
| boundary conditions | `croco_bry.nc` | **none** | AGRIF supplies them every barotropic step |
| surface forcing | GFS (online) | same GFS | both grids read the same atmosphere |

**That missing bry file is the whole point of online nesting.** In the Phase 6 offline
nest, `croco_bry_NEST_*.nc` *was* the mechanism — the entire coupling lived in that
file. Here there's nothing, because the parent hands the child its boundaries in
memory, every step, while both are running.

The child's IC comes from **the same source as the parent's** — Mercator, interpolated
onto the child grid. Not from the parent's output. (somisana does the same: their
`make_ini_inter` reads GLORYS directly for each child.)

### 3b — Which tool, and why it matters

!!! note
    **Use SEA-FORWARD's own `make_ini`, not croco_pytools'.**

This is not a style preference. croco_pytools ships a zoom-aware IC builder and it
*looks* right — there's even an example config, `Examples/benguela_multifiles/
ibc_zoom_agrif.ini`, that does exactly what you want:

```bash
python make_ini.py igog_ibc_zoom_agrif.ini
```

It runs. It reads the child grid correctly (`Reading CROCO grid: .../croco_grd.nc.1`).
It writes `croco_ini_mercator_Y2026M07.nc.1`. Every sign says success.

**And the file is poisoned.** Along the way it prints warnings that are easy to scroll
past:

```
  Interpolate v from OGCM to CROCO grid on each z level
[########....] 45/50   Warning: less than 10 good values in this layer
[#########...] 46/50   Warning: no good data in this layer
[##########..] 47/50   Warning: no good data in this layer
```

Here is what those mean. `Modules/interp_tools.py`, in `interp_horiz`:

```python
if NGood == 0:
    print("\n  Warning: no good data in this layer")
    tmpvar = np.full_like(crocogrd.lon, np.nan)          # whole layer -> NaN
elif NGood < 10:
    # Fill with NaN instead of mean to avoid spurious values
    print("\n  Warning: less than 10 good values in this layer")
    tmpvar = np.full_like(crocogrd.lon, np.nan)          # whole layer -> NaN
```

(Note the function's own docstring says "*if less than 10 good data: put the average
value everywhere*" — the code does something else. Someone changed the behaviour and
left the docstring stale. Don't trust the docstring.)

`NGood` counts valid source points **within the child's footprint**. A small box over
deep water has fewer than 10 wet Mercator points at the deepest z-levels, so those
layers become NaN, which netCDF writes as **`9.969e+36`** — the standard float
`_FillValue`. CROCO reads that as a velocity of 10³⁷ m/s and reports:

```
STEP   time[DAYS] KINETIC_ENRG    POTEN_ENRG    TOTAL_ENRG    NET_VOLUME   trd
   0  9688.00000 1.492439643E+71           NaN           NaN 1.7790546E+14  0
```

**Kinetic energy of 1.49e+71 at step zero** — before a single timestep. That number is
the signature of this bug. If you see it, the IC is broken; it is not an instability.

The thresholds `0` and `10` are **hardcoded**. The `min_nb_valid_data` key in the
config looks like the knob for this, but it's passed to a *different* function
(`ibc_tools.py` line 564, as `Nzgoodmin`) and has no effect here. Setting it to 1
tonight made the warning count go *up*, not down.

**It is worth proving the source data is not at fault**, otherwise you will spend an
hour blaming Mercator:

```python
import xarray as xr, numpy as np
MERC = ('/home/you/seaforward/forecast/model-runs/IGOG_12/20260713/'
        'downloaded_data/MERCATOR/MERCATOR_20260713_00.nc')
d = xr.open_dataset(MERC)
print('depth levels:', len(d.depth))
print('deepest: %.0f m' % float(d.depth.max()))
t = d.thetao.isel(time=1)
for k in [0, 20, 35, 40, 45, 49]:
    lay = t.isel(depth=k).values
    print('  depth %7.1f m: %5d valid of %d'
          % (float(d.depth[k]), np.isfinite(lay).sum(), lay.size))
```
```
depth levels: 50
deepest: 5728 m
  depth     0.5 m: 14566 valid of 24325
  depth  1062.4 m: 12116 valid of 24325
  depth  2225.1 m: 10443 valid of 24325
  depth  3992.5 m:  5465 valid of 24325     <- plenty, below the child's 3722 m
  depth  5727.9 m:     0 valid              <- only the deepest level is empty
```

Mercator has data well below the child's seafloor. The problem is that `NGood` is
counted **after subsetting to the child's small footprint** — globally a level has
5465 valid points, but inside an 86×86 window over São Tomé it has fewer than 10, and
the layer is discarded. The parent never hits this because its footprint spans the
whole basin.

somisana hits none of this because they use their own tool
(`cli.py make_ini_inter`). Do the same:

**Set up a generation directory** containing the **child** grid renamed to
`croco_grd.nc`, plus a `crocotools_param.py`:

```bash
CGEN=~/seaforward/forecast/scratch/IGOG_AGRIF/child_gen/CROCO_FILES
mkdir -p "$CGEN"
cp ~/seaforward/forecast/scratch/IGOG_AGRIF/CROCO_FILES/croco_grd.nc.1 "$CGEN/croco_grd.nc"
cp ~/seaforward/forecast/configs/IGOG_12/crocotools_param.py           "$CGEN/"
```

That rename is the trick: `make_ini` reads whatever `croco_grd.nc` it finds in
`--output_dir`. It doesn't know or care that the grid is a child.

**Edit the child's boundaries** — the copied `crocotools_param.py` has the *parent's*
`obc_dict`, which may not match the child:

```bash
nano "$CGEN/crocotools_param.py"
```

`Ctrl+W` `obc_dict` `Enter`:

```python
obc_dict     = dict(south=1, west=1, east=0, north=0)   # parent IGOG_12
```

For the São Tomé child, all four edges are in open ocean:

```python
obc_dict     = dict(south=1, west=1, east=1, north=1)   # AGRIF child: all edges open ocean
```

`Ctrl+O` `Enter`, `Ctrl+X`. Then check `sigma_params` on the way past — it must match
the parent (`N=50`), which it will if you copied the parent's file:

```bash
grep -E "obc_dict|sigma_params" "$CGEN/crocotools_param.py"
```
```
sigma_params = dict(theta_s=7, theta_b=2, N=50, hc=200)
obc_dict     = dict(south=1, west=1, east=1, north=1)
```

**Run make_ini** with the same arguments the forecast driver uses for the spin-up:

```bash
MERC=~/seaforward/forecast/model-runs/IGOG_12/20260713/downloaded_data/MERCATOR/MERCATOR_20260713_00.nc

cd ~/seaforward/sftools
conda activate seaforward
python seaforward.py make_ini \
    --input_file "${MERC}" --output_dir "${CGEN}" \
    --run_date "2026-07-13 00:00:00" --hdays 2 --Yorig 2000
```

`--run_date` is the **cycle** date and `--hdays 2` walks back two days — which is how
this lands on 2026-07-11, the same instant as the parent's IC. See "Matching the
clocks" below.

**Always verify before running:**

```python
import xarray as xr, numpy as np, glob
f = sorted(glob.glob(CGEN + '/croco_ini_*.nc'))[-1]
d = xr.open_dataset(f, decode_times=False)
for v in ['temp', 'salt', 'u', 'v', 'zeta']:
    a = d[v].values
    print('%-5s min=%11.4g max=%11.4g nan=%d'
          % (v, np.nanmin(a), np.nanmax(a), int(np.isnan(a).sum())))
print('time =', float(d.scrum_time.values.ravel()[0]) / 86400, 'days')
```

You want `u`/`v` within about ±1 m/s, zero NaNs, and **the same `scrum_time` as the
parent's IC**. Compare the two:

| | croco_pytools | SEA-FORWARD `make_ini` |
|---|---|---|
| `u` max | `9.969e+36` ✗ | **0.6396** ✓ |
| `v` max | `9.969e+36` ✗ | **0.3081** ✓ |
| temp NaN | 14 ✗ | **0** ✓ |

### Matching the clocks

The parent and child ICs must start at the **same instant**. Two traps:

- SEA-FORWARD's forecast ICs are named for the **cycle date**, not their valid time.
  `croco_ini_MERCATOR_20260713_00.nc` is the ocean state at **2026-07-11**, because
  the driver runs `--hdays 2` of spin-up before the cycle date.
- A Mercator download's record 0 may not be the day you think. Check:

```python
d = xr.open_dataset(MERC)
print(d.time.values[:4])
# 2026-07-10, 2026-07-11, 2026-07-12, 2026-07-13
```

Verify explicitly rather than assume:

```python
for f, lbl in [('croco_ini.nc', 'parent'), ('croco_ini.nc.1', 'child ')]:
    d = xr.open_dataset(f, decode_times=False)
    print(lbl, float(d.scrum_time.values.ravel()[0]) / 86400, 'days')
# parent 9688.0 days
# child  9688.0 days      <- must match
```