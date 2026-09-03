`croco.in` is CROCO's runtime settings file — timestep, dates, which files to read,
what to output. With AGRIF, **each grid gets its own**: the parent reads `croco.in`,
the child reads `croco.in.1`. You launch only the parent's; AGRIF finds the child's
automatically via `AGRIF_FixedGrids.in`.

Start from a copy of the parent's, because the child should share its physics, its
output settings and its forcing — you are changing only what is genuinely per-grid.
CROCO also ships a reference at `code/croco/OCEAN/croco.in.1` if you want to compare.

```bash
cd ~/seaforward/forecast/scratch/Canary_AGRIF
cp ~/seaforward/forecast/scratch/Canary_12/{cppdefs.h,param.h,croco.in,jobcomp} .
cp croco.in croco.in.1
```

!!! note
    **First, check the parent's own filenames.** If you copied `croco.in` from a config the driver has run, it points at that cycle's dated files — `croco_ini_MERCATOR_20260711_00.nc` rather than `croco_ini.nc` — while Step 4 staged them under the short names. Fix `croco.in` before going further:

```text
    boundary: filename
        CROCO_FILES/croco_bry.nc
    initial: NRREC / filename
              1
        CROCO_FILES/croco_ini.nc
```

    Then confirm both agree with what is on disk:

```bash
    ls CROCO_FILES/
    grep -n "CROCO_FILES/" croco.in | head -8
```

Now the child's copy:

```bash
nano croco.in.1
```

Six edits follow. Take them in order.

### 5a — the title

`Ctrl+W` `title` `Enter`. The cursor lands on line 1; the line **below** it is the
title text:

```text
title:
        CANARY_12 FORECAST                     <- change this
```

to

```text
title:
        CANARY_12 AGRIF ZOOM LEVEL 1
```

Cosmetic, but it is how you tell the two grids apart in the log — CROCO prints each
grid's title as it initialises.

### 5b — the timestep

`Ctrl+W` `time_stepping` `Enter`. **There are two matches.** The first is the one you
want:

```text
time_stepping: NTIMES   dt[sec]  NDTFAST  NINFO
                 288       300      60      1     <- this line
time_stepping_nbq: NDTNBQ    CSOUND_NBQ    VISC2_NBQ    <- NOT this one
```

Change `300` to `100` and **leave `288` alone**:

```text
                 288       100      60      1
```

The asymmetry behind that is explained at the end of this page, and it is the edit
most worth checking afterwards.

If your parent's `croco.in` still carries the driver's own `NTIMES` — 2016 for a
seven-day cycle — set both files to 288 for this one-day test, then raise them
together later.

### 5c — the grid file

`Ctrl+W` `grid:` `Enter`:

```text
grid:  filename
    CROCO_FILES/croco_grd.nc          <- add .1
```

becomes

```text
grid:  filename
    CROCO_FILES/croco_grd.nc.1
```

### 5d — the boundary file: delete it

`Ctrl+W` `boundary:` `Enter`:

```text
boundary: filename
    CROCO_FILES/croco_bry.nc          <- replace with the placeholder
```

becomes

```text
boundary: filename
      XXXXXXXXX
```

`XXXXXXXXX` is a deliberate non-existent filename — CROCO's way of saying "this
section is unused". **AGRIF supplies the child's boundaries every barotropic step;
there is no child bry file.** This is the line that most clearly distinguishes AGRIF
from the Phase 7 offline nest, where the bry file *was* the entire mechanism.

Do the same for `climatology:` if your parent has one.

### 5e — the initial file

`Ctrl+W` `initial:` `Enter`:

```text
initial: NRREC / filename
          1
    CROCO_FILES/croco_ini.nc          <- add .1
```

becomes `CROCO_FILES/croco_ini.nc.1`.

### 5f — the output files

Three more: `Ctrl+W` `history:`, then `averages:`, then `restart:`. Each has a
filename on the line below — append `.1` to all three:

```text
    CROCO_FILES/croco_his.nc.1
    CROCO_FILES/croco_avg.nc.1
    CROCO_FILES/croco_rst.nc.1
```

Skip these and the child writes into the parent's output files, and you lose both.

Save and exit: `Ctrl+O` `Enter`, `Ctrl+X`.

### Verify

```bash
grep -n "CROCO_FILES/" croco.in.1 | head -8
grep -n -A1 "^time_stepping:" croco.in.1
grep -n -A1 "^boundary:" croco.in.1
```

```text
23:    CROCO_FILES/croco_grd.nc.1
25:    CROCO_FILES/croco_frc.nc
27:    CROCO_FILES/croco_blk.nc
29:    CROCO_FILES/croco_clm.nc
34:    CROCO_FILES/croco_ini.nc.1
37:    CROCO_FILES/croco_rst.nc.1
41:    CROCO_FILES/croco_his.nc.1
44:    CROCO_FILES/croco_avg.nc.1
3:time_stepping: NTIMES   dt[sec]  NDTFAST  NINFO
4-                288     100       60      1
30:boundary: filename
31-      XXXXXXXXX
```

Five `.1` filenames, `dt = 100`, and the placeholder where the boundary was. The
`frc`, `blk` and `clm` lines stay as they are — their CPP switches are off, so CROCO
prints "Unrecognized keyword … DISREGARDED" and moves on.

Filenames are **explicit** — AGRIF does not append `.1` for you.

### The dt and NTIMES asymmetry

Getting this wrong does not fail. The run completes, both grids report `MAIN: DONE`,
and the answer is wrong.

The asymmetry is:

- **AGRIF multiplies the child's `NTIMES` by `timeref`.** You write 288; AGRIF runs
  864. Do not pre-multiply it yourself.
- **AGRIF does not divide the child's `dt`.** It uses whatever you wrote. You must set
  it to `dt_parent / timeref` by hand.

So for a parent at `288 × 300` with `timeref = 3`:

```text
parent croco.in    :  288    300      -> 288 steps x 300 s = 1 day
child  croco.in.1  :  288    100      -> AGRIF runs 864 x 100 s = 1 day
```

Leave `dt = 300` in the child and you get 864 × 300 s = **3 days** while the parent
runs 1. The child races ahead, pulls atmospheric forcing from two days in the parent's
future, and finishes "successfully".

**Verify the clocks in the log after starting the run.** Parent step 12 and child step
36 must report the same time:

```bash
grep -E "^ +(12|36) +9686\." run_agrif.log
```

```text
      12  9686.04167 ...      <- parent
      36  9686.04167 ...      <- child, locked
```

If they diverge, stop the run (`pkill -f "croco croco.in"`), fix `dt`, and start again.

!!! note
    The operational driver does this arithmetic for you — `DT_CHD=$(( DT / COEF ))` in `run_forecast_cycle.sh`. These edits are for the hand-built run; once the driver takes over, it patches `croco.in.1` on every cycle.