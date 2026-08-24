- **GFS "authentication" / licence error** — set up `~/.cdsapirc` and accept the
  GFS dataset licence on the CDS site (Step 3).
- **CROCO can't find an GFS file** — month padding: CROCO wants `M01` for Jan–Sep. Rename `M1`→`M01` (Step 5 WATCH) and confirm the convert uses `.zfill(2)`.
- **GLORYS empty / date out of range** — the `my` reanalysis has an end date; check the product's coverage, or use `myint`/anfc for very recent dates.
- **bry fails at a month edge** — you're missing the neighbour month; download the month before/after so the window's ± day buffer is covered.
- **`ERROR in get_bry: cannot read variable 'bry_time'`** or **`SET_CYCLE ERROR: non-cycling regime, but model time exceeds ...`** — the boundary file doesn't extend past the run window. CROCO needs a bry record *bracketing* every timestep, so the boundary time series must reach **one day beyond** the run on each end (and with `cycle_bry=0` it can't wrap around). Fix: build each phase's bry with a ±1-day pad — i.e. for a run `T0→T1`, call `make_bry_hindcast --start_date <T0−1day> --end_date <T1+1day>`. The operational driver does this automatically; if you run a phase by hand, add the pad yourself.
- **`inputdata` error in ini/bry** — must be `'mercator'` (GLORYS reads through it), not `'glorys'`.
- **BLOW UP / NaN** — recheck boundaries match the mask and the timestep; same as the forecast.