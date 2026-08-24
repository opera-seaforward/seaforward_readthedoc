Mapped onto the Phase 2 build (so you know which step each one extends):

1. **Tool** *(extends Phase 2 Step 5)* — `make_tides` added to `seaforward.py`,
   reading a tide-specific `crocotools_param.py` from its own gen dir (avoids the
   `inputdata` clash with the mercator param).
2. **Data** — TPXO10 atlas (or TPXO7 single-file), in `DATASETS_CROCOTOOLS/`,
   with a param file whose filename templates match the download.
3. **Param file** *(extends Phase 2 Step 4)* — `crocotools_param_tides.py`
   alongside the mercator `crocotools_param.py`, in the config's `CROCO_FILES/`.
4. **Generate + check** *(extends Phase 2 Step 5)* — one command per grid; verify
   M2 amplitude is physical and any fill values sit only on land.
5. **cppdefs** *(edits Phase 2 Step 8.3)* — `TIDES`/`SSH_TIDES`/`UV_TIDES`/
   `POT_TIDES` on, `TIDES_MAS` and `USE_CALENDAR` off; recompile (Step 12).
6. **croco.in** *(edits Phase 2 Step 10)* — `forcing:` points at `croco_frc.nc`;
   no `Ntides` section needed.
7. **Output** *(edits Phase 2 Step 13)* — hourly history, daily average (resolve
   M2, then remove it).
8. **Prove** — the shelf-point oscillation at ~12.4 h, the shelf-amplified range,
   the unchanged daily-mean RMSE vs Mercator.
9. **Operationalise** — `--tides` in the driver: per-cycle generation, staging to
   both phases, output retiming, binary selection, and (with a child) a second
   generation on the child grid.

The tide file carries a date; the driver keeps that date right for every cycle.
Get that one thing correct and the rest is bookkeeping.