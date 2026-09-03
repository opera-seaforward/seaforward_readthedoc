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
python make_ini.py canary_ibc_zoom_agrif.ini
```

It reads the child grid correctly and writes a `.nc.1` file. Every sign says success.

**And the file can be unusable.** Along the way it prints warnings that are easy to
scroll past:

```text
  Interpolate v from OGCM to CROCO grid on each z level
[########....] 45/50   Warning: less than 10 good values in this layer
[#########...] 46/50   Warning: no good data in this layer
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
`_FillValue`. CROCO reads that as a velocity of 10³⁷ m/s and reports a kinetic energy
of around 10⁷¹ at step zero, before a single timestep. That number is the signature:
the initial condition is broken, and it is not an instability.

Use SEA-FORWARD's `make_ini` instead, which is what the rest of this step does.

### 3c — Building the child's IC

**Set up a generation directory** containing the **child** grid renamed to
`croco_grd.nc`, plus a `crocotools_param.py`:

```bash
CGEN=~/seaforward/forecast/scratch/Canary_AGRIF/child_gen/CROCO_FILES
mkdir -p "$CGEN"
cp ~/seaforward/forecast/scratch/Canary_AGRIF/CROCO_FILES/croco_grd.nc.1 "$CGEN/croco_grd.nc"
cp ~/seaforward/forecast/configs/Canary_12/crocotools_param.py           "$CGEN/"
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
obc_dict     = dict(south=1, west=1, east=0, north=1)   # E=African coast (closed); S,W,N open
```

For this child those are already right — Step 2's edge check gave east 0/185, solid
land, and the other three open, matching the parent. A child whose box sits differently
may not match, so read its mask rather than assuming. `sigma_params` must equal the
parent's `N=50`, which it will if you copied the parent's file.

**Run make_ini** with the same arguments the forecast driver uses for the spin-up:

```bash
MERC=~/seaforward/forecast/scratch/Canary_12/downloaded_data/MERCATOR/MERCATOR_20260711_00.nc
cd ~/seaforward/sftools
conda activate seaforward
python seaforward.py make_ini \
    --input_file "${MERC}" --output_dir "${CGEN}" \
    --run_date "2026-07-11 00:00:00" --hdays 2 --Yorig 2000
```

`--run_date` is the **cycle** date and `--hdays 2` walks back two days, which lands on
2026-07-09 — the same instant as the parent's IC. See *Matching the clocks* below.

**Verify before going further:**

```bash
python3 << 'PYEOF'
import xarray as xr, numpy as np, glob, os
CGEN = os.path.expanduser('~/seaforward/forecast/scratch/Canary_AGRIF/child_gen/CROCO_FILES')
f = sorted(glob.glob(CGEN + '/croco_ini_*.nc'))[-1]
d = xr.open_dataset(f, decode_times=False)
print(os.path.basename(f))
for v in ['temp', 'salt', 'u', 'v', 'zeta']:
    a = d[v].values
    print('%-5s min=%11.4g max=%11.4g nan=%d'
          % (v, np.nanmin(a), np.nanmax(a), int(np.isnan(a).sum())))
print('time =', float(d.scrum_time.values.ravel()[0]) / 86400, 'days')
PYEOF
```

```text
croco_ini_MERCATOR_20260711_00.nc
temp  min=          0 max=      27.47 nan=0
salt  min=          0 max=      37.31 nan=0
u     min=    -0.5657 max=     0.3456 nan=0
v     min=     -0.368 max=     0.6385 nan=0
zeta  min=     -0.215 max=     0.1355 nan=0
time = 9686.0 days
```

Velocities within about ±0.6 m/s, zero NaNs, and no `9.969e+36` anywhere. That is a
usable initial condition.

### 3d — Matching the clocks

The parent and child ICs must start at the **same instant**. Two traps:

- SEA-FORWARD's forecast ICs are named for the **cycle date**, not their valid time.
  `croco_ini_MERCATOR_20260711_00.nc` is the ocean state at **2026-07-09**, because
  the driver runs `--hdays 2` of spin-up before the cycle date.
- A Mercator download's record 0 may not be the day you assume.

Verify explicitly rather than assume:

```bash
python3 << 'PYEOF'
import xarray as xr, os
P = os.path.expanduser('~/seaforward/forecast/model-runs/Canary_12/20260711/'
                       'gen_spinup/CROCO_FILES/croco_ini_MERCATOR_20260711_00.nc')
C = os.path.expanduser('~/seaforward/forecast/scratch/Canary_AGRIF/child_gen/'
                       'CROCO_FILES/croco_ini_MERCATOR_20260711_00.nc')
for f, lbl in [(P, 'parent'), (C, 'child ')]:
    d = xr.open_dataset(f, decode_times=False)
    print(lbl, float(d.scrum_time.values.ravel()[0]) / 86400, 'days')
PYEOF
```

```text
parent 9686.0 days
child  9686.0 days
```

They must match. A mismatch means the child starts from a different ocean than the
parent, and the nest is wrong from step zero. Here they agree by construction — same
tool, same Mercator file, same `--hdays`.