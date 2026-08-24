| Gotcha | Symptom | Fix |
|---|---|---|
| **dt not divided by timeref** | child's clock runs 3× fast; both grids reach `MAIN: DONE`; child forced with future atmosphere. **No error.** | `croco.in.1`: `dt = dt_parent / timeref`, `NTIMES` unchanged |
| **croco_pytools `make_ini` for the child** | `u`/`v` max = `9.969e+36`; child KE = 1e+71 at **step zero** | use `seaforward.py make_ini` with the child grid as `croco_grd.nc` |
| **`easygrid.py` displacement loop** | box silently moved; boundary lands on land | compare request vs `AGRIF_FixedGrids.in`; re-check edges after building |
| **`.1` suffix vs `1_` prefix** | files not found | `croco_grd.nc.1`, not `1_croco_grd.nc` |
| **`ini_filedate` with underscores** | looks for `MERCATOR_2026071300.nc` | quote it: `ini_filedate = "20260713_00"` — Python reads `20260713_00` as the integer `2026071300` |
| **IC clocks mismatched** | child starts 2 days from the parent | check `scrum_time` in both ICs before running |
| **IC named for the cycle date** | off-by-two-days | `croco_ini_MERCATOR_20260713_00.nc` is valid at 2026-07-11 (`--hdays 2`) |
| **`AGRIF_FixedGrids.in` in `CROCO_FILES/`** | not read | it belongs in the **run** directory |
| **child N ≠ parent N** | rejected | AGRIF requires equal vertical grids |
| **ratio not 3 or 5** | rejected | only 3 or 5 |
| **high `rx1`** | possible instability over steep bathymetry | `Maximum grid stiffness ratios: rx1 = 18.4` — watch it; >~20 is a concern |
