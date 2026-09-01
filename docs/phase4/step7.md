The hindcast bry subcommand takes a **date window** and reads whatever monthly
GLORYS files it spans — so a window crossing Dec→Jan reads both months
automatically:

```bash
cd ${SEAFORWARD}
python seaforward.py make_bry_hindcast \
    --input_dir ${HCAST}/downloaded_data/GLORYS \
    --output_dir ${CF} \
    --start_date 2025-12-02 --end_date 2025-12-30 --Yorig ${YORIG}
```

**Flags:** `--start_date` and `--end_date` are full dates, `--Yorig 1993` the time
origin. Internally it gathers the monthly files spanning the window (± a day buffer)
and hands the list to the interpolation, which concatenates them across time. It
processes the **open** boundaries — south, west and north — and **skips east**,
following your `obc_dict`.

!!! check
    Writes `croco_bry_GLORYS_Y...D..._to_Y...D....nc` with `bry_time` referenced to 1993 and only the open-boundary variables:
    ```bash
    ls -lh ${CF}/croco_bry_GLORYS_*.nc
    ncdump -h ${CF}/croco_bry_GLORYS_*to*.nc | grep -E "bry_time = |since|_south|_west|_north"
    ncdump -h ${CF}/croco_bry_GLORYS_*to*.nc | grep -c "_east"      # 0
    ```

    The `_east` count of zero is the proof that `obc_dict` took — the boundary file contains data only for the edges you declared open.

!!! warning
    **Keep the window inside the months you downloaded.** The ± day buffer means the last day of your window needs a GLORYS record *after* it. Ending on the last day of a downloaded month — or the first day of one — fails the same way `make_ini` does. Pull the end date back a day, or download the following month.

!!! note
    **Cross-year windows work.** `--start_date 2025-12-30 --end_date 2026-01-04` reads **both** `2025_12.nc` and `2026_01.nc` and stitches them; the filename records the span, e.g. `..._Y2025M12D30_to_Y2026M01D04.nc`.