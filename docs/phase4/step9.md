The one section that differs from the forecast is **`online:`**, which uses the
GFS form (real byear/bmonth, not the GFS `9999` dummy dates). For a single manual
test run (7 days, Dec 2→9, ini at D02):

```bash
nano croco.in
```

Make the Phase 2 Step 10 edits (title, S-coord, sponge) **plus** these. Each is a
`Ctrl-W` search, then edit the line *below* the keyword.

**Title.** `Ctrl-W` `BENGUELA TEST`, Enter. Change line 2 to:
```
        CANARY_12 HINDCAST
```

**time_stepping** — `Ctrl-W` `720`, Enter (or search `time_stepping`). Set the
values line (7 days at dt=300 → `NTIMES = 7×86400/300 = 2016`):
```
                2016      300      60      1
```

**initial** (NRREC=1) — `Ctrl-W` `croco_ini.nc`, Enter. Change the filename line to
your GLORYS ini (leave the `1` on the NRREC line above it):
```
    CROCO_FILES/croco_ini_GLORYS_Y2025M12D02.nc
```

**boundary** — `Ctrl-W` `croco_bry.nc`, Enter. Change the filename line to your
GLORYS bry:
```
    CROCO_FILES/croco_bry_GLORYS_Y2025M12D01_to_Y2025M12D10.nc
```

!!! warning
    ⚠️ Build this bry with a window that extends **one day past** the run on each end (so Dec 1 → Dec 10 for a Dec 2 → Dec 9 run). CROCO needs a boundary record bracketing every timestep — otherwise it errors at the last step with `cannot read variable 'bry_time'`. See Troubleshooting. (Generate it with `make_bry_hindcast --start_date 2025-12-01 --end_date 2025-12-10`.)

**sponge** — `Ctrl-W` `X_SPONGE`, Enter. Change the values line (the `XXX XXX`) to:
```
                    50000.            400.
```

**online (GFS form)** — `Ctrl-W` `byear  bmonth`, Enter. Set the two lines below
the `online:` header — the numbers line, then the data-path line:
```
online:    byear  bmonth recordsperday byearend bmonthend / data path
           2025   12      24            2025     12
    /home/<you>/seaforward/hindcast/scratch/Canary_12/downloaded_data/GFS/for_croco/
```
(replace `<you>` with your username).

- **What the online fields mean:** `byear=2025 bmonth=12` (window start),
  `recordsperday=24` (GFS is **hourly**), `byearend/bmonthend` (window end).
  CROCO builds `<path><VAR>_Y<year>M<month>.nc` (e.g. `T2M_Y2025M12.nc`) and reads
  across months if start/end differ.

Save: `Ctrl-O`, Enter. Exit: `Ctrl-X`.

!!! check
    ✅ **Verify all edits:**
    ```bash
    grep -nA1 "^time_stepping:" croco.in
    grep -nA2 "^initial:" croco.in
    grep -nA1 "^boundary:" croco.in
    grep -nA1 "^sponge:" croco.in
    grep -nA2 "^online:" croco.in
    grep -n "XXX" croco.in && echo "STILL HAS XXX" || echo "no XXX left"
    sed -n '2p' croco.in
    ```
Want: title `CANARY_12 HINDCAST`, time_stepping `2016 300 60 1`, initial → the
GLORYS ini with NRREC=1, boundary → the GLORYS bry, sponge `50000. 400.`, online
`2025 12 24 2025 12` + the GFS path, and no `XXX` left.

!!! important
    **`start_date`/`end_date`** — as in the forecast, with `USE_CALENDAR` off these are ignored for the manual run; leave them. (CROCO prints a harmless `Unrecognized keyword: start_date DISREGARDED`.) The operational driver patches them per phase for bookkeeping.

Then **compile** follow these instructions

```bash
cd ${HCAST}
cp ${CONFIG_DIR}/{cppdefs.h,param.h,croco.in,jobcomp} .
```

Then set the compile environment and build. **Compile outside conda** so the
system linker uses your `opt_seq` NetCDF, not conda's:

```bash
conda deactivate                 # leave conda for the link step
source ~/seaforward/env.sh       # ensures opt_seq's nf-config + compilers are set
which nf-config                  # must show .../seaforward/opt_seq/bin/nf-config
./jobcomp 2>&1 | tee compile.log | tail -40
```

!!! check
    ✅ **CHECK** — after a few minutes you see the CROCO ASCII logo and **`CROCO is OK`**, and a `croco` program appears:
     ```bash
      ls -lh ${HCAST}/croco
     ```