`forecast/run_forecast_cycle.sh` runs one complete cycle for **today**, ready to be
scheduled. The manual run above proves the configuration; this is how you'd actually
operate it.

## B.1 — What the driver does

The driver replaces the whole manual sequence — download, prepare, patch `croco.in`,
run — with one command that produces today's forecast in two phases and files the
result.

```bash
cd ~/seaforward/forecast
./run_forecast_cycle.sh
```

**One data download, two phases.** It fetches Mercator and GFS once for the whole
`today−2 … today+5` window; both phases read from that same download, each taking the
part it needs. The log numbers the stages:

| stage | what it does |
|---|---|
| 1 | Downloads Mercator + GFS for the whole window. |
| 2 | Reshapes GFS into online-forcing files, applying the longitude fix if `FIX_GFS_LON=1` (and builds tidal forcing, if `--tides`). |
| 3 | Builds the spin-up's ini + bry from the *analysis* part of the download. |
| 4 | Runs the 2-day spin-up, writing a restart. |
| 5 | Builds the forecast bry from the *forecast* part, and stages the spin-up restart as the forecast's initial condition. |
| 6 | Runs the 5-day forecast and files the output. |

`croco.in` is patched automatically for each phase — the timestep count, the initial
and boundary filenames, the online-forcing block. You never hand-edit it.

By default the driver runs **today's** cycle. To rerun a past one:

```bash
./run_forecast_cycle.sh --date 2026-07-11
```

## B.2 — Why two phases

The spin-up exists so the forecast doesn't start cold. A regional model handed a
coarse interpolated state spends its first hours or days adjusting: generating the
eddies and fronts the global product cannot resolve, and letting the density field
settle against the bathymetry. Doing that *inside* the forecast wastes the part of the
run you care about.

So the spin-up absorbs it. Two days from the analysis, output discarded, restart kept
— and the forecast begins from that adjusted state instead.

The two phases also differ in **where their ocean data comes from**: the spin-up is
driven by the analysis (the reconstructed recent past), the forecast by the forecast
portion of the same file. A single download contains both.

## B.3 — Optional physics, and the binary it needs

Three extensions are runtime flags:

```bash
./run_forecast_cycle.sh                          # plain
./run_forecast_cycle.sh --tides                  # tidal forcing
./run_forecast_cycle.sh --rivers                 # river freshwater forcing
./run_forecast_cycle.sh --child 1way             # AGRIF nest, one-way
./run_forecast_cycle.sh --child 2way             # AGRIF nest, two-way feedback
./run_forecast_cycle.sh --child 1way --tides     # flags compose
```

But AGRIF, tides and rivers are **compile-time** switches in CROCO, not run-time
options. Each combination is therefore a **separate binary**, and the driver picks one
by name from the flags you passed.

### How the name is built

```
croco_ + [ plain | 1way | 2way ] + [ _tides ] + [ _rivers ]
```

The order is fixed:

| command | binary the driver looks for |
|---|---|
| (no flags) | `croco_plain` |
| `--tides` | `croco_plain_tides` |
| `--rivers` | `croco_plain_rivers` |
| `--tides --rivers` | `croco_plain_tides_rivers` |
| `--child 1way` | `croco_1way` |
| `--child 1way --tides` | `croco_1way_tides` |
| `--child 1way --rivers` | `croco_1way_rivers` |
| `--child 1way --tides --rivers` | `croco_1way_tides_rivers` |
| `--child 2way` | `croco_2way` |
| `--child 2way --tides` | `croco_2way_tides` |
| `--child 2way --rivers` | `croco_2way_rivers` |
| `--child 2way --tides --rivers` | `croco_2way_tides_rivers` |

All of them live in `forecast/scratch/<CONFIG>/`. You only build the ones you intend
to use.

### The switches for each axis

| axis | `cppdefs.h` |
|---|---|
| no nest | `# undef AGRIF` |
| one-way nest | `# define AGRIF`, `# undef AGRIF_2WAY` |
| two-way nest | `# define AGRIF`, `# define AGRIF_2WAY` |
| tides | `# define TIDES`, `SSH_TIDES`, `UV_TIDES`, `POT_TIDES` (leave `TIDES_MAS` undef) |
| rivers | `# define PSOURCE`, `# define PSOURCE_NCFILE` (leave `PSOURCE_NCFILE_TS` undef) |

!!! note
    **Tides and rivers need a data file as well as a binary.** The switches only tell CROCO to read one. The tide file `croco_frc.nc` is generated per cycle by the driver from the TPXO atlas — and on a nested run the child needs its own, `croco_frc.nc.1`, because tidal forcing has to be defined on each grid. The river file `croco_runoff.nc` is built once per region and staged each cycle.

### Building them

Every build is the same three steps: set the switches in `cppdefs.h`, compile, rename
the result. `jobcomp` always produces a file called `croco`, and each build overwrites
the last — so **rename before building the next**.

**The plain binary — do this one first.** Phase 2 already built it; it just needs the
name:

```bash
cd ~/seaforward/forecast/scratch/Canary_12
cp croco croco_plain
```

!!! warning
    **Without this rename the driver fails immediately**, because Phase 2's `jobcomp` produces `croco` while the driver looks for `croco_plain`:
    ```
    ERROR: binary not found: .../scratch/Canary_12/croco_plain
      (child=none, tides=0) needs its own build.
    ```
    The error also prints the CPP switches for whichever combination it couldn't find.

**A tides build:**

```bash
cd ~/seaforward/forecast/scratch/Canary_12
nano cppdefs.h                    # define TIDES SSH_TIDES UV_TIDES POT_TIDES
conda deactivate
source ~/seaforward/env.sh
./jobcomp
cp croco croco_plain_tides        # rename before the next build
```

