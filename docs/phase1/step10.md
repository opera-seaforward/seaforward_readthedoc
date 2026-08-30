Run this all-in-one check. Every line should succeed:

```bash
source ~/seaforward/env.sh
conda activate seaforward

echo "-- python env --";      python -c "import xarray, copernicusmarine, netCDF4; print('  OK')"
echo "-- CLI --";             python ${SEAFORWARD}/seaforward.py --help >/dev/null && echo "  OK"
echo "-- NetCDF stack --";    nf-config --prefix
echo "-- CROCO source --";    ls ${CROCO_MODEL_DIR}/OCEAN/cppdefs.h >/dev/null && echo "  OK"
echo "-- pytools tools --";   ls ${CROCO_PYTOOLS_DIR}/prepro/Modules/toolsf*.so >/dev/null && echo "  OK"
echo "-- bathymetry --";      ls ${CROCO_DATA_ROOT}/DATASETS_CROCOTOOLS/Topo/etopo2.nc >/dev/null && echo "  OK"
```

If the five checks print `OK` and `nf-config --prefix` shows
`~/seaforward/opt_seq`, your machine is fully set up.