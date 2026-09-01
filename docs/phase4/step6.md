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

**Flags:** `--date YYYY-MM-DD` is the initial-condition date, `--Yorig 1993` the time
origin. It reads `crocotools_param.py` and `croco_grd.nc` from `--output_dir`.

!!! check
    Writes `croco_ini_GLORYS_Y2025M12D02.nc` with `s_rho = 50` and `scrum_time` in seconds since **1993**-01-01:
    ```bash
    ls -lh ${CF}/croco_ini_GLORYS*.nc
    ncdump -h ${CF}/croco_ini_GLORYS*.nc | grep -E "s_rho = |since|temp"
    ```

    The `since 1993` in the time units is the single best confirmation that `Yorig` propagated correctly.

!!! warning
    **Avoid the first day of a month.** The interpolator needs a record on each side of the target date. Asking for the 1st means the record before it is in the previous month's file, and if that month isn't downloaded the run fails with:
    ```
    IndexError: index 1 is out of bounds for axis 0 with size 1
    ```

    Either start on the 2nd, as here, or download the preceding month as well. The same applies at the far end of a boundary window.