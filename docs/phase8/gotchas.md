| Gotcha | Symptom | Fix |
|---|---|---|
| **dt not divided by timeref** | child's clock runs 3× fast; both grids reach `MAIN: DONE`; child forced with future atmosphere. **No error.** | `croco.in.1`: `dt = dt_parent / timeref`, `NTIMES` unchanged |
| **croco_pytools `make_ini` for the child** | `u`/`v` max = `9.969e+36`; child KE = 1e+71 at **step zero** | use `seaforward.py make_ini` with the child grid as `croco_grd.nc` |
| **`easygrid.py` displacement loop** | box silently moved; a boundary lands on land | compare the request against `AGRIF_FixedGrids.in`; re-check edges after building |
| **`.1` suffix vs `1_` prefix** | files not found | `croco_grd.nc.1`, not `1_croco_grd.nc` |
| **IC clocks mismatched** | child starts days from the parent | check `scrum_time` in both ICs before running |
| **IC named for the cycle date** | off by two days | `croco_ini_MERCATOR_20260713_00.nc` is valid at 2026-07-11, from `--hdays 2` |
| **`AGRIF_FixedGrids.in` in `CROCO_FILES/`** | not read; the model runs as if there were no child | it belongs in the **run** directory |
| **binary not renamed** | driver reports "binary not found" | `cp croco croco_1way` after each build; the driver selects by name |
| **child N ≠ parent N** | rejected | AGRIF requires equal vertical grids |
| **ratio not 3 or 5** | rejected | only 3 or 5 |
| **output intervals not scaled** | parent and child write different numbers of records | multiply the child's `NWRT`, `NAVG`, `NRST` by `timeref` |
| **high `rx1`** | possible instability over steep bathymetry | the IGOG child reports 15.78; watch it, and above about 20 lower `rfact` |