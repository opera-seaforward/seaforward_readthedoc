Once the manual run works, wrap Steps 3–7 in a driver so one command produces a
nested forecast. It's a sibling of the parent's `run_forecast_today.sh`, with two
deliberate differences: **no spin-up** (a single forecast run from the nested IC),
and the **ocean comes from the parent** (convert + make_ini/make_bry) instead of a
Mercator download. The atmosphere reuses the parent's GFS.

**Prerequisite — run the parent first.** The child needs the parent's output, so the
driver is on-demand and chained, not scheduled:
```bash
cd ~/seaforward/forecast
./run_forecast_today.sh     # 1) the 1/12° parent (produces croco_his.nc + GFS)
./run_nest_today.sh         # 2) the 1/25° child, nested inside it
```

**Running so it survives a closed terminal or a sleeping laptop.** These runs take a
while (the child especially), so run them **in the background with a log file** using
`nohup`. That detaches the job from your terminal — it keeps going if the terminal
closes, and the output is captured to a log you can watch:

```bash
cd ~/seaforward/forecast
# parent first, in the background, logging to a timestamped file
nohup ./run_forecast_today.sh > run_parent_$(date -u +%Y%m%d).log 2>&1 &
# then the child (wait for the parent to finish first, or chain with &&)
nohup ./run_nest_today.sh     > run_nest_$(date -u +%Y%m%d).log   2>&1 &

# watch progress live (Ctrl-C just stops watching, not the run):
tail -f run_nest_$(date -u +%Y%m%d).log
```

- `nohup … &` runs the script detached and in the background, so closing the
  terminal (or logging out) doesn't kill it.
- `> file 2>&1` sends both normal output and errors to the log file.
- `tail -f file` follows the log live; press `Ctrl-C` to stop watching — the run
  keeps going.
- To run them **in sequence** unattended (child only after the parent finishes), chain
  with `&&`:
  ```bash
  nohup bash -c './run_forecast_today.sh && ./run_nest_today.sh' \
      > run_chain_$(date -u +%Y%m%d).log 2>&1 &
  ```

> **A sleeping laptop still pauses the run.** `nohup` survives a *closed terminal*,
> but if the computer actually **suspends/sleeps**, the CPU stops and the run pauses
> until you wake it (then it resumes). To run through a lid-close, either keep the
> machine awake (disable sleep, or `caffeinate`/`systemd-inhibit` on some systems) or
> run on a machine that stays on. For long jobs, a terminal multiplexer like `tmux`
> or `screen` is also handy: start `tmux`, launch the run, detach with `Ctrl-b d`,
> and reattach later with `tmux attach` — the run keeps going in between.

!!! warning
    ⚠️ **Run only ONE instance at a time.** If you launch the driver again while a previous run (or a stray background job) is still going, the two instances write to the same files (`parent_<date>.nc`, the ini/bry) at once and collide — producing confusing errors that look like bugs but are just two runs stepping on each other (e.g. spurious `Invalid datetime` or half-written files). Before starting a fresh run, check for and clear any leftovers:
    ```bash
    # see what's running
    ps aux | grep run_nest_today.sh | grep -v grep
    jobs
    # if one is still going and you want to replace it:
    pkill -f run_nest_today.sh; sleep 1   # kill it, then launch the new one
    ```
    `pkill -f` matches the whole command line, so it catches `nohup ./run_nest_today.sh`,
    `bash run_nest_today.sh`, etc.; `sleep 1` gives it a moment to die before you relaunch.


**The flow (6 steps):**

