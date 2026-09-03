Now the **standard Phase-2 ini/bry step**, but the input is the converted parent
instead of a Mercator download.

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

**What / Why:** identical to Phase 2 Step 5, except `--input_file` is the converted
parent and `--Yorig 2000` matches the forecast track. `--hdays 0` puts T0 at the
parent's first record, with no spin-up offset.

!!! warning
    **`--run_date` must fall inside the converted parent's time range.** Step 3 printed it — `21 time(s)` spanning the parent's forecast window. Ask for a date outside that and the interpolation has nothing to work from. Check first if you're unsure:
    ```bash
    python3 -c "
    import xarray as xr
    d = xr.open_dataset('${PARENT}')
    print(d.time.values[0], '->', d.time.values[-1])"
    ```

!!! check
    Watch the interpolation messages: it reads **50 z-levels** and interpolates onto **75 sigma layers** (`Sigma layer : 75/75`) — the vertical refinement happening in front of you. It processes **south, west, north** and **skips east**, following your `obc_dict`. Two files appear: `croco_ini_NEST_20260712_00.nc` (~58 MB) and `croco_bry_NEST_20260712_00.nc` (~20 MB).

Confirm the child inputs really have 75 levels:

```bash
ncdump -h ${CF}/croco_ini_NEST_20260712_00.nc | grep "s_rho ="
```

!!! check
    `s_rho = 75`. The parent had 50 — this is where the refinement landed.