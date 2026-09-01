`croco.in` is CROCO's runtime settings file — timestep, dates, which files to read,
what to output. With AGRIF, **each grid gets its own**: the parent reads `croco.in`,
the child reads `croco.in.1`. You launch only the parent's; AGRIF finds the child's
automatically via `AGRIF_FixedGrids.in`.

Start from a copy of the parent's, because the child should share its physics, its
output settings, and its forcing — you're changing only what's genuinely per-grid.
(CROCO also ships a reference at `code/croco/OCEAN/croco.in.1` if you want to compare.)

```bash
cd ~/seaforward/forecast/scratch/IGOG_AGRIF
cp croco.in croco.in.1
nano croco.in.1
```

Six edits follow. Take them in order.

### 5a — the title

`Ctrl+W` `title` `Enter`. The cursor lands on line 1. The line **below** it is the
title text:

```
title:
        IGOG_12 FORECAST                       <- change this
```

to

```
title:
        IGOG_12 AGRIF ZOOM LEVEL 1 (Sao Tome)
```

Cosmetic, but it's how you tell the two grids apart in the log — CROCO prints each
grid's title as it initialises. Worth doing.

### 5b — the timestep ⚠️

`Ctrl+W` `time_stepping` `Enter`. **Careful — there are two matches.** The first is
the one you want:

```
time_stepping: NTIMES   dt[sec]  NDTFAST  NINFO
                 288       300      60      1     <- this line
time_stepping_nbq: NDTNBQ    CSOUND_NBQ    VISC2_NBQ    <- NOT this one
```

Change `300` to `100` and **leave `288` alone**:

```
                 288       100      60      1
```

See the warning below for why. This is the single most important edit in the chapter.

### 5c — the grid file

`Ctrl+W` `grid:` `Enter`:

```
grid:  filename
    CROCO_FILES/croco_grd.nc          <- add .1
```
→
```
grid:  filename
    CROCO_FILES/croco_grd.nc.1
```

### 5d — the boundary file: delete it

`Ctrl+W` `boundary:` `Enter`:

```
boundary: filename
    CROCO_FILES/croco_bry.nc          <- replace with the placeholder
```
→
```
boundary: filename
      XXXXXXXXX
```

`XXXXXXXXX` is a deliberate non-existent filename — CROCO's way of saying "this
section is unused". **AGRIF supplies the child's boundaries every barotropic step;
there is no child bry file.** This is the whole point of online nesting, and it's the
line that most clearly distinguishes AGRIF from the Phase 7 offline nest, where the
bry file *was* the entire mechanism.

Do the same for `climatology:` if your parent has one.

### 5e — the initial file

`Ctrl+W` `initial:` `Enter`:

```
initial: NRREC / filename
          1
    CROCO_FILES/croco_ini.nc          <- add .1
```
→ `CROCO_FILES/croco_ini.nc.1`

### 5f — the output files

Three more: `Ctrl+W` `history:`, then `averages:`, then `restart:`. Each has a
filename on the line below — append `.1` to all three:

```
    CROCO_FILES/croco_his.nc.1
    CROCO_FILES/croco_avg.nc.1
    CROCO_FILES/croco_rst.nc.1
```

If you skip these, the child writes into the parent's output files and you lose both.

Save and exit: `Ctrl+O` `Enter`, `Ctrl+X`.

### Verify

```bash
grep -nE -A1 "^title:|^time_stepping:|^grid:|^boundary:|^initial:|^history:" croco.in.1 | head -20
```

Expected:

```
1:title:
2-        IGOG_12 AGRIF ZOOM LEVEL 1 (Sao Tome)
3:time_stepping: NTIMES   dt[sec]  NDTFAST  NINFO
4-                 288       100      60      1
22:grid:  filename
23-    CROCO_FILES/croco_grd.nc.1
30:boundary: filename
31-      XXXXXXXXX
32:initial: NRREC / filename
33-          1
39:history: LDEFHIS, NWRT, NRPFHIS / filename
```

Filenames are **explicit** — AGRIF does not append `.1` for you.

### ⚠️ The dt / NTIMES asymmetry

This is the nastiest gotcha in the chapter, because **getting it wrong doesn't
fail**. The run completes, both grids report `MAIN: DONE`, and the answer is wrong.

The asymmetry:

- **AGRIF multiplies the child's `NTIMES` by `timeref`.** You write 288; AGRIF runs
  864. Do **not** pre-multiply it yourself.
- **AGRIF does *not* divide the child's `dt`.** It uses whatever you wrote. You must
  set it to `dt_parent / timeref` by hand.

So for a parent at `288 × 300` with `timeref = 3`:

```
parent croco.in    :  288    300      -> 288 steps x 300 s = 1 day
child  croco.in.1  :  288    100      -> AGRIF runs 864 x 100 s = 1 day  ✓
```

Leave `dt = 300` in the child and you get 864 × 300 s = **3 days** while the parent
runs 1. The child races ahead, pulling atmospheric forcing from two days in the
parent's future, and finishes "successfully".

The symptom, if you go looking:

```
715  9690.48264   <- child, day 9690.5
238  9688.82639   <- parent, day 9688.8      1.65 days apart
ONLINE_BULK -- Read file for time = 9690.    <- child reading future GFS
```

**Verify the clocks in the log after starting the run.** Parent step 30 and child step 90 must report the *same* time:

```bash
grep -E "^ +(25|75) +9688\." run_1way.log
```
```
25  9688.08681     <- parent
75  9688.08681     <- child  ✓ locked
```

If they diverge, stop the run (`pkill -f "croco croco.in"`), fix `dt`, start again.