```
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
The parent ran today, so the child runs today's window too; there's nothing to read
from files. The only nesting-specific parts are the ocean source (the parent's
output, converted) and reusing the parent's per-cycle GFS.

**Key CONFIG block (edit for your setup):**
```bash
CONFIG_NAME=Canary_25        # the child
PARENT_CONFIG=Canary_12      # the parent it nests inside
FDAYS=4                      # forecast length (inside the parent's 5-day window)
DT=150                       # child timestep (half the parent's 300, for CFL)
YORIG=2000                   # forecast track
NP=7                         # MPI ranks
```

**Why it uses the parent's per-cycle GFS.** The child runs the same window as the
parent, so it must read the **same GFS the parent's forecast used** (the per-cycle
copy under `model-runs/<parent>/<date>/`), which covers the full window. A stale
`scratch/<parent>/…` GFS may be shorter and cut the child off early with
`ONLINE_GET_BULK ... dataset ... missing`. Step [1/6] uses the per-cycle folder and
fails clearly if it's absent (no silent fallback to scratch).

**Scheduling.** This is meant to be run **on demand** (parent, then child), not from
cron — the nested run is ~9× the parent's cost and you usually want to watch it.
If you ever need it daily, wrap the two calls in a cron job; the driver itself
doesn't change.

!!! note
    **Environment notes baked into the driver.** It sources `env.sh` + `track.sh`, pins `OUTPUT_ROOT` the way the parent driver does, and activates conda with `source ${CONDA_BASE}/bin/activate seaforward` (not `conda activate`, which needs `conda init` and fails inside a script). It runs the prepro under conda, then runs `croco` outside conda so the linker uses `opt_seq` NetCDF.

## Nesting a hindcast cycle (no separate driver — here's why)

Everything above nests a **forecast**. You can nest a **hindcast** too, and it uses
the *same* tools — but there is deliberately **no `run_nest_*` driver** for it, and
the reason is worth understanding.

A forecast is a **live, repeating** operation: you run it for "today", every day, so
an operational driver (and, if you like, cron) earns its place. A hindcast is a
**one-off reconstruction**: you pick a past period, run it once, analyse it, done.
There is no "today's hindcast" to schedule — so there's nothing for a hindcast
driver to automate that a deliberate manual run doesn't already cover. Automation is
a forecasting concept; reconstruction is a choose-your-cycle concept.

So to nest a hindcast, do the **same manual steps** (Steps 3–7), choosing a cycle and
making three swaps you already know from Phase 4 (Hindcast):

| What | Forecast nest | Hindcast nest |
|---|---|---|
| Which parent | today's forecast cycle | a **chosen** past cycle you've run (e.g. `20251225`) |
| Time origin | `Yorig=2000` | **`Yorig=1993`** |
| Atmosphere | GFS `for_croco` | the cycle's **GFS** `for_croco` |
| Parent path | `model-runs/Canary_12/<tag>/fcst/...` | `model-runs/Canary_12/<tag>/hcast/...` |

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
**GFS** `for_croco` folder — the per-cycle copy the parent hindcast actually used,
which covers the cycle's full window (the same "use the parent's per-cycle forcing"
point as the forecast). The child's run_date is simply the chosen cycle's date (the
one you pass to make_ini/make_bry above), just as the forecast child uses today's
date.

!!! note
    The converter (`nesting.py`) and the validation tools (`compare_resolution`, etc.) are **`Yorig`-agnostic** — they already handle hindcasts; you just pass `Yorig=1993`. Only the *operational driver* is forecast-specific, by design.

## What changes for the next rung (1/50°) or a new region

The resolution ladder is the same recipe each rung:

| Step | 1/12°→1/25° | Next rung 1/25°→1/50° |
|---|---|---|
| Grid | `make_grid_config.py Canary_25 … 1/25` | `… Canary_50 … 1/50`, box inside Canary_25 |
| Vertical | `N=75` | `N=100` (if desired) |
| Convert | Canary_12 output → Mercator | Canary_25 output → Mercator |
| ini/bry | from converted 1/12° | from converted 1/25° |
| Timestep | `dt=150` (half of 300) | `dt=75` (half of 150) |
| param.h | `CANARY_25` 148×236×75 | `CANARY_50` … |

Each child nests inside its immediate parent, takes that parent's output as its
ocean source, halves the timestep, and shrinks the box slightly to sit inside.

## The consistency rules (nesting edition)

The Phase-2 rules still hold, plus one nesting-specific rule:

1. **Grid size:** `croco_grd.nc` → `param.h` (`LLm0=xi_rho−2`, `MMm0=eta_rho−2`).
2. **Vertical grid:** `sigma_params` N = S-coord = `param.h` N (here, **75**).
3. **Boundaries:** mask = `obc_dict` = `OBC_*` (child inherits the parent's).
4. **Nesting geometry:** the child box sits **inside** the parent, and the parent
   output is converted to Mercator format **with the parent's `Yorig`** (forecast
   2000, hindcast 1993) before make_ini/make_bry.
5. **Timestep:** child `dt` ≈ parent `dt` × (child `dl` / parent `dl`) — roughly
   halved per resolution doubling, for CFL stability.