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

``` { .text .no-copy }
        CANARY_12 FORECAST
```

Cosmetic, but keeps configs identifiable.

### 11.2 — The S-coordinate (check it matches)

`Ctrl-W`, `S-coord`, Enter. The line below should read:

``` { .text .no-copy }
           7.0d0     2.0d0      200.0d0
```

Three numbers — `theta_s`, `theta_b`, `hc` — that shape the **vertical grid**. CROCO does
not use fixed depth levels; it uses terrain-following sigma levels, which stretch from the
surface to the sea floor so every column has the same number of levels whether the water
is 20 m or 4000 m deep. These three control how that stretching is distributed.

| | |
|---|---|
| **`theta_s = 7`** | surface stretching. Higher packs more levels near the surface, where the thermocline and the wind-driven layer are. 7 is strong packing. |
| **`theta_b = 2`** | bottom stretching. Higher also packs levels near the sea floor, for the bottom boundary layer. 2 is moderate. |
| **`hc = 200`** | the depth in metres above which the surface packing applies in full. Below it the levels spread out. |

`d0` is Fortran for a double-precision constant — `7.0d0` is just `7.0`.

**Confirm** it reads `7.0 / 2.0 / 200.0`, because these **must equal** your `sigma_params`
from Step 4. The initial and boundary files were built on that vertical grid; if
`croco.in` describes a different one, the model interpolates onto levels its inputs were
never written for. The template usually already has these — check, don't assume.

### 11.3 — The sponge

`Ctrl-W`, `X_SPONGE`, Enter. The line **below** the header shows `XXX  XXX`, which
CROCO cannot read. Set real numbers:

``` { .text .no-copy }
                    0.                0.
```

**What:** the sponge is a viscosity band near the open boundaries that absorbs
outgoing waves so they don't reflect back inward. `0.  0.` turns it off. **Why zero
here:** the parent product is at the same resolution as the model, so the boundary
mismatch is small and CROCO's radiation conditions handle it on their own.

If you see energy building up along an open edge, turn it on: `50000.  400.` gives a
50 km band (≈5–6 cells at 1/12°) with a peak viscosity of 400 m²/s. Finer grids use
smaller numbers.

### 11.4 — The timestep (read it, don't change it)

`Ctrl-W`, `time_stepping`, Enter. The driver sets this line per run, so leave it as it
is — but it decides whether the model is stable, so it is worth knowing what it says:

``` { .text .no-copy }
time_stepping: NTIMES   dt[sec]  NDTFAST  NINFO
                2016     300       60      1
```

**What:** CROCO advances on two clocks. Surface gravity waves travel at √(gH) — around
200 m/s in deep water — and following them needs a short step. Currents, temperature and
salinity move at metres per second and can take a much longer one. So the fast motions
(the **barotropic** mode) and the slow ones (the **baroclinic** mode) are stepped
separately.

| | |
|---|---|
| **`dt`** | the slow (baroclinic) step, in seconds |
| **`NDTFAST`** | how many fast (barotropic) steps fit inside one slow step |
| **`NTIMES`** | how many slow steps to take — this sets the run length |
| **`NINFO`** | how often to print a diagnostic line; `1` is every step |

At `dt=300` and `NDTFAST=60`, the fast mode advances every 5 seconds and everything else
every 5 minutes.

**`NTIMES` and `dt` are coupled:**

``` { .text .no-copy }
NTIMES = run length in seconds / dt
```

Seven days at `dt=300` is 7 × 86400 / 300 = **2016**. Change `dt` and `NTIMES` must
change with it, or the run covers a different period than you meant — the same seven
days at `dt=600` needs 1008.

**The CFL condition.** Named for Courant, Friedrichs and Lewy, who set it out in 1928.
The idea is simple: **nothing the model carries may travel more than one grid cell in one
timestep.** If a wave crosses two cells while the scheme only looks at neighbours, the
scheme cannot follow it, and the error grows every step until the run fails.

The **Courant number** measures how close you are:

``` { .text .no-copy }
C = wave speed × timestep / cell size
```

At `C = 1` a wave crosses exactly one cell per step, which is the limit. Below it the
scheme can follow; above it the run blows up, as NaNs or `MAIN: BLOW UP` in the log.

Here the binding constraint is the fast mode, because gravity waves are the fastest thing
in the model. Check yours:

```bash
cd ${CF}
conda activate seaforward

python3 << 'PYEOF'
import numpy as np, xarray as xr

g  = xr.open_dataset('croco_grd.nc')
dx = 1.0 / np.maximum(g.pm.values, g.pn.values)      # the smaller cell spacing
c  = np.sqrt(9.81 * g.h.values)                       # gravity-wave speed

dt, ndtfast = 300.0, 60                               # your croco.in values

print('fast step  : %.1f s   (dt / NDTFAST)' % (dt / ndtfast))
print('slow step  : %.0f s' % dt)
print('barotropic Courant : %.2f' % np.nanmax(c * (dt / ndtfast) / dx))
print('baroclinic Courant : %.2f' % np.nanmax(2.0 * dt / dx))
PYEOF
```

Keep it below about **0.7** — a conventional working margin rather than a hard threshold.

**A finer grid needs a smaller `dt`**: at 1/25° the cells are half the size, so the same
timestep doubles the Courant number.

A comfortable number is not an invitation to raise `dt` as far as it allows. CFL is
necessary for stability, not sufficient — the vertical scheme, the advection scheme and
steep terrain-following coordinates impose their own limits this calculation does not
capture. If you do raise it, run a short test and compare the kinetic energy against the
shorter step before trusting it.

Save (`Ctrl-O`, Enter), exit (`Ctrl-X`), and confirm no placeholder remains:

```bash
grep -n "XXX" ${CONFIG_DIR}/croco.in && echo "STILL HAS XXX — fix it" || echo "no XXX left — good"
```

!!! note
    The `initial`, `boundary` and `online` lines are set at run time ([Phase 3](../phase3/03_forecast.md)). The `diagnostics`, `floats`, `stations`, `psource`, `sediment`, `biology` and `wkb_*` sections are inert unless their CPP switch is on, so you can ignore them for this configuration.