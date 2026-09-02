### Upstream data — the sources

The chain begins with the global datasets a regional model cannot produce for
itself. SEA-FORWARD uses the standard set, each supplying one class of input:

| upstream source | SEA-FORWARD product | role |
|---|---|---|
| Parent ocean model | **Mercator / GLORYS** (global 1/12°) | initial + boundary conditions |
| Atmospheric forcing | **GFS** (forecast) / GFS (hindcast) | surface forcing |
| Tidal atlas | **TPXO** | tidal boundary forcing (optional) |
| Bathymetry + coastline | **ETOPO2 + GSHHS** | the model grid |
| Ocean observations | tide gauges, altimetry, Argo | validation |
| River discharge | *(GloFAS — future)* | coastal freshwater forcing |

These are the inputs to the system owner's facility. They are described in full in
the *Forcing and Upstream Data* chapter; here they are simply the left edge of the
value chain.

### The system owner's facility — where the model runs

Everything inside SEA-FORWARD's compute environment plays the role the guide
assigns to the system owner's facility. It has two parts:

- **Storage** holds the durable artifacts: the grid, the downloaded forcings, the
  CROCO source code, and — critically for operation — the **restart files** that
  carry the ocean state from one cycle to the next.
- **A single, reproducible compute environment** holds the running system. The
  Architecture Guide stresses that an operational system should run in one
  controlled, reproducible environment; SEA-FORWARD realises this as a pinned
  `conda` environment plus a purpose-built NetCDF/CROCO stack (`env.sh`,
  `opt_seq`). Inside it live:
  - **the model configuration** — `cppdefs.h`, `param.h`, `croco.in`, and the
    grid dimensions, which together define exactly what the compiled model is;
  - **the forecast driver** — `run_forecast_cycle.sh`, which orchestrates the
    whole daily cycle: download to prepare to spin-up to forecast;
  - **validation** — the input-consistency checks before a run and the
    observation comparisons after it;
  - **history and restart output** — the model's forecast fields and the restart
    file that seeds the next cycle.

### The forecast — interoperable output

The engine produces **CROCO NetCDF** history and average files, and these are
**CF-compliant** (Climate and Forecast metadata conventions). This is not a
detail: interoperability is the property the Architecture Guide places at the
centre of the whole design. Because the output is CF-NetCDF, anyone downstream
can open it with standard tools — `xarray`, `ncview`, CDO — with no knowledge of
how it was produced. The output is the contract between the system owner and
everyone downstream.

### Downstream — visualization, analysis, users

On the downstream side, SEA-FORWARD (acting, as the guide allows, as its own
downstream provider) offers:

- **visualization and analysis tools** — the plotting and comparison notebooks
  that produce SST, SSH, and current-speed maps, the Mercator comparisons, and the
  tidal diagnostics;
- **derived products and indicators** — the extensible layer where intermediate
  users build on the interoperable output;
- **access for end users** — either directly to the downstream products, or by
  pulling the components themselves from the repository.

### The repository — how the system is reproduced

Underpinning all of it is the **`opera-seaforward/seaforward` repository**. In the
Architecture Guide's terms it is what makes the system *reproducible* rather than
merely *runnable*: every stage of the value chain — the storage layout, the
preprocessing tools (`seaforward.py`), the environment and model configuration,
the forecast driver, and the downstream notebooks — is distributed from one
versioned source. Anyone can reconstruct any component from it. The repository is,
in effect, the machine-readable definition of the whole architecture.