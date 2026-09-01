The one section that differs from the forecast is **`online:`**, which uses the ERA5
form — real `byear`/`bmonth`, not the GFS `9999` dummy dates. For a single manual
test run (7 days, Dec 2→9, ini at D02):

```bash
nano croco.in
```

Make the Phase 2 Step 11 edits (title, S-coord, sponge) **plus** these. Each is a
`Ctrl-W` search, then edit the line *below* the keyword.

**Title.** `Ctrl-W` `BENGUELA TEST`, Enter. Change line 2 to:

```
        CANARY_12 HINDCAST
```

**time_stepping** — `Ctrl-W` `time_stepping`, Enter. Set the values line (7 days at
`dt=300` → `NTIMES = 7×86400/300 = 2016`):

```
                2016      300      60      1
```

**initial** (NRREC=1) — `Ctrl-W` `croco_ini.nc`, Enter. Change the filename line to
your GLORYS ini, leaving the `1` on the NRREC line above it:

```
    CROCO_FILES/croco_ini_GLORYS_Y2025M12D02.nc
```

**boundary** — `Ctrl-W` `croco_bry.nc`, Enter. Change the filename line to your
GLORYS bry:

```
    CROCO_FILES/croco_bry_GLORYS_Y2025M12D01_to_Y2025M12D10.nc
```

!!! warning
    **Build the bry with a window that extends one day past the run at each end** — Dec 1 → Dec 10 for a Dec 2 → Dec 9 run. CROCO needs a boundary record bracketing every timestep; without the margin it stops at the last step with `ERROR in get_bry: cannot read variable 'bry_time'`. Generate it with `make_bry_hindcast --start_date 2025-12-01 --end_date 2025-12-10`.

**sponge** — `Ctrl-W` `X_SPONGE`, Enter. Replace the `XXX  XXX` values line:

```
                    0.                0.
```

As in Phase 2, the sponge is off here: the parent product is at the same resolution
as the model, so the boundary mismatch is small. If energy builds up along an open
edge, turn it on with `50000.  400.`

**online (ERA5 form)** — `Ctrl-W` `byear  bmonth`, Enter. Set the two lines below the
`online:` header — the numbers line, then the data path:

```
online:    byear  bmonth recordsperday byearend bmonthend / data path
           2025   12      24            2025     12
    /home/<you>/seaforward/hindcast/scratch/Canary_12/downloaded_data/ERA5/for_croco/
```

Replace `<you>` with your username.

- **What the fields mean:** `byear=2025 bmonth=12` is the window start,
  `recordsperday=24` because ERA5 is hourly, and `byearend`/`bmonthend` the window
  end. CROCO builds `<path><VAR>_Y<year>M<month>.nc` — `T2M_Y2025M12.nc` and so on —
  and reads across months when start and end differ.

!!! warning
    **`bmonthend` must be the last month of the run, not the first.** A three-month hindcast starting in June needs `2018 6 24 2018 8`; leaving it as `2018 6` runs out of forcing at the end of June.

Save: `Ctrl-O`, Enter. Exit: `Ctrl-X`.

!!! check
    ```bash
    grep -nA1 "^time_stepping:" croco.in
    grep -nA2 "^initial:" croco.in
    grep -nA1 "^boundary:" croco.in
    grep -nA1 "^sponge:" croco.in
    grep -nA2 "^online:" croco.in
    grep -n "XXX" croco.in && echo "STILL HAS XXX" || echo "no XXX left"
    sed -n '2p' croco.in
    ```

    You want: title `CANARY_12 HINDCAST`, time_stepping `2016 300 60 1`, initial pointing at the GLORYS ini with NRREC=1, boundary at the GLORYS bry, sponge `0. 0.`, online `2025 12 24 2025 12` with the ERA5 path, and no `XXX` left.

!!! note
    **Leave `start_date` / `end_date` alone.** As in the forecast, `USE_CALENDAR` is off, so CROCO ignores them and prints a harmless `Unrecognized keyword: start_date DISREGARDED`. The operational driver fills them in per phase purely for bookkeeping.

### Stage the files into the run folder

You edited the four files in `${CONFIG_DIR}` — the config recipe. The build and the
run happen in `${HCAST}`, so copy them across:

```bash
cd ${HCAST}
cp ${CONFIG_DIR}/{cppdefs.h,param.h,croco.in,jobcomp} .
ls cppdefs.h param.h croco.in jobcomp
```

Everything from here on happens in `${HCAST}`.

### Compile

Compile **outside conda**, so the system linker uses your `opt_seq` NetCDF rather
than conda's:

```bash
conda deactivate                 # leave conda for the link step
source ~/seaforward/env.sh       # opt_seq's nf-config + compilers
which nf-config                  # must show .../seaforward/opt_seq/bin/nf-config
./jobcomp 2>&1 | tee compile.log | tail -40
```

!!! check
    After a few minutes: the CROCO logo and **`CROCO is OK`**, and a `croco` program appears.

```bash
    ls -lh croco
```

### Run it

```bash
./croco croco.in 2>&1 | tee run.log | tail -60
```

**What to watch.** It reads the grid, initial, boundary and ERA5 files
(`GET_INITIAL`, `GET_BRY`, `ONLINE_BULK -- Read file`), then a step table counting
toward 2016. Kinetic energy should stay bounded rather than growing, and `trd` should
be `0`.

**Read the first timestamp.** The `time[DAYS]` column counts from `Yorig`, so a run
starting 2025-12-02 shows about `11994` — days since 1993-01-01. That single number
confirms `Yorig`, the initial condition, the boundaries and the ERA5 forcing all
agree, which makes it the best sanity check in the whole build.

!!! check
    It ends with **`MAIN: DONE`** and writes the output:
    ```bash
    ls -lh ${CF}/croco_his.nc ${CF}/croco_avg.nc
    tail -6 run.log
    ```

!!! warning
    **If it stops with `ERROR in get_bry: cannot read variable 'bry_time'`** near the end, the boundary file ran out — rebuild it with a day's margin at each end. **If numbers go `NaN` or it says `BLOW UP`**, recheck that the open boundaries match the mask and that `dt` isn't too large.