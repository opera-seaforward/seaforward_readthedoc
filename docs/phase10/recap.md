Mapped onto the Phase 2 build, so you know which step each one extends:

1. **Tool** *(extends Phase 2 Step 5)* — `make_tides` added to `seaforward.py`, reading
   a tide-specific `crocotools_param.py` from its own gen dir, which avoids the
   `inputdata` clash with the Mercator param.
2. **Data** — TPXO10 atlas, or TPXO7 single-file, in `DATASETS_CROCOTOOLS/`, with a
   param file whose filename templates match the download.
3. **Param file** *(extends Phase 2 Step 4)* — `crocotools_param_tides.py` alongside
   the Mercator `crocotools_param.py`, in the config's `CROCO_FILES/`.
4. **Generate and check** *(extends Phase 2 Step 5)* — one command per grid; verify the
   M2 amplitude is physical and any fill values sit only on land.
5. **cppdefs** *(edits Phase 2 Step 8)* — `TIDES`, `SSH_TIDES`, `UV_TIDES` and
   `POT_TIDES` on; `TIDES_MAS` and `USE_CALENDAR` off; recompile and rename the binary.
6. **croco.in** *(edits Phase 2 Step 10)* — `forcing:` points at `croco_frc.nc`; no
   `Ntides` section needed.
7. **Output** *(edits Phase 2 Step 13)* — hourly history, daily average: resolve M2,
   then remove it.
8. **Prove** — the sea-level oscillation at ~12.4 h, the spring–neap envelope across
   the run, and the spatial range read against the bathymetry.
9. **Operationalise** — `--tides` in the driver: per-cycle generation, staging to both
   phases, output retiming, binary selection, and with a child a second generation on
   the child grid.

The one thing to keep right is the date. The tide file's phase epoch is set when it is
built, so a file built for the wrong day puts every wave out of phase — and the run
completes without complaint. The driver handles this per cycle; by hand, it is the
`--run_date` you pass to `make_tides`.