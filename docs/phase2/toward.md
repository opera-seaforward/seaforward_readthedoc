## Running it operationally — the driver

The manual sequence you followed — download, prepare ini/bry/forcing, patch `croco.in`,
run — is wrapped in a single driver that does the whole two-phase cycle for today without
intervention, and can be put on a schedule. Nothing is rebuilt: it reuses the compiled
model and grid you just made, and each cycle refreshes only the boundaries and atmosphere
from the latest global products.

A short settings block at the top adapts it to a configuration — the config name, the
spin-up and forecast lengths, the download box, and whether the GFS longitude fix applies.
These are the only lines that change for a new region, and they must match what you built
here, or the driver runs the wrong domain.

Each cycle lands in its own dated folder:

``` { .text .no-copy }
forecast/model-runs/Canary_12/<date>_<build>/
├── spinup/     # the 2-day spin-up (produces croco_rst.nc)
└── fcst/       # the 5-day forecast — what you keep
    └── CROCO_FILES/
        ├── croco_his.nc     # forecast history (what you plot)
        └── croco_avg.nc     # forecast time-averages
```

The built config stays in `forecast/scratch/<CONFIG>/` — the workbench, reused every
cycle. Each day's output goes to `forecast/model-runs/<CONFIG>/<date>_<build>/`, the
results you keep.

## The optional physics — tides, nesting and rivers

The same driver carries three optional extensions as flags, so they are selected at launch
rather than kept as separate scripts: tidal forcing, river freshwater forcing, and an
AGRIF nest running one-way or two-way. The flags are independent and compose.

Because all three are **compile-time** features, each combination needs its own binary,
and the driver selects one by name from the flags you give it. That is why the folder
above is named `<date>_<build>`: the suffix records which build produced it.

This chapter's plain forecast is the base; the flags layer physics on top.

---

**[Phase 3 — Running a Forecast](../phase3/03_forecast.md)** covers all of this as a
working procedure: preparing the binaries, the settings block, launching a cycle,
scheduling it, and the output layout in full. Tides are built in
[Phase 10](../phase10/10_tides.md), rivers in [Phase 11](../phase11/11_rivers.md), and
AGRIF nesting in [Phase 8](../phase8/08_agrif.md).