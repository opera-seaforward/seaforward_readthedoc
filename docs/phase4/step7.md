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

**Flags:** `--start_date`/`--end_date` (full dates), `--Yorig 1993`. Internally it
gathers the monthly files spanning the window (± a day buffer) and hands the list
to the interpolation, which concatenates them across time. It processes the
**open** boundaries (south, west, north) and **skips east** (your `obc_dict`).

!!! check
    ✅ **CHECK** — writes `croco_bry_GLORYS_Y...D..._to_Y...D....nc` with `bry_time` referenced to 1993 and the open-boundary variables (no `_east`):
    ```bash
    ls -lh ${CF}/croco_bry_GLORYS_*.nc ncdump -h ${CF}/croco_bry_GLORYS_*to*.nc | grep -E "bry_time = |since|_south|_west|_north"
    ```

!!! note
    **Cross-year proof.** A window like `--start_date 2025-12-30 --end_date 2026-01-04` reads **both** `2025_12.nc` and `2026_01.nc` and stitches them — the file name records the span, e.g. `..._Y2025M12D30_to_Y2026M01D04.nc`.