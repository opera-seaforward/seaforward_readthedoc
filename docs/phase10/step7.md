Tides fold into the forecast driver as a runtime flag, `--tides`, composing with the
existing child axis:

```text
--child none|1way|2way     no nest / one-way AGRIF / two-way AGRIF
--tides                    add TPXO tidal forcing
```

Both are compile-time in CROCO, so each combination needs its own pre-built binary:

```text
                no tide            with tide
no child        croco_plain        croco_plain_tides
child 1-way     croco_1way         croco_1way_tides
child 2-way     croco_2way         croco_2way_tides
```

```bash
./run_forecast_cycle.sh                        # parent only, no tide
./run_forecast_cycle.sh --tides                # parent only, with tide
./run_forecast_cycle.sh --child 1way           # nest, no tide
./run_forecast_cycle.sh --child 1way --tides   # nest + tide
./run_forecast_cycle.sh --child 2way --tides   # the full thing
```

The driver also takes `--rivers`, which extends the same scheme —
`croco_plain_tides_rivers` and so on. Phase 11 covers it.

### What `--tides` does inside the driver

1. **Generates the tide file(s) per cycle** at the spin-up start date. Parent grid →
   `croco_frc.nc`. When a child is present, a *second* generation on the child grid →
   `croco_frc.nc.1`. These run before the ICs, in their own gen directories, exactly
   like the child IC.

2. **Stages** the frc file(s) into both the spin-up and forecast run dirs. The *same*
   file serves both phases — the harmonics are time-independent and the phase epoch is
   set at generation, so there is no need to regenerate between them.

3. **Retimes the output** to hourly history and daily average, as Step 5 requires.
   Without `--tides` it stays 6 h for both.

4. **Selects the tide binary** and wires `croco_frc.nc` into the `forcing:` line of
   `croco.in`, and `croco_frc.nc.1` into `croco.in.1` for the child.

The guards are flag-aware: the TPXO directory and tide param file are only checked when
`--tides` is set, and the child tide generation only when a child is present too.

### Why the child needs its own tide file

Under AGRIF each grid reads its own forcing files, with `.1` appended for the child.
CROCO sets the tide file name from the `forcing:` keyword — confirmed in `read_inp.F` —
and the child's `SSH_TIDES` and `UV_TIDES` boundary code needs the harmonic
constituents **on the child grid** to apply them at its own open edges.

So `--tides --child` builds two tide files:

- `croco_frc.nc` — parent grid
- `croco_frc.nc.1` — child grid

parallel to the two initial conditions. The child is a full tidal model on its own
grid, not a passive recipient of the parent's tide.