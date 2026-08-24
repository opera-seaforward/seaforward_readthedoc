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
export EXTENTS=-23.5,-14.0,12.5,25.5           # GLORYS download box (grid + ~1.5°)
export GFS_BOX="-22,-15.5,14,24"              # GFS grid box (a 2° margin is added)
export YORIG=1993                               # reanalysis time origin — NOT 2000

mkdir -p ${CONFIG_DIR} ${CF} \
         ${HCAST}/downloaded_data/GLORYS \
         ${HCAST}/downloaded_data/GFS/for_croco
```

!!! warning
    ⚠️ **`Yorig=1993` for the hindcast.** GLORYS and GFS use 1993 as the time origin (the start of the altimetry era the reanalysis covers). Use **1993** consistently across the ini, bry, GFS convert, and the run — mixing origins corrupts the time axis.
