`forecast/run_forecast_cycle.sh` runs one complete cycle for **today**, ready to
run daily (e.g. from cron). It reuses the compiled model and grid from Phase 2
and handles everything else.

### B.1 The two-phase cycle (the picture)

Each daily run has two phases on the model clock:

```
        day:  -2      -1       0       +1  +2  +3  +4  +5
              │───spin-up───►│
              │  (2 days,     │◄──────forecast (5 days)──────►│
              │   ini+bry     │   ini = spin-up END (restart)
              │   from        │   bry = FORECAST part
              │   ANALYSIS)   │   of the anfc
```

The driver's key numbers are **`SPINUP_DAYS=2`** and **`FCST_DAYS=5`**. Your
documentation diagram shows exactly this: a 2-day spin-up bar (ini+bry from the
analysis) feeding a 5-day forecast bar whose ini is the spin-up's end and whose
bry is the forecast part of the product.

- **Spin-up — 2 days.** From `today − 2` to `today`, with its initial condition
  (**ini**) and boundary conditions (**bry**) built from the **analysis** part of
  the global ocean product (GLO12 analysis via Mercator anfc). Running these 2
  days lets the fine grid settle into balance and write a clean restart at
  `today`.
- **Forecast — 5 days.** From `today` to `today + 5`:
  - **ini** = the **spin-up's end** (the restart the spin-up wrote at `today`) —
    not the global data again.
  - **bry** = the **forecast** part of the global product (the future portion of
    the anfc), because this window is in the future and its edges must come from
    the forecast, not the analysis.

So the two phases differ in where their boundaries come from: the spin-up's boundaries are from the Global Forecasting System (GFS), the forecast's boundaries are from the spin-up analysis. The forecast's initial condition is the spin-up restart. This is better illustrated by the figure below.

![Phase 3](../img/forecasting_scheme.png)

### B.2 One download feeds both phases

The driver downloads today's ocean + weather **once** — a single Mercator anfc
file that contains **both** the analysis (past → `today`) and the forecast
(`today` → `today+5`) parts, covering the whole `today−2 … today+5` window. The
spin-up reads the **analysis** records for its ini+bry; the forecast reads the
**forecast** records for its bry. The model clock selects the right records from
that one file — no second download.

### B.3 What the driver reuses from Phase 2

It expects the compiled model and grid to exist in
`forecast/scratch/<CONFIG>/` (exactly what Phase 2 produced):

```bash
source ~/seaforward/env.sh
source ~/seaforward/forecast/track.sh
export CONFIG_NAME=Canary_12
ls ${CROCO_RUNS_ROOT}/${CONFIG_NAME}/croco \
   ${CROCO_RUNS_ROOT}/${CONFIG_NAME}/CROCO_FILES/croco_grd.nc \
   ${CROCO_RUNS_ROOT}/${CONFIG_NAME}/CROCO_FILES/crocotools_param.py \
   ${CROCO_RUNS_ROOT}/${CONFIG_NAME}/croco.in
```

### B.4 Settings at the top of the driver

!!! warning
    ⚠️ **The driver ships set up for `Canary_12`.** The reference `run_forecast_cycle.sh` has the Canary_12 config name and its download box baked in. **Every time you build a new region in Phase 2, you must update these settings to match that config**, or the driver will try to run Canary_12 instead of yours. What to change for a new region:
     - `CONFIG_NAME` → your config's exact name (must match the folder in `forecast/scratch/` and `forecast/configs/`, and the `# define <NAME>` in `cppdefs.h`).
     - `EXTENTS` → the **same download box** you used in Phase 2 Step 0 for that region.
     - `FIX_GFS_LON` → `1` if the region is west of Greenwich, else `0`.
     - `SPINUP_DAYS` / `FCST_DAYS` → only if you want a different cycle length.

!!! note
    A clean way to keep this straight: copy the driver per region (e.g.`run_forecast_<CONFIG>.sh`) with that config's settings, so each region has its own ready-to-run driver.

Open `forecast/run_forecast_cycle.sh` and check the CONFIG block:

```bash
CONFIG_NAME=Canary_12               # <-- change to YOUR config name
SPINUP_DAYS=2                       # the 2-day spin-up
FCST_DAYS=5                         # the 5-day forecast
YORIG=2000
EXTENTS="-23.5,-14.0,12.5,25.5"     # <-- change to YOUR download box (same as Phase 2)
FIX_GFS_LON=1                       # GFS longitude fix: 1 = apply, 0 = skip
```

**About `FIX_GFS_LON`.** This is the automatic version of the Phase 2 Step 6
longitude fix. GFS labels longitude 0–360; CROCO uses −180…180. West of Greenwich
these disagree and the model crashes reading the weather, so the forcing must be
converted. Set it by where your region is:

- `FIX_GFS_LON=1` → **western hemisphere** (your box has negative longitudes —
  Canary, West Africa, the Americas). Applies the conversion.
