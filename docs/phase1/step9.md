Building a grid needs global **bathymetry** (sea-floor depth, ETOPO2) and a
**coastline** (GSHHS). CROCO distributes these as the *DATASETS_CROCOTOOLS*
package (several GB). If you already have the datasets, place them in the
repository's `data/` directory. Otherwise download them:

```bash
mkdir -p ${SEA_FORWARD_ROOT}/data
cd ${SEA_FORWARD_ROOT}/data

wget -c https://data-croco.ifremer.fr/DATASETS/DATASETS_CROCOTOOLS.tar.gz
tar -xzf DATASETS_CROCOTOOLS.tar.gz
```

!!! note
    **Large download — plan for it.** The package is several GB and can take hours; running it overnight is sensible. The `-c` flag lets `wget` resume a partial download rather than starting over, so an interrupted transfer costs nothing. You can also postpone this step until you first build a grid (Phase 2).

!!! note
    This data is **large and never committed** to the repository (it is git-ignored). Each user downloads it once. `CROCO_DATA_ROOT` in `env.sh` points at `~/seaforward/data`, so as long as the datasets sit there, the tools find them.

Verify:

```bash
source ~/seaforward/env.sh
ls $CROCO_DATA_ROOT/DATASETS_CROCOTOOLS/Topo/etopo2.nc && echo "bathymetry OK"
```