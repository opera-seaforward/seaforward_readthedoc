This phase added four hindcast subcommands to `seaforward.py`, parallel to the
forecast ones:

| Subcommand | What it does |
|---|---|
| `download_ocean_hindcast` | GLORYS monthly reanalysis (CMEMS) → `YYYY_MM.nc` |
| `download_atmosphere_hindcast` | ERA5 (CDS) request **and** convert → `for_croco/` |
| `make_ini_hindcast` | GLORYS initial condition for a `--date` |
| `make_bry_hindcast` | GLORYS boundaries for a `--start_date` / `--end_date` window, reading across months |

Plus the `hindcast/run_hindcast_cycle.sh` cycling driver.