- `FIX_GFS_LON=0` → **eastern hemisphere** (your box is all positive longitudes —
  Mediterranean, East Africa, Asia). No conversion needed.

Canary is at 22°W–15.5°W, so the provided driver ships with `FIX_GFS_LON=1`. If
unsure, the `covers?` check from Phase 2 Step 6 tells you: `covers? False` with
big forcing numbers (like 336–346) means you need `1`.

These must agree with the config you built in Phase 2. The example values shown
are for the provided **Canary_12** build; a different region overrides all of
them.

Paths — **inputs read from `scratch`, outputs written to `model-runs`**:

```bash
export CROCO_CONFIGS_ROOT="${SEA_FORWARD_ROOT}/forecast/configs"
export CROCO_RUNS_ROOT="${SEA_FORWARD_ROOT}/forecast/scratch"       # binary + grid live here
OUTPUT_ROOT="${SEA_FORWARD_ROOT}/forecast/model-runs/${CONFIG_NAME}"
CYCLE_ROOT="${OUTPUT_ROOT}/${RUN_TAG}"                              # one folder per day
```

### B.5 What it does, stage by stage

The driver's `patch_croco_in` sets each phase's settings **automatically** —
including the **dates** (`start_date`/`end_date`): the spin-up gets
`today−2 → today`, the forecast gets `today → today+5`. It also sets
`time_stepping` (phase days ÷ dt), the `initial` block, `boundary`, and the online
forcing block. **You never hand-edit `croco.in` — or its dates — for an
operational run.** Its six stages:

1. **Download** the Mercator ocean + GFS weather for the **whole window**
   (`today−2 … today+5`) in one go — `--hdays 2 --fdays 5` pull that full span,
   not just today.
2. **Reformat GFS** into online forcing over that window (and apply the longitude
   fix if `FIX_GFS_LON=1`).
3. **Build spin-up ini + bry** — `make_ini` and `make_bry` from the **analysis**
   part of the anfc file, for the 2-day spin-up window.
4. **Run the spin-up** (2 days) → writes a restart at `today`:
   `${SPIN_DIR}/CROCO_FILES/croco_rst.nc`. This restart holds the fine grid's
   balanced ocean state at `today` and the model clock — it becomes the
   forecast's starting point.
5. **Build forecast bry** — `make_bry` from the **forecast** part of the same
   anfc file, spanning the 5-day forecast window. No new ini is built: instead
   the driver copies the spin-up restart in as the forecast's initial condition —
   `cp ${SPIN_DIR}/CROCO_FILES/croco_rst.nc  ${FCST_DIR}/CROCO_FILES/croco_ini.nc`
   — and patches the forecast `croco.in` to read it (`NRREC=1`, `initial:` →
   `CROCO_FILES/croco_ini.nc`). Because the restart carries the model clock, the
   run continues cleanly from `today`.
6. **Run the forecast** (5 days) → writes the outputs you keep:
   `${FCST_DIR}/CROCO_FILES/croco_his.nc` (history, e.g. every 6 h) and
   `croco_avg.nc` (time-averaged fields), plus its own `croco_rst.nc`.

### B.6 Run it

```bash
cd ~/seaforward/forecast
source ~/seaforward/env.sh
conda activate seaforward
./run_forecast_cycle.sh 2>&1 | tee fcst_$(date -u +%Y%m%d).log
```

### B.7 Where the results go

Everything for one day lives in one dated folder under `model-runs`:

```
forecast/model-runs/Canary_12/20260711/
├── spinup/            # the 2-day spin-up run (produces croco_rst.nc)
├── fcst/              # the 5-day forecast run
│   └── CROCO_FILES/
│       ├── croco_his.nc     # forecast history  (what you plot)
│       └── croco_avg.nc     # forecast averages
├── downloaded_data/   # Mercator + GFS for the whole window (today−2…today+5) + forcing
├── gen_spinup/        # where the spin-up ini/bry were generated
└── gen_fcst/          # where the forecast bry was generated
```

The forecast you care about is `fcst/CROCO_FILES/croco_his.nc` (and
`croco_avg.nc`).

!!! note
    **scratch vs model-runs.** The built config (binary, grid) stays in `forecast/scratch/<CONFIG>/`; each day's **output** is written to `forecast/model-runs/<CONFIG>/<date>/`. Scratch is the workbench; model-runs holds the results you keep.

### B.8 Automating (optional)

To run daily at, say, 06:00 UTC, add a cron entry (`crontab -e`):

```
0 6 * * *  /bin/bash -lc 'source ~/seaforward/env.sh && cd ~/seaforward/forecast && ./run_forecast_cycle.sh >> ~/seaforward/forecast/cron.log 2>&1'
```

!!! note
    **Data availability:** Mercator analysis-forecast and GFS for "today" must be published before your cron time. If a download comes back empty, push the cron later.