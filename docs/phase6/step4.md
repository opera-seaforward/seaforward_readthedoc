Now the **standard Phase-2 ini/bry step** (Step 5d/5e), but the input is the
converted parent instead of a Mercator download.

```bash
cd ~/seaforward/sftools
export PARENT=${FCAST}/downloaded_data/PARENT/parent_20260712.nc

# initial condition
python seaforward.py make_ini \
    --input_file ${PARENT} --output_dir ${CF} \
    --run_date "2026-07-12 00:00:00" --hdays 0 --Yorig 2000

# boundary conditions
python seaforward.py make_bry \
    --input_file ${PARENT} --output_dir ${CF} \
    --run_date "2026-07-12 00:00:00" --hdays 0 --fdays 5 --Yorig 2000

ls -lh ${CF}/croco_ini_NEST_20260712*.nc ${CF}/croco_bry_NEST_20260712*.nc
```

**What / Why:** identical to Phase 2, except `--input_file` is the converted
parent and `--Yorig 2000` matches the forecast track. `--hdays 0` sets T0 at the
parent's first record (no spin-up offset).

!!! check
    ✅ **CHECK** — watch the interpolation messages: it reads **50 z-levels** and interpolates onto **75 sigma layers** (`Sigma layer : 75/75`) — the vertical refinement happening. It processes **south, west, north** and **skips east** (your `obc_dict`). Two files appear: `croco_ini_NEST_20260712_00.nc` (~58 MB) and `croco_bry_NEST_20260712_00.nc` (~20 MB).

Confirm the child inputs really have 75 levels:
```bash
ncdump -h ${CF}/croco_ini_NEST_20260712_00.nc | grep "s_rho ="
```

!!! check
    ✅ **CHECK** — `s_rho = 75`.