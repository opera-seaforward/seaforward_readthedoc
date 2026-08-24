Tides fold into the forecast driver as a runtime flag, `--tides`, that composes
with the existing child axis. Two independent choices:

```
--child none|1way|2way     no nest / one-way AGRIF / two-way AGRIF
--tides                     add TPXO tidal forcing
```

giving a 2×3 matrix, one pre-built binary per cell (both AGRIF and TIDES are
compile-time):

```
                no tide            with tide
no child        croco_plain        croco_plain_tides
child 1-way     croco_1way         croco_1way_tides
child 2-way     croco_2way         croco_2way_tides
```

```bash
./run_forecast.sh                        # parent only, no tide
./run_forecast.sh --tides                # parent only, with tide
./run_forecast.sh --child 1way           # nest, no tide
./run_forecast.sh --child 1way --tides   # nest + tide
./run_forecast.sh --child 2way --tides   # the full thing
```

### What `--tides` does inside the driver

1. **Generates the tide file(s) per cycle** at the spin-up start date. Parent
   grid → `croco_frc.nc`. When a child is present, a *second* generation on the
   child grid → `croco_frc.nc.1` (see below). These run before the ICs, in their
   own gen directories, exactly like the child IC.

2. **Stages** the frc file(s) into both the spin-up and forecast run dirs. The
   *same* file serves both phases — the harmonics are time-independent, and the
   phase epoch (set at generation) is what matters, so there is no need to
   regenerate between spin-up and forecast.

3. **Retimes the output** to hourly history / daily average, as Step 5 requires.
   Without `--tides` it stays 6 h / 6 h.

4. **Selects the tide binary** and wires `croco_frc.nc` into the `forcing:` line
   of `croco.in` (and `croco_frc.nc.1` into `croco.in.1` for the child).

Everything is matrix-aware: the tide guards (TPXO directory present, tide param
file present) only fire when `--tides` is set, and the child tide gen only when a
child is also present.

### Why the child needs its own tide file

Under AGRIF, each grid reads its own forcing files, and AGRIF appends `.1` to the
child's filenames. CROCO sets the tide file name from the `forcing:` keyword
(confirmed in `read_inp.F`), and the child's `SSH_TIDES`/`UV_TIDES` boundary code
needs the harmonic constituents **on the child grid** to apply them at its open
edges. So `--tides --child` builds two tide files:

- `croco_frc.nc`   — parent grid
- `croco_frc.nc.1` — child grid

parallel to the two initial conditions (`croco_ini.nc` and `croco_ini.nc.1`). The
somisana operational AGRIF config (their C11) confirms the child compiles with
the same `TIDES`/`SSH_TIDES`/`UV_TIDES` block as a standalone run — the child is
a full tidal model on its own grid, not a passive recipient of the parent's tide.