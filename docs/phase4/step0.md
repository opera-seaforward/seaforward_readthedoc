```bash
source ~/seaforward/env.sh                 # shared paths + compilers + NetCDF
source ~/seaforward/hindcast/track.sh      # pick the HINDCAST track
conda activate seaforward
```

`hindcast/track.sh` points `CROCO_CONFIGS_ROOT` at `hindcast/configs` and
`CROCO_RUNS_ROOT` at `hindcast/scratch` — so everything you build lives under
`hindcast/`, fully separate from the forecast.

Set the region + hindcast variables:

```bash
export CONFIG_NAME=Canary_12
export CONFIG_DIR=${CROCO_CONFIGS_ROOT}/${CONFIG_NAME}   # hindcast/configs/Canary_12
export HCAST=${CROCO_RUNS_ROOT}/${CONFIG_NAME}           # hindcast/scratch/Canary_12
export CF=${HCAST}/CROCO_FILES

export LON_MIN=-22.0; export LON_MAX=-15.5      # grid box
export LAT_MIN=14.0;  export LAT_MAX=24.0
export RES=$(echo "1/12" | bc -l)
export EXTENTS=-23.5,-14.0,12.5,25.5            # GLORYS download box (grid + ~1.5°)
export ERA5_BOX="-22,-15.5,14,24"               # ERA5 grid box (a 2° margin is added)
export YORIG=1993                               # reanalysis time origin — NOT 2000

mkdir -p ${CONFIG_DIR} ${CF} \
         ${HCAST}/downloaded_data/GLORYS \
         ${HCAST}/downloaded_data/ERA5/for_croco
```

!!! warning
    **`Yorig=1993` for the hindcast.** GLORYS begins in 1993, at the start of the altimetry era, and the reanalysis convention is to count from there. Use **1993** consistently — in `make_ini_hindcast`, `make_bry_hindcast`, the ERA5 conversion, and every post-processing call. Mixing origins doesn't crash anything; it silently mislabels every timestamp.

!!! note
    **Two different domain strings.** `EXTENTS` is your grid box plus ~1.5° and goes to the GLORYS download. `ERA5_BOX` is the grid box itself — the ERA5 downloader adds its own 2° margin. Passing the wrong one to either gives too little data or too much.