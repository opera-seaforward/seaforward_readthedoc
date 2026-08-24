This is the first milestone: a working AGRIF nest, parent and child stepping
together, no feedback yet. Get here before touching `AGRIF_2WAY`.

### 7a — Launch

```bash
cd ~/seaforward/forecast/scratch/IGOG_AGRIF
conda deactivate                       # the model needs the compiler env, not python
source ./config.sh
nohup ./croco croco.in > run_1way.log 2>&1 &
```

**You launch only the parent's `croco.in`.** AGRIF reads it, finds
`AGRIF_FixedGrids.in` in the current directory, sees there's one child, and pulls in
`croco.in.1` by itself. There is no second command, no second executable, no MPI
ranks to split — one process integrates both grids.

`nohup ... &` puts it in the background so you keep your terminal. Watch it with:

```bash
tail -f run_1way.log
```

(`Ctrl+C` stops watching, not the run.) To actually stop the run:

```bash
pkill -f "croco croco.in"
```

!!!warning
    ⚠️ **Run one instance at a time.** Two `croco` processes in the same directory will write over each other's output files and produce nonsense that looks like a physics problem.

### 7b — What the startup tells you

Early in the log, CROCO lists the CPP options it was compiled with:

```
 Activated C-preprocessing Options:
          REGIONAL
          IGOG_12
          AGRIF                 <- the binary really is AGRIF-enabled
```

Further down, the child's boundary conditions appear:

```
          AGRIF_OBC_WEST
          AGRIF_OBC_NORTH
          AGRIF_OBC_SOUTH
          AGRIF_FLUX_BC
          AGRIF_OBC_M2SPECIFIED
          AGRIF_OBC_M3ORLANSKI
          AGRIF_OBC_TORLANSKI
```

These are the child receiving boundaries **from the parent** — the coupling, named.
Note there's no `AGRIF_OBC_EAST` here: the defaults in `cppdefs_dev.h` define all
four, but they're filtered by the parent's own `OBC_*` settings.

You'll also see a wall of warnings. Most are harmless:

```
 WARNING: Unrecognized keyword: start_date  --> DISREGARDED.
 WARNING: Unrecognized keyword: end_date  --> DISREGARDED.
 WARNING: Unrecognized keyword: bulk_forcing  --> DISREGARDED.
```

`start_date`/`end_date` are disregarded because this build has `USE_CALENDAR`
undefined — time comes from `NTIMES × dt` only, so the dates in `croco.in` are
cosmetic. `bulk_forcing` is unused because `ONLINE` is defined and CROCO reads GFS
directly. Neither is a problem, but it's worth knowing *why* so you don't chase them.

The forcing confirmation is worth checking:

```
 Online forcing: datasets in /home/you/.../GFS/for_croco/ with 24 records per day.
```

And each grid announces itself, so you can tell them apart:

```
 IGOG_12 FORECAST                       <- parent (croco.in)
       288  ntimes
    300.00  dt
...
 IGOG_12 AGRIF ZOOM LEVEL 1 (Sao Tome)  <- child (croco.in.1)
       288  ntimes
    100.00  dt                          <- CHECK THIS: parent's dt / timeref
```

That `100.00` is the edit from Step 5b. If it says `300.00`, stop the run now — see
the dt/NTIMES warning above.

Look for the child's grid stiffness too:

```
 Maximum grid stiffness ratios:   rx0 = 0.347   rx1 = 18.39
```

And confirm the child is writing its own output:

```
 DEF_HIS/AVG - Created new netCDF file 'CROCO_FILES/croco_his.nc.1'.
 WRT_GRID -- wrote grid data into file 'CROCO_FILES/croco_his.nc.1'.
```

If `croco_his.nc.1` never appears, the child isn't running at all — check that
`AGRIF_FixedGrids.in` is in the run directory (Step 4c).

### Reading the step tables

Both grids print their own step tables, interleaved:

```
25  9688.08681 2.469078679E-03 ... 2.1948671E+15  0    <- parent
75  9688.08681 2.874230499E-03 ... 1.7790849E+14  0    <- child
76  9688.08796 2.878546270E-03 ...
77  9688.08912 2.882053564E-03 ...
26  9688.09028 2.470478997E-03 ... 2.1948646E+15  0    <- parent
78  9688.09028 2.885023770E-03 ...
```

The columns are: `STEP  time[DAYS]  KINETIC_ENRG  POTEN_ENRG  TOTAL_ENRG NET_VOLUME  trd`.

