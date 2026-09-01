### 3a — What the child needs, and what it doesn't

The child is a full CROCO grid running its own dynamics. Like any CROCO run it needs
a **starting ocean state** — temperature, salinity, velocity and sea surface at every
cell, at the moment the run begins.

Unlike a standalone run, it does **not** need boundary conditions:

| File | Parent | AGRIF child | Why |
|---|---|---|---|
| grid | `croco_grd.nc` | `croco_grd.nc.1` | built in Step 2 |
| initial condition | `croco_ini.nc` | **`croco_ini.nc.1`** | this step |
| boundary conditions | `croco_bry.nc` | **none** | AGRIF supplies them every barotropic step |
| surface forcing | GFS (online) | same GFS | both grids read the same atmosphere |

**That missing bry file is the whole point of online nesting.** In the Phase 7 offline
nest, `croco_bry_NEST_*.nc` *was* the mechanism — the entire coupling lived in that
file. Here there is nothing, because the parent hands the child its boundaries in
memory, every step, while both are running.

The child's initial condition comes from **the same source as the parent's** —
Mercator, interpolated onto the child grid — not from the parent's output.

### 3b — Which tool, and why it matters

!!! warning
    **Use SEA-FORWARD's `make_ini`, not croco_pytools'.**

croco_pytools ships a zoom-aware IC builder, and it *looks* right. There is an example
config to copy from — `Examples/benguela_multifiles/ibc_zoom_agrif.ini` — and adapting
it for the child runs cleanly:

```bash
cd ~/seaforward/code/croco_pytools/prepro
python make_ini.py igog_ibc_zoom_agrif.ini
```

It reads the child grid correctly (`Reading CROCO grid: .../croco_grd.nc.1`) and writes
`croco_ini_mercator_Y2026M07.nc.1`. Every sign says success.

**And the file is unusable.** Along the way it prints warnings that are easy to scroll
past:

```text
  Interpolate v from OGCM to CROCO grid on each z level
[########....] 45/50   Warning: less than 10 good values in this layer
[#########...] 46/50   Warning: no good data in this layer
[##########..] 47/50   Warning: no good data in this layer
```

Those come from `Modules/interp_tools.py`, in `interp_horiz`:

```python
if NGood == 0:
    # No good data: return nan array with target shape
    print("\n  Warning: no good data in this layer")
    tmpvar = np.full_like(crocogrd.lon, np.nan)
elif NGood < 10:
    # Fill with NaN instead of mean to avoid spurious values
    print("\n  Warning: less than 10 good values in this layer")
    tmpvar = np.full_like(crocogrd.lon, np.nan)
```

A whole layer becomes NaN, which netCDF writes as **`9.969e+36`**, the standard float
`_FillValue`. CROCO reads that as a velocity of 10³⁷ m/s and reports:

```text
STEP   time[DAYS] KINETIC_ENRG    POTEN_ENRG    TOTAL_ENRG    NET_VOLUME   trd
   0  9688.00000 1.492439643E+71           NaN           NaN 1.7790546E+14  0
```

**Kinetic energy of 1.49e+71 at step zero**, before a single timestep. That number is
the signature: the initial condition is broken, and it is not an instability.

**The source data is not at fault**, which is worth establishing before you spend an
hour blaming Mercator:

```bash
cd ~/seaforward
python3 << 'PYEOF'
import xarray as xr, numpy as np
c = xr.open_dataset('forecast/scratch/IGOG_AGRIF/CROCO_FILES/croco_grd.nc.1')
lo, la = float(c.lon_rho.min()), float(c.lon_rho.max())
s,  n  = float(c.lat_rho.min()), float(c.lat_rho.max())

MERC = ('forecast/model-runs/IGOG_12/20260713/downloaded_data/'
        'MERCATOR/MERCATOR_20260713_00.nc')
d   = xr.open_dataset(MERC)
sub = d.thetao.isel(time=1).sel(longitude=slice(lo, la), latitude=slice(s, n))
print('child footprint: %d x %d Mercator points'
      % (sub.sizes['longitude'], sub.sizes['latitude']))
for k in [0, 20, 35, 40, 45, 49]:
    lay = sub.isel(depth=k).values
    print('  depth %7.1f m: %5d valid of %d'
          % (float(d.depth[k]), int(np.isfinite(lay).sum()), lay.size))
PYEOF
```

```text
child footprint: 88 x 122 Mercator points
  depth     0.5 m:  7085 valid of 10736
  depth    77.9 m:  6137 valid of 10736
  depth  1062.4 m:  5351 valid of 10736
  depth  2225.1 m:  4187 valid of 10736
  depth  3992.5 m:  1218 valid of 10736
  depth  5727.9 m:     0 valid of 10736
```

