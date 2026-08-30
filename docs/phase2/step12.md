![build progress](../img/run_parent.png)

*Step 12 **runs the model** — now every prepared input converges on the run.*

Compiling only proves the code builds — it doesn't prove your grid, boundaries and
data actually run. So do **one** manual run here. The operational driver in Phase 3
does this automatically every day; this single run is the by-hand proof.

Four sections of `croco.in` need setting for a run: how long to integrate, which
initial and boundary files to read, and where the surface forcing lives. The driver
patches these for you; here you do it by hand.

First stage the `croco.in` you edited in Step 11 into the run folder — the compile
step staged the other three files, this is the last one — then patch it:

```bash
cd ${FCAST}
cp ${CONFIG_DIR}/croco.in .            # stage the run-time file you edited in Step 11
TODAY=$(date -u +%Y%m%d)

# NTIMES  dt  NDTFAST  NINFO
#   2016 steps x 300 s = 7 days (the today-2 .. today+5 window)
#   60 = barotropic sub-steps per baroclinic step; 1 = print every step
sed -i '/^time_stepping:/{n; s/.*/                2016     300       60      1/}' croco.in

# initial condition — two lines below the header (NRREC, then the filename)
sed -i "/^initial:/{n; n; s|.*|    CROCO_FILES/croco_ini_MERCATOR_${TODAY}_00.nc|}" croco.in

# boundary file — one line below the header
sed -i "/^boundary:/{n; s|.*|    CROCO_FILES/croco_bry_MERCATOR_${TODAY}_00.nc|}" croco.in

# online forcing — the settings line, then the path to for_croco/
sed -i '/^online:/{n;   s/.*/           9999   1      24            9999     1/}' croco.in
sed -i "/^online:/{n; n; s|.*|    ${FCAST}/downloaded_data/GFS/for_croco/|}" croco.in
```

Each `sed` finds a section header in `croco.in` and rewrites the line below it —
`{n;}` moves down one line, `{n; n;}` two. Nothing else in the file is touched.
Check they landed:

```bash
grep -A2 -E "^(time_stepping|initial|boundary|online):" croco.in
```

!!! note
    **Why these values.** `dt=300` s and `NTIMES=2016` integrate **7 days** — the whole `today−2 … today+5` window — as one continuous cold-started run. (This is not the two-phase spin-up/forecast cycle described at the end of the chapter; that splits the same window in two. Here it is a single straight integration, enough to prove the configuration runs.) `9999 1 24 9999 1` is the dummy-date convention that pairs with the `Y9999M01` forcing files (24 = hourly records). With `USE_CALENDAR` off (the regional default), CROCO ignores real calendar dates and just steps through the records — so you don't hand-edit real dates here, and you can leave `start_date` / `end_date` alone.

Check what the output intervals are set to before you run:

```bash
grep -A2 -E "^(history|averages|restart):" croco.in
```

`NWRT` and `NAVG` are counted in timesteps, so at `dt=300` a value of 72 writes every
6 hours and 288 writes daily. For this proof run the template defaults are fine.

Now run the model (outside conda, same linker reason as compiling):

```bash
cd ${FCAST}
conda deactivate
source ~/seaforward/env.sh
./croco croco.in 2>&1 | tee run.log | tail -60
```

**What to watch:** it reads the grid, initial, boundary and weather files
(`GET_INITIAL`, `GET_BRY`, `ONLINE_BULK -- Read file`), then a table of steps
counting toward 2016. The kinetic-energy column should stay small and steady (not
grow), and `trd` should be `0`.

!!! check
    It ends with **`MAIN: DONE`** and writes the outputs:

```bash
    ls -lh ${CF}/croco_his.nc ${CF}/croco_avg.nc
    tail -6 run.log
```

You should see `croco_his.nc` (history) and `croco_avg.nc` (averages). The
`IEEE_UNDERFLOW` note at the very end is harmless. Your configuration is now
proven — it builds *and* runs.

!!! warning
    **If it crashes with `Abnormal termination: netCDF INPUT`** right after "Open Meteo file" — it's the GFS longitude issue; redo the GFS-longitude fix in Step 5b. **If numbers go `NaN` or it says `BLOW UP`** — an instability: recheck that the open boundaries (Step 3) match the mask, and that the timestep isn't too large.