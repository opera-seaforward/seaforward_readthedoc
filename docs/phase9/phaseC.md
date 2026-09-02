## C1 — what lives where

The split matters, and the naming is misleading: **`scratch/` is not disposable.**

```text
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

!!! note
    **Two configs, two directories.** `Agulhas_12` holds the standalone parent and its `croco_plain`; `Agulhas_AGRIF` holds the nested pair. The driver looks only in `scratch/${CONFIG_NAME}/`, so that variable decides which it uses — running `Agulhas_AGRIF` without `--child` would look for a `croco_plain` that B6 never builds.

## C2 — configure

The driver is `run_forecast_cycle.sh`, already in `forecast/`. Edit its settings block
for this config:

```bash
nano ~/seaforward/forecast/run_forecast_cycle.sh
```

```bash
SEA_FORWARD_ROOT=${HOME}/seaforward
CONFIG_NAME=Agulhas_AGRIF
COEF=3                                     # must match AGRIF_FixedGrids.in
SPINUP_DAYS=2
FCST_DAYS=5
YORIG=2000
EXTENTS="15.5,31.5,-41.5,-30.5"            # PARENT box + 1.5 deg each side
FIX_GFS_LON=0                              # eastern hemisphere -> skip the lon fix
TPXO_DIR="${SEA_FORWARD_ROOT}/data/DATASETS_CROCOTOOLS/TPXO10"
DT=300; NDTFAST=60; NINFO=1
```

Those are the same lines Phase 3 documents; only the values change. `TPXO_DIR` matters
only with `--tides`, which this chapter doesn't use.

There is no date here — the driver runs today's cycle unless you pass
`--date YYYY-MM-DD`.

```bash
bash -n ~/seaforward/forecast/run_forecast_cycle.sh && echo "syntax OK"
```

## C3 — run
```bash
cd ~/seaforward/forecast
./run_forecast_cycle.sh --child 1way 2>&1 | tee agrif_run.log
```

```text
============================================================
 SEA-FORWARD forecast
   config  : Agulhas_AGRIF
   child   : 1way  (3x)
   binary  : croco_1way
   run_date: 2026-07-17
   spin-up : 2026-07-15 -> 2026-07-17
   forecast: 2026-07-17 -> 2026-07-22
============================================================
```

The banner shows 2026-07-17 because that is when this run was made. Without `--date`
the driver uses today; for a past cycle:

```bash
./run_forecast_cycle.sh --child 1way --date YYYY-MM-DD
```

**Reaching that banner means the build phase is complete.** The driver checks the
binary, both grids, `AGRIF_FixedGrids.in`, `croco.in.1`, both param files, that `COEF`
matches the file, and that `DT % COEF == 0` — all before downloading anything.

Then:

```text
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

Without the `* COEF` on the output intervals the child writes three times as often as
the parent, and every comparison then needs interpolating.

## C4 — two-way

```bash
./run_forecast_cycle.sh --child 2way
```

Nothing else changes: same grids, same ICs, same `croco.in` and `croco.in.1`. One
binary swap — which is what makes it a clean experiment, and why both binaries are
worth the disk.

!!! note
    The Agulhas nest in this chapter was run **one-way only**. Phase 8 Step 8 shows what the two-way comparison looks like and how to read it; run it here the same way, keeping the one-way output as your baseline.