- **ERA5 authentication or licence error** — set up `~/.cdsapirc` and accept the
  ERA5 dataset licence on the CDS site (Step 3).
- **CROCO can't find an ERA5 file** — month padding: CROCO wants `M01` for Jan–Sep.
  Rename `M1` → `M01` (Step 5) and confirm the converter uses `.zfill(2)`.
- **GLORYS empty, or date out of range** — the `my` reanalysis has an end date; check
  the product's coverage, or use `myint` or the analysis-forecast for very recent
  dates.
- **`IndexError: index 1 is out of bounds for axis 0 with size 1`** in `make_ini` —
  you downloaded the monthly-mean product. Re-download with
  `--product_id cmems_mod_glo_phy_my_0.083deg_P1D-m`; `ncdump -h` should show
  `time = 30` or `31`, not `1`.
- **bry fails at a month edge** — you're missing the neighbour month; download the
  month before and after so the window's ±1-day buffer is covered.
- **`ERROR in get_bry: cannot read variable 'bry_time'`** or **`SET_CYCLE ERROR:
  non-cycling regime, but model time exceeds ...`** — the boundary file doesn't extend
  past the run window. CROCO needs a boundary record *bracketing* every timestep, so
  the series must reach **one day beyond** the run at each end, and with `cycle_bry=0`
  it can't wrap around. Build each phase's bry with a ±1-day pad: for a run `T0→T1`,
  call `make_bry_hindcast --start_date <T0−1day> --end_date <T1+1day>`. The driver does
  this automatically; if you run a phase by hand, add the pad yourself.
- **`inputdata` error in ini or bry** — it must be `'mercator'`, not `'glorys'`.
  GLORYS reads through the `'mercator'` branch; there is no `'glorys'` key.
- **The run ends early with the ERA5 forcing "missing"** — check `bmonthend` in the
  `online:` block is the *last* month of the run, not the first.
- **BLOW UP or NaN** — recheck the boundaries match the mask, and the timestep; same
  as the forecast.