Reading this takes a moment because two grids share one stream. Tell them apart by
the step number and the volume: the parent's steps advance slowly (25, 26, …) with
`NET_VOLUME ≈ 2.19e+15`; the child's advance 3× faster (75, 76, 77, 78, …) with
`NET_VOLUME ≈ 1.78e+14`.

**Three child steps per parent step, meeting at identical times.** Parent 25 and child
75 both read `9688.08681`; parent 26 and child 78 both read `9688.09028`. That
lock-step is the single best evidence the nest is correctly configured.

What to check, and what each symptom means:

| Check | Good | Bad — and what it means |
|---|---|---|
| **step zero, both grids** | same time, KE ~1e-3 | child KE `1e+71` → **broken IC** (fill values, Step 3), not instability |
| **clock lock** | parent 25 = child 75 = same time | child racing ahead → **child `dt` not divided** (Step 5b) |
| **child KE vs parent** | child **higher** | expected: a finer grid resolves more flow |
| **child NET_VOLUME** | smaller, in proportion | ~8% of the parent for the São Tomé child. Correct, not a symptom |
| **`trd` (last column)** | `0` | non-zero = blowup counter |
| **volume drift** | conserved to ~5 s.f. | steady loss/gain = a boundary problem |

The child's KE being higher (2.87e-3 vs 2.47e-3) and its volume being much smaller are
both *expected* and worth internalising — the smaller volume is a box-size artefact,
not a warning. Tonight both numbers were briefly mistaken for symptoms.

### 7c — Finishing

Success is **two** `MAIN: DONE`, one per grid:

```
 MAIN - number of records written into history  file(s):    5
 MAIN: DONE                                                    <- parent
 MAIN - number of records written into history  file(s):   13
 MAIN: DONE                                                    <- child
```

```bash
grep -c "MAIN: DONE" run_1way.log      # want 2
ls -lh CROCO_FILES/croco_his.nc CROCO_FILES/croco_his.nc.1
```

If the parent says `DONE` and the child says `Abnormal termination: BLOWUP`, that's
**one-way isolation working as designed** — the child died without poisoning the
parent. It also tells you exactly where to look: the child, alone.

```
 MAIN: DONE                              <- parent finished all 288 steps
 MAIN: Abnormal termination: BLOWUP      <- child died
```

Diagnose it by *when* it died:

- **step zero** → the IC (fill values / wrong clock)
- **mid-run** → stability: high `rx1`, or the timestep
- **at a specific time** → forcing or boundary data running out

### Looking at the result

```python
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, xarray as xr

B = 'forecast/scratch/IGOG_AGRIF/CROCO_FILES/'
p = xr.open_dataset(B + 'croco_his.nc',   decode_times=False)
c = xr.open_dataset(B + 'croco_his.nc.1', decode_times=False)

ps = p.temp.isel(time=-1, s_rho=-1).where(p.mask_rho == 1)
cs = c.temp.isel(time=-1, s_rho=-1).where(c.mask_rho == 1)
vmin, vmax = float(cs.min()), float(cs.max())

fig, ax = plt.subplots(1, 2, figsize=(13, 5), constrained_layout=True)
ax[0].pcolormesh(p.lon_rho, p.lat_rho, ps, cmap='RdYlBu_r', vmin=vmin, vmax=vmax)
ax[0].set_title('parent  1/12 (9.2 km)')
ax[0].plot([float(c.lon_rho.min()), float(c.lon_rho.max()), float(c.lon_rho.max()),
            float(c.lon_rho.min()), float(c.lon_rho.min())],
           [float(c.lat_rho.min()), float(c.lat_rho.min()), float(c.lat_rho.max()),
            float(c.lat_rho.max()), float(c.lat_rho.min())], 'k-', lw=1.5)
m1 = ax[1].pcolormesh(c.lon_rho, c.lat_rho, cs, cmap='RdYlBu_r', vmin=vmin, vmax=vmax)
ax[1].set_title('AGRIF child  1/36 (3.06 km)')
fig.colorbar(m1, ax=ax, label='SST (C)')
fig.savefig('docs/img/agrif_sst.png', dpi=110)
```

![parent vs AGRIF child SST](img/agrif_sst.png)

*Left: the parent at 9.2 km renders the equatorial front through the child box as a smooth smear. Right: at 3.06 km the same water resolves into a cyclonic eddy spiral near 7.2°E, 0.5°N, a cold filament along São Tomé's eastern flank, and a warm/cold contrast at Príncipe's southern edge — none of which exist in the parent.*

!!! note
    Note the colour range is taken from the child, so the parent's panel saturates. This shows detail well but is not a like-for-like comparison. And this is one day from a Mercator cold start — much of the structure is initial adjustment, not spun-up dynamics.