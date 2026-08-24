You **run** this (it's not a file to edit), but understand it: these commands
tell every tool where SEA-FORWARD lives, pick your track, step into the Python
environment, and set the region you're building.

Open a terminal and run the three-line **session ritual**:

```bash
source ~/seaforward/env.sh                 # shared paths + compilers + NetCDF
source ~/seaforward/forecast/track.sh      # pick the FORECAST track
conda activate seaforward                  # the Python tools
```

- `env.sh` sets the shared variables: `SEA_FORWARD_ROOT=~/seaforward`,
  `CROCO_MODEL_DIR=…/code/croco`, `CROCO_PYTOOLS_DIR=…/code/croco_pytools`,
  `CROCO_DATA_ROOT=…/data`, `SEAFORWARD=…/sftools`, the compilers, and the
  `opt_seq` NetCDF paths.
- `track.sh` sets the **per-track** variables — where configs and runs live:
  - `forecast/track.sh` → `CROCO_CONFIGS_ROOT=…/forecast/configs`,
    `CROCO_RUNS_ROOT=…/forecast/scratch`

!!! important
    **Why a track?** Sourcing `forecast/track.sh` sets the paths for the forecast workflow — configs under `forecast/configs`, runs under `forecast/scratch`. This document uses the **forecast** track throughout.

Now set **your region** (the only numbers you change for a different region):

```bash
export CONFIG_NAME=Canary_12
export LON_MIN=-22.0; export LON_MAX=-15.5      # west/east edges of your box
export LAT_MIN=14.0;  export LAT_MAX=24.0       # south/north edges
export RES=$(echo "1/12" | bc -l)               # grid spacing: 1/12° (~9 km)
export EXTENTS=-23.5,-14.0,12.5,25.5            # DOWNLOAD box = your box + ~1.5° margin
export HDAYS=2; export FDAYS=5                   # 2 days spin-up + 5 days forecast
export YORIG=2000                                # time reference year (leave at 2000)

# derived paths (config recipe vs run folder)
export CONFIG_DIR=${CROCO_CONFIGS_ROOT}/${CONFIG_NAME}   # forecast/configs/Canary_12
export FCAST=${CROCO_RUNS_ROOT}/${CONFIG_NAME}           # forecast/scratch/Canary_12
export CF=${FCAST}/CROCO_FILES
mkdir -p ${CONFIG_DIR} ${CF} \
         ${FCAST}/downloaded_data/MERCATOR \
         ${FCAST}/downloaded_data/GFS/for_croco
echo "Building ${CONFIG_NAME}: lon ${LON_MIN}..${LON_MAX}, lat ${LAT_MIN}..${LAT_MAX}"
```

**Two folders, two jobs.** `CONFIG_DIR` (`forecast/configs/Canary_12`) holds the
**recipe** — the config files you edit, kept for the future. `FCAST`
(`forecast/scratch/Canary_12`) is the **workbench** — where you build the grid,
generate data, compile, and test.

**Why the two boxes?** Your *grid box* (`LON_MIN..LAT_MAX`) is your model's
domain. The *download box* (`EXTENTS`) is ~1.5° bigger on every side, because the
tools that interpolate global data onto your grid need data slightly *beyond*
your grid edges. If the download box is too tight, `make_ini`/`make_bry` fail
with "extents not sufficient."

!!! warning 
    ⚠️ **WATCH — the region variables live only in this terminal.** The scripts below read them; if one is missing, a tool guesses a wrong path and stops. If you open a fresh terminal later, re-run the whole Step 0 block first (the ritual **and** the region variables).

!!! important
    **`bc -l` for the resolution.** We compute `1/12` with `bc -l` so you never hand-round it to `0.0833`. The full-precision value is what makes the grid come out to the expected point count.