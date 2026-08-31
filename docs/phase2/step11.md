![build progress](../img/runtime_input.png)

*Step 11 sets the **run-time inputs** in `croco.in` — dates, filenames, output intervals. Changing these needs no recompile.*

`croco.in` holds the model's run-time settings. You already compiled — this file is
read at *run* time, not compile time, which is why it comes after the build. Edit
the copy in your config folder:

```bash
nano ${CONFIG_DIR}/croco.in
```

### 11.1 — Title

`Ctrl-W`, `BENGUELA TEST`, Enter. Change the title line to your config's name:

```
        CANARY_12 FORECAST
```

Cosmetic, but keeps configs identifiable.

### 11.2 — The S-coordinate (check it matches)

`Ctrl-W`, `S-coord`, Enter. The line below should read:

```
           7.0d0     2.0d0      200.0d0
```

**Confirm** it's `7.0 / 2.0 / 200.0` — these are `theta_s / theta_b / hc`, and
they **must equal** your `sigma_params` from Step 4. The template usually already
has these — check, don't assume.

### 11.3 — The sponge

`Ctrl-W`, `X_SPONGE`, Enter. The line **below** the header shows `XXX  XXX`, which
CROCO cannot read. Set real numbers:

```
                    0.                0.
```

**What:** the sponge is a viscosity band near the open boundaries that absorbs
outgoing waves so they don't reflect back inward. `0.  0.` turns it off. **Why zero
here:** the parent product is at the same resolution as the model, so the boundary
mismatch is small and CROCO's radiation conditions handle it on their own.

If you see energy building up along an open edge, turn it on: `50000.  400.` gives a
50 km band (≈5–6 cells at 1/12°) with a peak viscosity of 400 m²/s. Finer grids use
smaller numbers.

Save (`Ctrl-O`, Enter), exit (`Ctrl-X`), and confirm no placeholder remains:

```bash
grep -n "XXX" ${CONFIG_DIR}/croco.in && echo "STILL HAS XXX — fix it" || echo "no XXX left — good"
```

!!! note
    The `time_stepping`, `initial`, `boundary` and `online` lines are set at run time (Phase 3). The `diagnostics`, `floats`, `stations`, `psource`, `sediment`, `biology` and `wkb_*` sections are inert unless their CPP switch is on, so you can ignore them for this configuration.