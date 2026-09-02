## Before you run: check the GFS covers the window

The child has no spin-up of its own, so it reuses the **parent's** GFS forcing. Which
copy you point at matters, and getting it wrong stops the run partway.

There are two. The **per-cycle** copy the parent's forecast actually ran with, under
its run folder, and an older **staging** copy in scratch:

```
model-runs/<parent>/<date>/downloaded_data/GFS/for_croco/     <- use this one
scratch/<parent>/downloaded_data/GFS/for_croco/               <- may be shorter
```

They can cover different windows. The per-cycle copy spans the parent's full
forecast; a stale scratch copy may not. Point the child at a shorter GFS and it runs
fine until the forcing runs out, then stops:

```
ONLINE_GET_BULK - ERROR: The dataset for the year 9999 month 2 is missing
```

That is not a model failure — everything written up to that point is valid. The
forcing simply ended early.

Check a folder's coverage before running:

```bash
python3 -c "
import xarray as xr, glob
GFS_DIR = '${SEA_FORWARD_ROOT}/forecast/model-runs/Canary_12/20260712/downloaded_data/GFS/for_croco'
fs = sorted(glob.glob(GFS_DIR + '/*.nc'))
g  = xr.open_dataset(fs[0], decode_times=False)
tv = [v for v in ('bulk_time', 'time', 'tair_time') if v in g.variables][0]
t  = g[tv].values
print('GFS covers %.2f .. %.2f days' % (t.min(), t.max()))
"
```

!!! warning
    **Run the child for 4 days, not the parent's full 5.** The parent's boundary output and its GFS both span exactly `[today, today+5]`. A limited-area model cannot integrate to the very last instant of its forcing: to advance the final step *to* `today+5` it needs a record *beyond* it, and there isn't one. Pushing to the exact end gives `ERROR in get_bry: cannot read variable 'bry_time'` a few hours short. So `FDAYS=4` — comfortably inside the window, finishing cleanly at `MAIN: DONE`. A full 5-day child would need the parent run for 6.

## Run it

```bash
cd ${FCAST}
# all three inputs must exist
ls -lh CROCO_FILES/croco_grd.nc \
       CROCO_FILES/croco_ini_NEST_20260712_00.nc \
       CROCO_FILES/croco_bry_NEST_20260712_00.nc

./croco croco.in 2>&1 | tee run.log | tail -60
```

**What to watch:** it reads the grid, `GET_INITIAL` (child ini), `GET_BRY` (child
bry) and `ONLINE_BULK -- Read file` (GFS forcing), then a step table counting toward
2880. The columns are step number, model time, **kinetic energy**, and `trd`, an
error flag.

!!! check
    The kinetic-energy column stays small and steady — around 1.4×10⁻³, not growing — `trd = 0` on every row, and it ends with **`MAIN: DONE`**:

```bash
    ls -lh ${CF}/croco_his.nc
    tail -5 run.log
```

!!! warning
    **If it blows up** — `BLOW UP`, `NaN`, or kinetic energy climbing — at 1/25° this usually means the timestep is too large or the boundaries are reflecting. In order: turn the **sponge on** (`X_SPONGE 25000. 400.`) if you had it off; reduce `dt` to 120 with `NTIMES=3600`; then re-check the open boundaries match the mask. Sponge and timestep are run-time values, so no recompile is needed — re-stage `croco.in` and rerun.

## The first day is spin-up

The child starts from an **interpolated** initial condition — the parent's state,
smoothed onto the finer grid. That interpolation cannot contain the fine-scale
structure the child grid is *capable* of resolving: at T0 the child's ocean is
essentially a parent-resolution field sitting on a fine grid.

The child then has to **grow its own dynamics** — the sharper fronts, smaller eddies
and filaments that 1/25° can resolve but the smooth initial condition doesn't hold.
These develop over roughly the first day.

This is worth watching rather than waiting out: plot the child's SST or surface
vorticity on day 1, day 2 and day 3 and you will see filaments sharpen and multiply
as the fine grid spins up. The spin-up isn't a nuisance — it *is* the resolution
benefit appearing.

Two practical consequences:

- **When you validate against the parent** (next page), compare on **day 3–5**, not
  day 1. Day 1 still looks parent-like and understates what the child adds.
- **For a real forecast**, give the child a proper spin-up as the parent has one:
  start it two days before T0 so the fine structure is already developed when the
  forecast window begins. That needs the parent output to cover those extra days. For
  this manual example we keep it simple and treat the first day as visible spin-up.

## What you have now

A **nested 1/25°, 75-level child** that ran to completion, forced entirely by your
own 1/12° model:

```text
forecast/scratch/Canary_25/
├── croco                              # the compiled child
├── cppdefs.h param.h croco.in jobcomp # child config (also in configs/Canary_25)
├── run.log                            # proof it ran to MAIN: DONE
├── CROCO_FILES/
│   ├── croco_grd.nc                   # 1/25° grid (150×238)
│   ├── crocotools_param.py            # N=75 pre-processing params
│   ├── croco_ini_NEST_20260712_00.nc  # child initial (75 levels)
│   ├── croco_bry_NEST_20260712_00.nc  # child boundaries (75 levels)
│   └── croco_his.nc                   # the nested 1/25° output
└── downloaded_data/PARENT/
    └── parent_20260712.nc             # the 1/12° output, in Mercator format
```