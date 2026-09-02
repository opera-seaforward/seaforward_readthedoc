### Upstream data — the sources

The chain begins with the global datasets a regional model cannot produce for itself.
SEA-FORWARD uses the standard set, each supplying one class of input:

| upstream source | SEA-FORWARD product | role |
|---|---|---|
| Parent ocean model | **Mercator** (forecast) / **GLORYS** (hindcast), global 1/12° | initial and boundary conditions |
| Atmospheric forcing | **GFS** (forecast) / **ERA5** (hindcast) | surface forcing |
| Tidal atlas | **TPXO** | tidal forcing (Phase 10) |
| River discharge | **Dai & Trenberth climatology** | coastal freshwater (Phase 11) |
| Bathymetry and coastline | **ETOPO2 + GSHHS** | the model grid |
| Ocean observations | tide gauges, altimetry, Argo | validation |

These are the inputs to the system owner's facility — the left edge of the value chain.

### The system owner's facility — where the model runs

Everything inside SEA-FORWARD's compute environment plays the role the guide assigns to
the system owner's facility. It has two parts.

**Storage** holds the durable artifacts: the grid, the downloaded forcings, the CROCO
source, and — critically for operation — the **restart files** carrying the ocean state
from one cycle to the next.

**A single, reproducible compute environment** holds the running system. The Architecture
Guide stresses that an operational system should run in one controlled, reproducible
environment; SEA-FORWARD realises this as a pinned `conda` environment plus a
purpose-built NetCDF stack (`env.sh`, `opt_seq`). Inside it live:

- **the model configuration** — `cppdefs.h`, `param.h`, `croco.in` and the grid
  dimensions, which together define exactly what the compiled model is;
- **the forecast driver** — `run_forecast_cycle.sh`, which orchestrates the daily cycle:
  download, prepare, spin up, forecast;
- **validation** — the input-consistency checks before a run and the comparisons after
  it;
- **history and restart output** — the forecast fields, and the restart that seeds the
  next cycle.

### The forecast — interoperable output

The engine produces **CROCO NetCDF** history and average files, written with CF-style
metadata: variables carry `long_name`, `units` and `standard_name` attributes, and the
grid carries its coordinates. Anyone downstream can open the output with standard tools
— `xarray`, `ncview`, CDO — without knowing how it was produced.

Interoperability is the property the Architecture Guide places at the centre of the
design, and it is worth being precise about what has been shown. The output *is* NetCDF
with CF-style attributes, which is what the tooling in Phase 5 relies on. Whether it
passes a formal CF compliance check has not been tested here, and doing so would be a
worthwhile step toward the guide's standard.

### Downstream — visualization, analysis, users

On the downstream side, SEA-FORWARD acts — as the guide allows — as its own downstream
provider:

- **visualization and analysis** — the `sftools` post-processing toolkit of Phase 5:
  maps, sections, profiles, Hovmöllers, time series and animations, plus the parent
  comparisons;
- **derived products and indicators** — the extensible layer where intermediate users
  build on the output;
- **access for end users** — either to the derived products, or by pulling the
  components from the repository.

### The repository — how the system is reproduced

Underpinning all of it is the **`opera-seaforward/seaforward` repository**. In the
guide's terms it is what makes the system *reproducible* rather than merely *runnable*:
the storage layout, the preprocessing tools, the environment and model configuration,
the forecast driver and the post-processing all come from one versioned source. Anyone
can reconstruct any component from it.