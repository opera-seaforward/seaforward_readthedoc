This phase added four hindcast subcommands to `seaforward.py`, parallel to the
forecast ones:

| Subcommand | Does |
|---|---|
| `download_ocean_hindcast` | GLORYS monthly reanalysis (CMEMS) → `YYYY_MM.nc` |
| `download_atmosphere_hindcast` | GFS (CDS) request **+** convert → `for_croco/` |
| `make_ini_hindcast` | GLORYS initial condition for a `--date` |
| `make_bry_hindcast` | GLORYS boundaries for a `--start_date/--end_date` window (cross-month) |

Plus the `hindcast/run_hindcast_cycle.sh` cycling driver.