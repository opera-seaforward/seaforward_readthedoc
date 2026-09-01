Once the manual run works, wrap Steps 3–7 in a driver so one command produces a
nested forecast. It's a sibling of the parent's `run_forecast_cycle.sh`, with two
deliberate differences: **no spin-up** (a single forecast run from the nested IC),
and the **ocean comes from the parent** (convert, then make_ini/make_bry) instead of
a Mercator download. The atmosphere reuses the parent's GFS.

**Prerequisite — run the parent first.** The child needs the parent's output, so the
driver is on-demand and chained, not scheduled:

```bash
cd ~/seaforward/forecast
./run_forecast_cycle.sh     # 1) the 1/12° parent (produces croco_his.nc + GFS)
./run_nest_today.sh         # 2) the 1/25° child, nested inside it
```

!!! warning
    **The nesting driver expects an untagged parent folder.** It looks for `model-runs/<parent>/<date>/fcst/`, but the forecast driver now writes `<date>_plain` (or `<date>_plain_tides`, and so on). Until the two are reconciled, either rename the parent's output folder to the bare date, or run Steps 3–7 by hand as above.

## Running it so it survives a closed terminal

These runs take a while — the child especially — so run them in the background with
a log file, using `nohup`. That detaches the job from your terminal: it keeps going
if the terminal closes, and the output is captured to a log you can watch.

```bash
cd ~/seaforward/forecast
# parent first, in the background, logging to a timestamped file
nohup ./run_forecast_cycle.sh > run_parent_$(date -u +%Y%m%d).log 2>&1 &
# then the child (wait for the parent to finish, or chain with &&)
nohup ./run_nest_today.sh     > run_nest_$(date -u +%Y%m%d).log   2>&1 &
# watch progress live (Ctrl-C stops watching, not the run)
tail -f run_nest_$(date -u +%Y%m%d).log
```

- `nohup … &` runs the script detached and in the background, so closing the terminal
  or logging out doesn't kill it.
- `> file 2>&1` sends both normal output and errors to the log.
- `tail -f file` follows the log live; `Ctrl-C` stops watching while the run
  continues.
- To run them in sequence unattended, so the child starts only after the parent
  finishes, chain with `&&`:

```bash
    nohup bash -c './run_forecast_cycle.sh && ./run_nest_today.sh' \
        > run_chain_$(date -u +%Y%m%d).log 2>&1 &
```

!!! note
    **A sleeping laptop still pauses the run.** `nohup` survives a closed terminal, but if the machine actually suspends, the CPU stops and the run pauses until you wake it — then resumes. To run through a lid-close, either keep the machine awake (disable sleep, or use `caffeinate` / `systemd-inhibit`) or use a machine that stays on. For long jobs a terminal multiplexer helps too: start `tmux`, launch the run, detach with `Ctrl-b d`, and reattach later with `tmux attach`.

!!! warning
    **Run only one instance at a time.** Launch the driver again while a previous run is still going and the two write to the same files — `parent_<date>.nc`, the ini and bry — at once. The collisions produce errors that look like bugs but are just two runs stepping on each other: spurious `Invalid datetime`, half-written files. Before starting fresh, check for leftovers:

```bash
    # see what's running
    ps aux | grep run_nest_today.sh | grep -v grep
    jobs
    # if one is still going and you want to replace it
    pkill -f run_nest_today.sh; sleep 1
```

    `pkill -f` matches the whole command line, so it catches `nohup ./run_nest_today.sh` and `bash run_nest_today.sh` alike; `sleep 1` gives it a moment to die before you relaunch.

## What the driver does

```text
[1/6] locate today's parent output  →  fail clearly if the parent hasn't run
      └─ point at the parent's PER-CYCLE GFS (model-runs/<parent>/<date>/…),
         not the scratch copy, so the child gets the full forecast window
[2/6] convert parent croco_his.nc  →  Mercator-format parent_<date>.nc   (nesting.py)
[3/6] make_ini + make_bry from the converted parent   (child N=75, hdays=0)
[4/6] stage the run dir  (grid, ini/bry, config, the compiled child)
[5/6] patch croco.in     (NTIMES from FDAYS/dt, NEST files, per-cycle GFS path)
[6/6] run the child      →  croco_his.nc
```

The date is simply **today** — the same `date -u +%Y%m%d` the forecast driver uses.
The parent ran today, so the child runs today's window too; there is nothing to read
from files. The only nesting-specific parts are the ocean source (the parent's
output, converted) and reusing the parent's per-cycle GFS.

**The settings block, to edit for your setup:**

```bash
CONFIG_NAME=Canary_25        # the child
PARENT_CONFIG=Canary_12      # the parent it nests inside
FDAYS=4                      # forecast length (inside the parent's 5-day window)
DT=150                       # child timestep (half the parent's 300, for CFL)
YORIG=2000                   # forecast track
NP=7                         # MPI ranks
```

