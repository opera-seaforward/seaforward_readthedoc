The hindcast ini subcommand builds the ocean's starting state from GLORYS for a
**date** (it picks the right monthly file, and reads across months if the window
needs it):

```bash
cd ${SEAFORWARD}
python seaforward.py make_ini_hindcast \
    --input_dir ${HCAST}/downloaded_data/GLORYS \
    --output_dir ${CF} \
    --date 2025-12-02 --Yorig ${YORIG}
```

**Flags:** `--date YYYY-MM-DD` (the IC date), `--Yorig 1993`. It reads
`crocotools_param.py` + `croco_grd.nc` from `--output_dir`.

!!! check
    ✅ **CHECK** — writes `croco_ini_GLORYS_Y2025M12D02.nc` with `s_rho = 50` and `scrum_time` in "seconds since **1993**-01-01":
    ```bash
    ls -lh ${CF}/croco_ini_GLORYS*.nc ncdump -h ${CF}/croco_ini_GLORYS*.nc | grep -E "s_rho = |since|temp"
    ```