Mercator has ample data through the child's whole depth range — over a thousand valid
points at 3992 m, against a threshold of ten. Only the deepest level, 5728 m, is empty,
and that sits below the child's 5089 m seafloor.

So the tool discards layers it has data for. Whatever the trigger, the outcome is
measurable and the fix is to use the other tool.

### 3c — Building the child's IC

**Set up a generation directory** containing the **child** grid renamed to
`croco_grd.nc`, plus a `crocotools_param.py`:

```bash
CGEN=~/seaforward/forecast/scratch/IGOG_AGRIF/child_gen/CROCO_FILES
mkdir -p "$CGEN"
cp ~/seaforward/forecast/scratch/IGOG_AGRIF/CROCO_FILES/croco_grd.nc.1 "$CGEN/croco_grd.nc"
cp ~/seaforward/forecast/configs/IGOG_12/crocotools_param.py           "$CGEN/"
```

That rename is the trick: `make_ini` reads whatever `croco_grd.nc` it finds in
`--output_dir`, and neither knows nor cares that the grid is a child.

**Check the child's boundaries** against the copied `crocotools_param.py`, which holds
the *parent's* `obc_dict`:

```bash
grep -E "obc_dict|sigma_params" "$CGEN/crocotools_param.py"
```

```text
sigma_params = dict(theta_s=7, theta_b=2, N=50, hc=200)
obc_dict     = dict(south=1, west=1, east=0, north=0)
```

For this child those are already right — Step 2's edge check gave east 0/368 and north
22/266, both coast, matching the parent. A child whose box sits differently may not
match, so read its mask rather than assuming. `sigma_params` must equal the parent's
`N=50`, which it will if you copied the parent's file.

**Run make_ini** with the same arguments the forecast driver uses for the spin-up:

```bash
MERC=~/seaforward/forecast/model-runs/IGOG_12/20260713/downloaded_data/MERCATOR/MERCATOR_20260713_00.nc
cd ~/seaforward/sftools
conda activate seaforward
python seaforward.py make_ini \
    --input_file "${MERC}" --output_dir "${CGEN}" \
    --run_date "2026-07-13 00:00:00" --hdays 2 --Yorig 2000
```

`--run_date` is the **cycle** date and `--hdays 2` walks back two days, which lands on
2026-07-11 — the same instant as the parent's IC. See *Matching the clocks* below.

**Verify before going further:**

```bash
python3 << 'PYEOF'
import xarray as xr, numpy as np, glob, os
CGEN = os.path.expanduser('~/seaforward/forecast/scratch/IGOG_AGRIF/child_gen/CROCO_FILES')
f = sorted(glob.glob(CGEN + '/croco_ini_*.nc'))[-1]
d = xr.open_dataset(f, decode_times=False)
for v in ['temp', 'salt', 'u', 'v', 'zeta']:
    a = d[v].values
    print('%-5s min=%11.4g max=%11.4g nan=%d'
          % (v, np.nanmin(a), np.nanmax(a), int(np.isnan(a).sum())))
print('time =', float(d.scrum_time.values.ravel()[0]) / 86400, 'days')
PYEOF
```

You want `u` and `v` within about ±1 m/s, zero NaNs, and the same `scrum_time` as the
parent's IC. The two tools side by side:

| | croco_pytools | SEA-FORWARD `make_ini` |
|---|---|---|
| `u` max | `9.969e+36` | **0.6396** |
| `v` max | `9.969e+36` | **0.3081** |
| NaNs | present | **0** |

### 3d — Matching the clocks

The parent and child ICs must start at the **same instant**. Two traps:

- SEA-FORWARD's forecast ICs are named for the **cycle date**, not their valid time.
  `croco_ini_MERCATOR_20260713_00.nc` is the ocean state at **2026-07-11**, because the
  driver runs `--hdays 2` of spin-up before the cycle date.
- A Mercator download's record 0 may not be the day you assume:

```bash
python3 -c "
import xarray as xr
d = xr.open_dataset('${MERC}')
print(d.time.values[:4])
"
```

Verify explicitly rather than assume:

```bash
python3 << 'PYEOF'
import xarray as xr, os
base = os.path.expanduser('~/seaforward/forecast/scratch/IGOG_AGRIF/CROCO_FILES/')
for f, lbl in [('croco_ini.nc', 'parent'), ('croco_ini.nc.1', 'child ')]:
    d = xr.open_dataset(base + f, decode_times=False)
    print(lbl, float(d.scrum_time.values.ravel()[0]) / 86400, 'days')
PYEOF
```

```text
parent 9688.0 days
child  9688.0 days
```

They must match. A mismatch means the child starts from a different ocean than the
parent, and the nest is wrong from step zero.