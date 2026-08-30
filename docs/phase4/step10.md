`hindcast/run_hindcast_cycle.sh` automates the whole thing over a date range, in
**2-day spin-up + 5-day hindcast** cycles. It mirrors the forecast driver, with
GLORYS + ERA5 and a cycle loop.

![The two-phase cycle](../img/forecasting_scheme.png)

### 10.1 What one cycle does (per cycle date T)

- **spin-up** (T−2 → T): `make_ini_hindcast` at T−2 plus `make_bry_hindcast` for
  T−2→T; run 2 days → `croco_rst.nc`.
- **hindcast** (T → T+5): the initial condition is the spin-up **restart** (copied
  to `croco_ini.nc`, NRREC=1); `make_bry_hindcast` for T→T+5; run 5 days →
  `croco_his.nc` and `croco_avg.nc`.
- T then advances by 5 days to the next cycle. **Each cycle re-initialises from
  GLORYS** through its own spin-up rather than chaining restarts, which keeps a long
  hindcast anchored to the reanalysis instead of drifting.

The driver **auto-downloads** any missing GLORYS or ERA5 month for each cycle's
window, and its `patch_croco_in` sets the ERA5 online block automatically — spanning
months when a cycle crosses a boundary, e.g. `2025 12 24 2026 01`.

### 10.2 Settings at the top

```bash
CONFIG_NAME=Canary_12
START_DATE="2025-12-25"      # first cycle date T
NCYCLES=3                    # number of cycles
SPINUP_DAYS=2
HCAST_DAYS=5
YORIG=1993
EXTENTS="-23.5,-14.0,12.5,25.5"   # GLORYS box (grid + ~1.5°)
ERA5_BOX="-22,-15.5,14,24"        # ERA5 box (the downloader adds 2°)
```

!!! warning
    **Match the driver to your config.** As with the forecast driver, update `CONFIG_NAME`, `EXTENTS` and `ERA5_BOX` for a new region, or it runs Canary_12 instead of yours.

With these, the three cycles are:

| Cycle | T | spin-up | hindcast | note |
|---|---|---|---|---|
| 1 | 2025-12-25 | Dec 23→25 | Dec 25→30 | December |
| 2 | 2025-12-30 | Dec 28→30 | **Dec 30→Jan 4** | **crosses the year** |
| 3 | 2026-01-04 | Jan 2→4 | Jan 4→9 | January |

Note the hindcast windows tile without gaps or overlap — each starts where the last
one ended, because the stride equals `HCAST_DAYS`. The spin-ups sit *before* each
window and are discarded.

Cycle 2 is the interesting one: its hindcast window **Dec 30 → Jan 4** straddles the
year boundary, so it needs ocean and atmosphere data from **two** months. It will:

- build its boundaries by reading **both** `2025_12.nc` and `2026_01.nc` and stitching
  them across the year, thanks to the date-based `make_bry_hindcast` from Step 7, and
- read **both** months' ERA5 forcing — the driver sets the online block to
  `2025 12 24 2026 01`, so CROCO opens `..._Y2025M12.nc` and rolls over to
  `..._Y2026M01.nc` as the run crosses midnight on Dec 31.

This is why the cross-month support in Steps 6–7 matters: a single-month tool would
fail here.

### 10.3 Run it

```bash
cd ~/seaforward/hindcast
./run_hindcast_cycle.sh 2>&1 | tee hcast_3cycles.log
```

The `tee` keeps a full log in `hcast_3cycles.log` while you watch it live.

**What the console shows.** For each cycle you get a banner, then four stages
(trimmed):

```
############################################################
# CYCLE 1/3  T=20251225
#   spin-up : 2025-12-23 -> 2025-12-25
#   hindcast: 2025-12-25 -> 2025-12-30
############################################################
>>> [1/4] build spin-up ini + bry (GLORYS) ...
    ... make_ini_hindcast: interpolates temp/salt/u/v onto 50 sigma levels ...
    ... make_bry_hindcast: south/west/north boundaries (east skipped) ...
>>> [2/4] run spin-up ...
    CANARY_12 HINDCAST
    ... timestep table, kinetic energy small and steady, trd column = 0 ...
    MAIN: DONE                         <-- spin-up finished, wrote croco_rst.nc
>>> [3/4] build hindcast bry (GLORYS) ...
    ... make_bry_hindcast for the 5-day window ...
>>> [4/4] run hindcast ...
    ... GET_INITIAL restarts from the spin-up; GET_BRY + ONLINE_BULK read ...
    MAIN: DONE                         <-- hindcast finished, wrote croco_his.nc
  cycle 20251225 done -> .../20251225/hcast/CROCO_FILES/croco_his.nc
```

