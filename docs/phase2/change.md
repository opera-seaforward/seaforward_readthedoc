When you build a different region, these are the only things that differ:

| Step / file | What you change | Set from |
|---|---|---|
| Step 0 | `CONFIG_NAME`, box, `EXTENTS` | your chosen region |
| Step 3 | which boundaries are open/closed | the land mask |
| Step 4 `crocotools_param.py` | `obc_dict`, `sigma_params` | Step 3 + your vertical choice |
| Step 7 `cppdefs.h` | config name, `OBC_*` | Steps 0 and 3 |
| Step 8 `param.h` | `LLm0`, `MMm0`, `N` | Step 2 grid size |
| Step 11 `croco.in` | title, sponge (S-coord to match) | your setup |

Everything else — downloading data, building the grid, compiling, and the
`SOURCE1` path in `jobcomp` — is the same every time.

And the **upstream-data choices** — the sources from "What feeds your model"
above — set for this forecast build:

| choice | this guide | notes |
|---|---|---|
| global ocean | Mercator (`inputdata='mercator'`) | analysis + forecast, the ocean you refine |
| atmosphere | GFS (default format) | a hindcast uses ERA5 (`# define ERA_ECMWF`) → Phase 4 |
| tides | off (`TIDES` undef) | add TPXO tides → Phase 10 |
| rivers | off (`PSOURCE` undef) | add Dai & Trenberth runoff → Phase 12 |
| bathymetry | ETOPO2 + GSHHS | no choice — always, at grid build |

For *this* build you leave all of these at their defaults — Mercator, GFS, no tides,
no rivers. The point of the table is that when your goal changes — a historical run,
a shelf where tides matter, a delta where freshwater does — you know which upstream
source to swap and where.