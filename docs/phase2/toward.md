The run you just did is a complete forecast, but a *manual, cold-started* one — the
two simplifications flagged at the top of this chapter. An operational forecast
differs in two ways, and neither touches the model configuration you built.

### From a cold start to a spin-up

The single run you just did started the model directly from the global ocean,
interpolated onto your grid (`make_ini`). That is a **cold start**: the fine grid
is handed a coarse state and must spend the first hours or days of the run adjusting
to it — generating the eddies and fronts the global product is too coarse to
resolve, and letting the density field settle into balance with the bathymetry.
During that adjustment the forecast is least trustworthy.

An operational cycle keeps the cold-start adjustment out of the forecast by splitting
the run into two phases:

```text
        day:  −2      −1       0       +1  +2  +3  +4  +5
              │◄──── spin-up (2 days) ───►│
              │   ini + bry from the      │◄──────── forecast (5 days) ───────►│
              │   ANALYSIS (past→today)   │   ini = spin-up's restart at day 0
              │                           │   bry from the FORECAST (today→+5)
```

- **Spin-up — 2 days** (`today−2 → today`). A short run whose initial and boundary
  conditions come from the **analysis** part of the global product (the reconstructed
  recent past). Its only job is to let the regional model settle into its own
  dynamical balance and write a clean **restart** at `today`. You discard its output;
  you keep its restart.
- **Forecast — 5 days** (`today → today+5`). The forecast you actually use. Its
  **initial condition is the spin-up's restart** — an already-adjusted regional state,
  not a fresh cold interpolation — and its **boundaries come from the forecast** part
  of the global product, because this window is in the future.

So the two phases differ in where their data comes from: the spin-up is driven by
the analysis, the forecast by the forecast, and the forecast inherits the spin-up's
adjusted state as its starting point. A single download of today's global product
feeds both — it contains both the analysis and the forecast portions of the window.

`SPINUP_DAYS = 2` and `FCST_DAYS = 5` are the standard choice: two days is enough
for a regional domain to shed the cold-start imbalance, and five days is the useful
horizon of the global forecast that drives the boundaries.

### Running it operationally — the driver

The manual sequence you followed — download, prepare ini/bry/forcing, patch
`croco.in`, run — is wrapped in a single driver that does the whole two-phase cycle
for **today** without intervention, and can be put on a schedule. You don't rebuild
anything: it reuses the compiled model and grid you just made, and each cycle
refreshes only the boundaries and atmosphere from the latest global products. It is
set up per configuration by a short block of settings at the top.

**1. Set the driver's configuration block.** Open the driver and set it to match
the config you built. For Canary_12:

```bash
nano ~/seaforward/forecast/run_forecast_cycle.sh
```

```bash
CONFIG_NAME=Canary_12               # must match your config folder and cppdefs name
SPINUP_DAYS=2                       # the spin-up length
FCST_DAYS=5                         # the forecast length
YORIG=2000
EXTENTS="-23.5,-14.0,12.5,25.5"     # the SAME download box you used in Step 0
FIX_GFS_LON=1                       # 1 = west of Greenwich (apply GFS lon fix), 0 = east
```

!!! note
    These are the only lines you change for a new region. `CONFIG_NAME`, `EXTENTS`, and `FIX_GFS_LON` must match what you built in Phase 2 — otherwise the driver runs the wrong domain or crashes reading the weather. `FIX_GFS_LON` is the automatic version of the longitude fix from Step 5: `1` for a western-hemisphere box (negative longitudes), `0` for an eastern one.

**2. Launch the cycle.** From the `forecast/` directory, inside the environment:

```bash
cd ~/seaforward/forecast
source ~/seaforward/env.sh
conda activate seaforward
./run_forecast_cycle.sh 2>&1 | tee fcst_$(date -u +%Y%m%d).log
```

The driver then does the whole cycle automatically: downloads Mercator + GFS for
the entire `today−2 … today+5` window in one go, builds the spin-up ini+bry from
the **analysis**, runs the 2-day spin-up to a restart, builds the forecast bry from
the **forecast** part of the same file, copies the spin-up restart in as the
forecast's initial condition, and runs the 5-day forecast. You never hand-edit
`croco.in` or its dates — the driver patches them per phase.

**3. Collect the result.** Everything for one day lands in a dated folder:

```
forecast/model-runs/Canary_12/<date>/
├── spinup/     # the 2-day spin-up (produces croco_rst.nc)
└── fcst/       # the 5-day forecast — what you keep
    └── CROCO_FILES/
        ├── croco_his.nc     # forecast history (what you plot)
        └── croco_avg.nc     # forecast time-averages
```

The built config stays in `forecast/scratch/<CONFIG>/` (the workbench); each day's
output goes to `forecast/model-runs/<CONFIG>/<date>/` (the results you keep).

**4. Schedule it (optional).** To produce a fresh forecast every morning, add a
cron entry (`crontab -e`) — for 06:00 UTC:

```
0 6 * * *  /bin/bash -lc 'source ~/seaforward/env.sh && cd ~/seaforward/forecast && ./run_forecast_cycle.sh >> ~/seaforward/forecast/cron.log 2>&1'
```

Mercator and GFS for "today" must be published before your cron time; if a download
comes back empty, push the cron later.

### The optional physics — tides, nesting and rivers

The same driver carries three optional extensions as runtime flags, so you select
them at launch rather than keeping separate scripts:

```bash
./run_forecast_cycle.sh                        # plain: one grid, no tides, no rivers
./run_forecast_cycle.sh --tides                # add tidal forcing
./run_forecast_cycle.sh --rivers               # add river freshwater forcing
./run_forecast_cycle.sh --child 1way           # add an AGRIF nest (one-way)
./run_forecast_cycle.sh --child 2way           # add an AGRIF nest (two-way feedback)
./run_forecast_cycle.sh --child 1way --tides   # flags compose
```

The flags are independent and compose. **`--tides`** generates a tidal-forcing file
per cycle and switches the output to hourly history and daily averages (full setup in
**Phase 10**). **`--rivers`** stages the pre-built river climatology into each cycle
(**Phase 12**). **`--child 1way|2way`** runs the AGRIF nest described just above — the
parent and child together, the parent supplying the child's boundaries each step —
with `1way` passing information parent→child only and `2way` also feeding the child's
solution back to the parent.

Because tides, rivers and nesting are all compile-time features, each combination is a
pre-built binary the driver selects from the flags — but the daily cycle itself is
unchanged. This chapter's plain forecast is the base; the flags layer physics on top.

Full details of the operational driver — every stage, the settings, the output
layout — are in **Phase 3 (Running a Forecast)**.