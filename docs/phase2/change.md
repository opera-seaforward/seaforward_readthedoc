When you build a different region, these are the only things that differ:

| Step / file | What you change | Set from |
|---|---|---|
| Step 0 | `CONFIG_NAME`, box, `EXTENTS` | your chosen region |
| Step 3 | which boundaries are open/closed | the land mask |
| Step 4 `crocotools_param.py` | `obc_dict`, `sigma_params`, `inputdata` | Step 3 + your vertical choice |
| Step 7 `cppdefs.h` | config name, `OBC_*`, forcing switch | Steps 0 and 3 |
| Step 8 `param.h` | `LLm0`, `MMm0`, `N` | Step 2 grid size |
| Step 9 `jobcomp` | `SOURCE1` | your CROCO source path |
| Step 11 `croco.in` | title, sponge (S-coord to match) | your setup |

Everything else — downloading data, building the grid, compiling — is the same
every time.

And the **upstream-data choices** — the sources from "What feeds your model"
above — set for this forecast build:

| choice | this guide | notes |
|---|---|---|
| global ocean forecast | Mercator (`inputdata='mercator'`) | analysis + forecast, the ocean you refine |
| atmosphere | GFS (default format) | the global weather forecast |
| tides | off (`TIDES` undef) | add TPXO tides → Phase 10 (`# define TIDES` + `make_tides`) |
| rivers | off | future addition (GloFAS) |
| bathymetry | ETOPO2 + GSHHS | no choice — always, at grid build |

For *this* forecast build you leave all of these at their defaults — Mercator, GFS, no tides. The point of the table is that when your goal changes (a historical run, a shelf where tides matter), you now know exactly which upstream source to swap and where.