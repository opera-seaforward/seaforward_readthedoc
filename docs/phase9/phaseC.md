## C1 — what lives where

The split matters, and the naming is misleading: **`scratch/` is not disposable.**

```
scratch/Agulhas_AGRIF/                    BUILT ONCE, permanent
├── croco_1way, croco_2way                the binaries
├── croco.in, croco.in.1                  templates (driver copies + patches)
├── cppdefs.h, param.h, jobcomp
├── AGRIF_FixedGrids.in
└── CROCO_FILES/
    ├── croco_grd.nc, croco_grd.nc.1
    ├── crocotools_param.py
    └── crocotools_param_child.py

model-runs/Agulhas_AGRIF/20260717_1way/   PER CYCLE, disposable
├── downloaded_data/
├── gen_spinup/, gen_spinup_child/
├── spinup/    <- staged copies + the run
└── fcst/      <- staged copies + the run
```

The driver never writes into `scratch/`; it copies out of it. Delete `model-runs/`
freely. Delete `scratch/` and you rebuild the grid and recompile.

## C2 — configure

```bash
cp run_forecast_agrif.sh ~/seaforward/forecast/
chmod +x ~/seaforward/forecast/run_forecast_agrif.sh
nano ~/seaforward/forecast/run_forecast_agrif.sh
```

```bash
CONFIG_NAME=Agulhas_AGRIF
COEF=3                                  # must match AGRIF_FixedGrids.in
SPINUP_DAYS=2
FCST_DAYS=5
EXTENTS="15.5,31.5,-41.5,-30.5"         # PARENT box + 1.5 deg each side
FIX_GFS_LON=0                           # eastern hemisphere -> skip the lon fix
```

!!! important
    **`env.sh` vs `config.sh`.** Older configs (IGOG_AGRIF) ship a per-config `config.sh`; Phase-2 configs don't — `env.sh` carries the compiler and `opt_seq` NetCDF paths. If your driver still says `source config.sh`, change both run lines to `source "${SEA_FORWARD_ROOT}/env.sh"` and drop `config.sh` from `stage_agrif_rundir`.

```bash
bash -n ~/seaforward/forecast/run_forecast_agrif.sh && echo "syntax OK"
grep -n "env.sh" ~/seaforward/forecast/run_forecast_agrif.sh    # want 2 hits
```

## C3 — run

```bash
cd ~/seaforward/forecast
./run_forecast_agrif.sh --mode 1way 2>&1 | tee agrif_run.log
```

```
============================================================
 SEA-FORWARD AGRIF forecast
   config  : Agulhas_AGRIF
   mode    : 1way   (binary: croco_1way)
   refine  : 3x
   run_date: 2026-07-17
   spin-up : 2026-07-15 -> 2026-07-17  (2 d)
   forecast: 2026-07-17 -> 2026-07-22  (5 d)
============================================================
```

**Reaching that banner means the build phase is complete** — it checks both binaries,
both grids, `AGRIF_FixedGrids.in`, `croco.in.1`, both param files, that `COEF` matches
the file, and that `DT % COEF == 0`, all before downloading anything.

Then:

```
[1/6] download Mercator + GFS          both grids share it
[2/6] GFS -> online forcing            both grids read the same files
[3/6] parent ini+bry, child ini        then VALIDATES both
[4/6] spin-up 2 days, BOTH grids       wants 2x MAIN: DONE
[5/6] forecast bry; ICs = both restarts
[6/6] forecast 5 days, BOTH grids
```

### Why the spin-up handoff is free

AGRIF integrates both grids in one executable, so the spin-up produces **`croco_rst.nc`
and `croco_rst.nc.1`**. The forecast restarts both. The child needs no forecast IC built
at all — its restart already carries the model clock.

### The child's timing, in the driver

```bash
DT_CHD=$(( DT / COEF ))          # 100 -- AGRIF does NOT do this for you
NRST_CHD=$(( NRST * COEF ))      # child steps are 3x more frequent, so scale
NWRT_CHD=$(( NWRT * COEF ))      # the output intervals to write at the same TIMES
NAVG_CHD=$(( NAVG * COEF ))
```
and in `patch_croco_in_child`:
```bash
local ntimes=$(( days * 86400 / DT ))     # the PARENT's ntimes, deliberately
```

Without the `* COEF` on the output intervals you get 5 parent records and 13 child
records for the same period — which is what happened on IGOG's first run.

## C4 — two-way

```bash
./run_forecast_agrif.sh --mode 2way
```

Nothing else changes: same grids, same ICs, same `croco.in`. One binary swap. That's
what makes it a clean experiment — and why the two binaries are worth the disk.