**Why it uses the parent's per-cycle GFS.** The child runs the same window as the
parent, so it must read the **same GFS the parent's forecast used** — the per-cycle
copy under `model-runs/<parent>/<date>/`, which covers the full window. A stale
`scratch/<parent>/…` copy may be shorter and cut the child off early with
`ONLINE_GET_BULK ... dataset ... missing`. Stage [1/6] uses the per-cycle folder and
fails clearly if it's absent, with no silent fallback to scratch.

**Scheduling.** This is meant to be run on demand — parent, then child — rather than
from cron. The nested run costs roughly nine times the parent and you usually want to
watch it. If you do need it daily, wrap the two calls in a cron job; the driver
itself doesn't change.

!!! note
    **Environment handling baked into the driver.** It sources `env.sh` and `track.sh`, pins `OUTPUT_ROOT` the way the parent driver does, and activates conda with `source ${CONDA_BASE}/bin/activate seaforward` rather than `conda activate`, which needs `conda init` and fails inside a script. It runs the pre-processing under conda, then runs `croco` outside it so the linker uses `opt_seq`'s NetCDF.

## Nesting a hindcast cycle

Everything above nests a **forecast**. You can nest a **hindcast** too, using the
same tools — but there is deliberately **no `run_nest_*` driver** for it, and the
reason is worth understanding.

A forecast is a live, repeating operation: you run it for "today", every day, so an
operational driver earns its place. A hindcast is a one-off reconstruction: you pick
a past period, run it once, analyse it, and you're done. There is no "today's
hindcast" to schedule, so there is nothing for a hindcast driver to automate that a
deliberate manual run doesn't already cover.

So to nest a hindcast, do the same manual steps (3–7), choosing a cycle and making
three swaps you already know from Phase 4:

| What | Forecast nest | Hindcast nest |
|---|---|---|
| Which parent | today's forecast cycle | a **chosen** past cycle you've run, e.g. `20251225` |
| Time origin | `Yorig=2000` | **`Yorig=1993`** |
| Atmosphere | GFS `for_croco` | the cycle's **ERA5** `for_croco` |
| Parent path | `model-runs/Canary_12/<tag>/fcst/…` | `model-runs/Canary_12/<tag>/hcast/…` |

Concretely, to nest the `20251225` hindcast cycle:

```python
# Step 3 — convert the HINDCAST parent (note Yorig=1993)
import sftools.nesting as nest
nest.croco_to_mercator(
    ".../hindcast/model-runs/Canary_12/20251225/hcast/CROCO_FILES/croco_his.nc",
    "${FCAST}/downloaded_data/PARENT/parent_20251225.nc", Yorig=1993)
```

```bash
# Step 4 — make_ini/make_bry from it (Yorig 1993; run_date = the cycle's start)
python seaforward.py make_ini --input_file .../parent_20251225.nc --output_dir ${CF} \
    --run_date "2025-12-25 00:00:00" --hdays 0 --Yorig 1993
python seaforward.py make_bry --input_file .../parent_20251225.nc --output_dir ${CF} \
    --run_date "2025-12-25 00:00:00" --hdays 0 --fdays 5 --Yorig 1993
```

Then Steps 5–7 as before, with the child's `online:` block pointing at that cycle's
**ERA5** `for_croco` folder — the per-cycle copy the parent hindcast actually used,
which covers the full window. The child's run date is simply the chosen cycle's date.

!!! note
    The converter (`nesting.py`) and the validation tools are **`Yorig`-agnostic** — they already handle hindcasts, you just pass `Yorig=1993`. Only the operational driver is forecast-specific, by design.

## The next rung, or a new region

The resolution ladder is the same recipe each time:

| Step | 1/12° → 1/25° | Next rung, 1/25° → 1/50° |
|---|---|---|
| Grid | `make_grid_config.py Canary_25 … 1/25` | `… Canary_50 … 1/50`, box inside Canary_25 |
| Vertical | `N=75` | `N=100`, if you want it |
| Convert | Canary_12 output → Mercator | Canary_25 output → Mercator |
| ini/bry | from the converted 1/12° | from the converted 1/25° |
| Timestep | `dt=150`, half of 300 | `dt=75`, half of 150 |
| `param.h` | `CANARY_25` 148×236×75 | `CANARY_50` … |

Each child nests inside its immediate parent, takes that parent's output as its ocean
source, halves the timestep, and shrinks the box slightly to sit inside.

## The consistency rules, nesting edition

The Phase-2 rules still hold, plus two that are specific to nesting:

1. **Config name:** `cppdefs.h` = `param.h` — `CANARY_25` in both.
2. **Grid size:** `croco_grd.nc` → `param.h` (`LLm0 = xi_rho − 2`, `MMm0 = eta_rho − 2`).
3. **Vertical grid:** `sigma_params` N = S-coord = `param.h` N. Here, **75**.
4. **Boundaries:** mask = `obc_dict` = `OBC_*`, read from the *child's* mask.
5. **Nesting geometry:** the child box sits **inside** the parent, and the parent
   output is converted with the parent's own `Yorig` — 2000 for a forecast, 1993 for
   a hindcast — before make_ini and make_bry.
6. **Timestep:** child `dt` ≈ parent `dt` × (child spacing / parent spacing), so
   roughly halved per resolution doubling, for CFL stability.