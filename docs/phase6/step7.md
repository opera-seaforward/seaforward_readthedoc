```bash
cd ${FCAST}
# all three inputs must exist
ls -lh CROCO_FILES/croco_grd.nc \
       CROCO_FILES/croco_ini_NEST_20260712_00.nc \
       CROCO_FILES/croco_bry_NEST_20260712_00.nc

./croco croco.in 2>&1 | tee run.log | tail -60
```

**What to watch:** it reads the grid, `GET_INITIAL` (child ini), `GET_BRY` (child
bry) and `ONLINE_BULK -- Read file` (GFS forcing), then a step table counting
toward 2880. The columns are step number, model time, **kinetic energy**, and
`trd` (error flag).

!!! check
    ✅ **CHECK** — the **kinetic-energy column stays small and steady** (e.g. ~1.4×10⁻³, not growing), `trd = 0` every row, and it ends with **`MAIN: DONE`**, writing:

```bash
ls -lh ${CF}/croco_his.nc
tail -5 run.log
```

!!! warning
    ⚠️ **WATCH — instability (`BLOW UP` / `NaN` / KE exploding).** At 1/25° this usually means the timestep is too large or the boundaries are reflecting. Fixes, in order: (1) turn the **sponge on** (`X_SPONGE 25000. 400.`) if you had it off; (2) reduce `dt` to 120 (`NTIMES=3600`); (3) re-check the open boundaries match the mask. Sponge and timestep are runtime values — no recompile needed, just re-stage `croco.in` and rerun.

## What you have now

A **nested 1/25°, 75-level child** that ran to completion, forced entirely by your
own 1/12° model:

```
forecast/scratch/Canary_25/
├── croco                              # the compiled child
├── cppdefs.h param.h croco.in jobcomp # child config (also in configs/Canary_25)
├── run.log                            # proof it ran to MAIN: DONE
├── CROCO_FILES/
│   ├── croco_grd.nc                   # 1/25° grid (150×238)
│   ├── crocotools_param.py            # N=75 pre-processing params
│   ├── croco_ini_NEST_20260712_00.nc  # child initial (75 levels)
│   ├── croco_bry_NEST_20260712_00.nc  # child boundaries (75 levels)
│   └── croco_his.nc                   # the nested 1/25° output
└── downloaded_data/PARENT/
    └── parent_20260712.nc             # the 1/12° output, in Mercator format
```

**Next:** validate the child against the parent — does 1/25° resolve finer eddies
and filaments than 1/12°? Use the Phase-5 tools (`compare_*`, `field_map`,
`error_vs_depth`) with the child as the fine model and the parent as the
reference. Then Part B wraps all of Steps 3–7 into an on-demand nesting driver.