`define_attrs.py` is the single source of truth for how each variable is
**labelled and displayed**. Each entry carries CF metadata (`long_name`,
`units`, `standard_name`) and display defaults (`cmap`, `vmin`, `vmax`,
`diverging`).

The plotting layer reads these automatically, so a temperature field draws with
`RdYlBu_r` and an SSH/velocity/vorticity field draws with a diverging colormap
centred on zero — with no manual settings. The priority for colour and range is:

**explicit keyword → variable attribute → auto from data.**

Diverging variables (SSH, velocity, vorticity, fluxes) with no fixed range get a
symmetric range about zero automatically; fields like speed and EKE are pinned
to a zero floor.

The registry covers ocean state (temperature, salinity, density, SSH, velocity,
speed, vertical velocity), derived quantities (vorticity, EKE, mixed-layer
depth, stratification) and atmosphere/flux fields (wind, wind stress, heat and
radiative fluxes), plus grid variables.

You rarely call `define_attrs` directly — but you can override any display
choice at plot time:

```python
pl.plot(pp.field_map(ds, "temp"), cmap="turbo", vmin=16, vmax=25)
```

!!! note
    - Density (`rho`, `sigma_t`) uses the `cmo.dense` colormap from **cmocean**.
    - Install it with `conda install -c conda-forge cmocean`, otherwise matplotlib falls back to a default colormap.