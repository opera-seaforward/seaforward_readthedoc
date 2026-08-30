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
- `track.sh` sets the **per-track** variables — where configs and runs live. The
  forecast track gives `CROCO_CONFIGS_ROOT=…/forecast/configs` and
  `CROCO_RUNS_ROOT=…/forecast/scratch`; the hindcast track points at
  `hindcast/` instead. This document uses the forecast track throughout.

Now set **your region** (the only numbers you change for a different region):

```bash
export CONFIG_NAME=Canary_12                     # your region's name (used everywhere)
export LON_MIN=-22.0; export LON_MAX=-15.5       # west/east edges of your box
export LAT_MIN=14.0;  export LAT_MAX=24.0        # south/north edges
export RES=$(echo "1/12" | bc -l)                # grid spacing: 1/12° (~9 km)
export EXTENTS=-23.5,-14.0,12.5,25.5             # DOWNLOAD box = your box + ~1.5° margin
export HDAYS=2; export FDAYS=5                   # 2 days spin-up + 5 days forecast
export YORIG=2000                                # time reference year (leave at 2000)

# derived paths (config recipe vs run folder)
export CONFIG_DIR=${CROCO_CONFIGS_ROOT}/${CONFIG_NAME}   # the recipe: config files you edit
export FCAST=${CROCO_RUNS_ROOT}/${CONFIG_NAME}           # the workbench: grid, data, binary
export CF=${FCAST}/CROCO_FILES                           # where the grid and forcing files go

# create the folders those paths name
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

**Why `bc -l`?** It computes `1/12` at full precision, so you never hand-round it
to `0.0833` — the exact value is what makes the grid come out to the expected
point count.

!!! warning
    **The region variables live only in this terminal.** The scripts below read them; if one is missing, a tool guesses a wrong path and stops. If you open a fresh terminal later, re-run the whole Step 0 block first — the ritual **and** the region variables.