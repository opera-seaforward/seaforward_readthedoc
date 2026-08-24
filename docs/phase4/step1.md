The hindcast builds its **own** grid so the track is self-contained — even though
for the same region it comes out identical to the forecast's. This is Phase 2
Steps 1–2, run under the hindcast track:

```bash
cd ${SEAFORWARD}/config
python3 make_grid_config.py "${CONFIG_NAME}" \
        ${LON_MIN} ${LON_MAX} ${LAT_MIN} ${LAT_MAX} ${RES} ${RES}

cd ${CROCO_PYTOOLS_DIR}/prepro
python3 make_grid.py ${CONFIG_DIR}/grid.ini 2>&1 | tail -20

ncdump -h ${CF}/croco_grd.nc | grep -E "xi_rho|eta_rho"
```

!!! check
    ✅ `xi_rho = 81`, `eta_rho = 123` (→ `LLm0=79, MMm0=121`), written to `hindcast/scratch/Canary_12/CROCO_FILES/croco_grd.nc`.