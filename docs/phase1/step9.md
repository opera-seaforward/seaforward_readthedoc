Building a grid needs global **bathymetry** (sea-floor depth, ETOPO2) and a
**coastline** (GSHHS). CROCO distributes these as the *DATASETS_CROCOTOOLS*
package (several GB). If you already have the datasets, place it in the repository's `data/` directory. Otherwise, download it using the following commands:

```bash
# This can be postponed for later when it's needed. It also takes a lot of time; do it overnight. 
# Use -c option with wget -c to resume downloading a partially downloaded file instead of starting the download over from the beginning.
# this can take some time; do it overnight.

mkdir -p ${SEA_FORWARD_ROOT}/data
cd ${SEA_FORWARD_ROOT}/data

wget -c https://data-croco.ifremer.fr/DATASETS/DATASETS_CROCOTOOLS.tar.gz
tar -xzf DATASETS_CROCOTOOLS.tar.gz -C data/
```

!!! note
    This data is **large and never committed** to the repository (it is git-ignored). Each user downloads it once. `CROCO_DATA_ROOT` in `env.sh` points at `~/seaforward/data`, so as long as the datasets sit there, the tools find them.

Verify:

```bash
source ~/seaforward/env.sh
ls $CROCO_DATA_ROOT/DATASETS_CROCOTOOLS/Topo/etopo2.nc && echo "bathymetry OK"
```