**Both model runs in every cycle must end in `MAIN: DONE`** — six in total for three
cycles.

**Watching cycle 2, the cross-year one.** Two tell-tales that the year-crossing
worked:

1. In stage `[3/4]`, the boundary window is Dec 29→Jan 5 once padded, so
   `make_bry_hindcast` pulls in both `2025_12.nc` and `2026_01.nc`. The output
   filename records the span: `croco_bry_GLORYS_Y2025M12D29_to_Y2026M01D05.nc`.
2. In stage `[4/4]`, the run header prints online forcing months spanning the year —
   first `year 2025, month 12`, last `year 2026, month 1` — and as the run passes
   Dec 31 it opens `T2M_Y2026M01.nc`.

If a cycle stops early instead of reaching `MAIN: DONE`, see Troubleshooting. The
most common first-run cause is the boundary window not extending past the run (the
`bry_time` error), which the driver's ±1-day pad normally handles.

### 10.4 Where the results go

Each cycle writes a dated folder under `hindcast/model-runs/<CONFIG>/`:

```
hindcast/model-runs/Canary_12/20251225/
├── spinup/                 # the 2-day spin-up run
│   ├── croco.in            # patched for this phase (NTIMES, online, filenames)
│   ├── croco_spinup.out    # spin-up console log
│   └── CROCO_FILES/
│       ├── croco_ini.nc    # the spin-up IC (from GLORYS, at T-2)
│       ├── croco_bry.nc    # the spin-up boundaries
│       └── croco_rst.nc    # RESTART — handed to the hindcast phase as its IC
├── hcast/                  # the 5-day hindcast run
│   ├── croco.in
│   ├── croco_hcast.out     # hindcast console log
│   └── CROCO_FILES/
│       ├── croco_ini.nc    # = the spin-up restart (warm start)
│       ├── croco_bry.nc
│       ├── croco_his.nc    # THE HINDCAST HISTORY — what you keep
│       └── croco_avg.nc    # time-averaged fields
├── gen_spinup/CROCO_FILES/ # where the spin-up ini/bry were generated (dated names)
└── gen_hcast/CROCO_FILES/  # where the hindcast bry was generated
```

and likewise `20251230/` for cycle 2 and `20260104/` for cycle 3.

!!! note
    **Why `gen_*` and generic names both exist.** The generator writes dated files — `croco_ini_GLORYS_Y2025M12D23.nc` — into `gen_spinup/`; the driver then copies them into the run directory under the generic names `croco_ini.nc` and `croco_bry.nc` that `croco.in` points at. So the run directories always use simple names, while `gen_*` keeps the provenance of which date each file was built for.

### 10.5 Check every cycle succeeded

```bash
export CONFIG_NAME=Canary_12
export OUT=${SEA_FORWARD_ROOT}/hindcast/model-runs/${CONFIG_NAME}

for d in ${OUT}/*/; do
    tag=$(basename "$d")
    his="${d}hcast/CROCO_FILES/croco_his.nc"
    if [[ -f "$his" ]] && grep -q "MAIN: DONE" "${d}hcast/croco_hcast.out" 2>/dev/null; then
        echo "  ${tag}: OK — $(du -h "$his" | cut -f1) croco_his.nc"
    else
        echo "  ${tag}: FAILED — check ${d}hcast/croco_hcast.out"
    fi
done
```

!!! check
    Three lines, one per cycle, each `OK`.

**Peek at a result** — cycle 2's history, confirming it has records and a time axis
crossing the year:

```bash
ncdump -h ${OUT}/20251230/hcast/CROCO_FILES/croco_his.nc | grep -E "time = |scrum_time|since"
```

### 10.6 Stitch the cycles into one hindcast

Each `croco_his.nc` covers its own 5-day window. Because the windows tile without
overlap and share the grid, they concatenate directly with NCO's `ncrcat`:

```bash
ncrcat ${OUT}/20251225/hcast/CROCO_FILES/croco_his.nc \
       ${OUT}/20251230/hcast/CROCO_FILES/croco_his.nc \
       ${OUT}/20260104/hcast/CROCO_FILES/croco_his.nc \
       ${OUT}/canary12_hindcast_2025-12-25_to_2026-01-09.nc
```

Keep them in time order. If `ncrcat` isn't installed: `conda install -c conda-forge nco`
or `sudo apt install nco`. The result is one file spanning Dec 25 → Jan 9 that you can
plot or analyse as a single time series.

!!! note
    **scratch vs model-runs** — the same split as the forecast. The built config (binary, grid, downloaded data) stays in `hindcast/scratch/<CONFIG>/`; each cycle's output goes to `hindcast/model-runs/<CONFIG>/<T>/`. You can delete a `model-runs/<T>/` folder and re-run that cycle without touching the build.