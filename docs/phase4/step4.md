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

- `--domain` — the download box. Use the `--domain="${EXTENTS}"` form with the equals
  sign: a box with negative longitudes starts with `-`, and the parser would read that
  as an option. The `=` form is safe either way.
- `--month_start` / `--month_end` — the months to fetch, inclusive.
- `--product_id` — the CMEMS GLORYS dataset. `..._P1D-m` is the daily reanalysis;
  `..._P1M-m` is monthly means.

!!! warning
    **Always pass `--product_id` with `P1D`.** Without it the default is the **monthly-mean** product — one record per month. `make_ini_hindcast` then fails with `IndexError: index 1 is out of bounds for axis 0 with size 1`, because it needs two records to bracket a date. Monthly means are also unusable for a hindcast: no synoptic variability enters at the boundaries, and any later particle tracking needs daily currents at minimum.

!!! note
    **Does the product cover your dates?** The daily multiyear reanalysis `cmems_mod_glo_phy_my_0.083deg_P1D-m` runs from 1993 to roughly the present — check the current end date on the CMEMS product page. For dates beyond the reanalysis, switch to the interim product (`myint`) or the analysis-forecast. `copernicusmarine describe --dataset-id <id>` shows coverage.

!!! check
    One file per month appears:
    ```bash
    ls -lh ${HCAST}/downloaded_data/GLORYS/
    ncdump -h ${HCAST}/downloaded_data/GLORYS/2025_12.nc | grep -E "time = |zos|thetao|depth ="
    ```

You want `2025_12.nc` and `2026_01.nc`, each with **`time = 31`** (daily records — this is the check that catches the monthly-mean mistake), `depth = 50`, and the ocean variables. Re-running skips months already present.

!!! note
    **Neighbour months for boundaries.** Boundary conditions need ocean data slightly *beyond* the run window. For a cycle near a month edge — Dec 30 to Jan 4, say — the tools read **both** `2025_12.nc` and `2026_01.nc`. So download the month before and after your period too. The operational driver does this automatically.