**A rivers build:**

```bash
nano cppdefs.h                    # define PSOURCE and PSOURCE_NCFILE
                                  # leave PSOURCE_NCFILE_TS undef
./jobcomp
cp croco croco_plain_rivers
```

**A one-way nest with tides:**

```bash
nano cppdefs.h                    # define AGRIF (leave AGRIF_2WAY undef), keep the TIDES block
./jobcomp
cp croco croco_1way_tides
```

**A two-way nest:**

```bash
nano cppdefs.h                    # define AGRIF and AGRIF_2WAY
./jobcomp
cp croco croco_2way
```

Check what you have at any point:

```bash
ls ~/seaforward/forecast/scratch/Canary_12/croco_*
```

Full setup for each: **Phase 10** for tides, **Phase 11** for rivers, **Phase 8** for
AGRIF — those chapters cover the data files each one also needs, not just the switches.

## B.4 — Settings at the top of the driver

!!! warning
    **The driver is configured for `Canary_12` by default.** The settings block names that config, its download box and its hemisphere flag. **Every time you build a new region in Phase 2, update these to match**, or the driver runs Canary_12 instead of yours.

Find the settings block:

```bash
grep -n "^CONFIG_NAME=\|^EXTENTS=\|^FIX_GFS_LON=\|^COEF=" \
     ~/seaforward/forecast/run_forecast_cycle.sh
```

```
58:CONFIG_NAME=Canary_12
59:COEF=3
63:EXTENTS="-23.5,-14.0,12.5,25.5"
64:FIX_GFS_LON=1
```

Open the file there — `nano +58` puts the cursor on the first of them:

```bash
nano +58 ~/seaforward/forecast/run_forecast_cycle.sh
```

The whole block:

```bash
SEA_FORWARD_ROOT=${HOME}/seaforward
CONFIG_NAME=Canary_12               # must match your config folder and cppdefs name
COEF=3                              # AGRIF refinement ratio, only used with --child
SPINUP_DAYS=2                       # spin-up length
FCST_DAYS=5                         # forecast length
YORIG=2000
EXTENTS="-23.5,-14.0,12.5,25.5"     # the SAME download box you used in Phase 2 Step 0
FIX_GFS_LON=1                       # 1 = box west of Greenwich, 0 = east
TPXO_DIR="${SEA_FORWARD_ROOT}/data/DATASETS_CROCOTOOLS/TPXO10"
DT=300; NDTFAST=60; NINFO=1         # timestep settings, as in croco.in
```

What to change for a new region:

- **`CONFIG_NAME`** — must match the folder under `forecast/scratch/` and the name you
  set in `cppdefs.h`.
- **`EXTENTS`** — your grid box plus about 1.5° of margin, the same string you used in
  Phase 2.
- **`FIX_GFS_LON`** — `1` if your box has negative longitudes, `0` if it is entirely
  east of Greenwich. This is the automatic version of the longitude fix you did by hand
  in Phase 2 Step 5.

`SPINUP_DAYS` and `FCST_DAYS` rarely change: two days is enough for a regional domain
to shed the cold-start imbalance, and five is the useful horizon of the global forecast
driving the boundaries. `COEF` only matters with `--child`, and `DT`/`NDTFAST` should
match what you set in `croco.in`.

!!! tip
    **Copy the driver per region.** Rather than editing one script back and forth, keep a copy per configuration — `run_forecast_Canary_12.sh`, `run_forecast_IGOG_12.sh` — each with its own settings block. Then a scheduled job can run several regions without conflict.

## B.5 — Running it

```bash
cd ~/seaforward/forecast
source ~/seaforward/env.sh
conda activate seaforward
./run_forecast_cycle.sh 2>&1 | tee fcst_$(date -u +%Y%m%d).log
```

The driver prints a header showing the config, the child mode, whether tides are on,
which binary it picked and the two date windows — worth reading before it starts, as a
last check that it is running what you intended.

!!! check
    Two `MAIN: DONE` lines in the log — one for the spin-up, one for the forecast — and a dated folder under `model-runs/`.

**If it takes a long time,** run it detached so a closed terminal doesn't stop it:

```bash
nohup ./run_forecast_cycle.sh > fcst_$(date -u +%Y%m%d).log 2>&1 &
tail -f fcst_$(date -u +%Y%m%d).log        # Ctrl-C stops watching, not the run
```

## B.6 — Where the output goes

```
forecast/model-runs/Canary_12/<date>/
├── spinup/
│   └── CROCO_FILES/
│       └── croco_rst.nc     # the restart the forecast starts from
└── fcst/
    └── CROCO_FILES/
        ├── croco_his.nc     # forecast history — what you plot
        └── croco_avg.nc     # forecast time-averages
```

Two roots, two jobs: `forecast/scratch/<CONFIG>/` is the workbench, holding the
compiled binaries and the grid, reused every cycle.
`forecast/model-runs/<CONFIG>/<date>/` holds the results you keep, one folder per day.

## B.7 — Scheduling it

To produce a fresh forecast every morning, add a cron entry with `crontab -e`. For
06:00 UTC:

```
0 6 * * *  /bin/bash -lc 'source ~/seaforward/env.sh && cd ~/seaforward/forecast && ./run_forecast_cycle.sh >> ~/seaforward/forecast/cron.log 2>&1'
```

The `-lc` matters: cron runs with a minimal environment, so the shell has to be a login
shell for conda and the paths to resolve.

!!! warning
    **Check the data is published before your cron time.** Mercator and GFS for "today" appear at different hours. If a download returns nothing, the cycle fails at stage 1 — move the cron later rather than retrying.