The CLI has a hindcast ocean subcommand that pulls **GLORYS monthly files**
(`YYYY_MM.nc`, one file per month containing that month's daily records):

```bash
cd ${SEAFORWARD}
python seaforward.py download_ocean_hindcast \
    --domain="${EXTENTS}" \
    --month_start 2025-12 --month_end 2026-01 \
    --product_id cmems_mod_glo_phy_my_0.083deg_P1D-m \
    --outputDir ${HCAST}/downloaded_data/GLORYS
```

**What each flag is:**

- `--domain` — the download box (negative lons → use the `=` form, as in theforecast).
- `--month_start/--month_end` — the months to fetch (inclusive).
- `--product_id` — the CMEMS GLORYS dataset. **`..._P1D-m`** is the **daily** reanalysis (day-to-day variability); `..._P1M-m` is monthly means. Use daily for a real hindcast.

!!! important
    **Which GLORYS product / does it cover my dates?** The daily multiyear reanalysis `cmems_mod_glo_phy_my_0.083deg_P1D-m` covers 1993 → ~present (verify the current end date on the CMEMS product page). For very recent dates beyond the reanalysis, you'd switch to the interim (`myint`) or the anfc analysis. Check coverage with `copernicusmarine describe --dataset-id <id>` if unsure.

!!! check
    ✅ **CHECK** — one file per month appears:
    ```bash
    ls -lh ${HCAST}/downloaded_data/GLORYS/ncdump -h ${HCAST}/downloaded_data/GLORYS/2025_12.nc | grep -E "time = |zos|thetao|depth ="
    ```

You want `2025_12.nc`, `2026_01.nc` with `time = 31`/`time = 31` (daily records),
`depth = 50`, and the ocean variables. (Re-running skips months already present.)

!!! note
    **Neighbour months for boundaries.** Boundary conditions need ocean data slightly *beyond* the run window. For a cycle near a month edge (e.g. Dec 30 → Jan 4), the tools read **both** `2025_12.nc` and `2026_01.nc`. So download the month before and after your period too. The operational driver does this automatically.