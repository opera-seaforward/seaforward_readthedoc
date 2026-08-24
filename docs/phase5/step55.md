### The smart wrapper

`pl.plot(da)` inspects a labelled DataArray and dispatches to the right builder:

| Data shape | Drawn as |
| --- | --- |
| has `lon_rho`/`lat_rho`, no `s_rho` | map |
| has `distance_km` + 2-D `depth` | section |
| 1-D over `time` | time series |
| 1-D with a `depth` coordinate | profile |
| `(time, second axis)` | Hovmöller |

So the same `pl.plot(...)` call handles every extractor above.

### Generic builders

You can also call the builders directly for more control:

```python
pl.plot_map(da, cmap=None, vmin=None, vmax=None, title=None,
            ds=None, isobaths=None, uv=None, uv_kind="current")
pl.plot_section(da, ...)
pl.plot_profile(da, ...)
pl.plot_hovmoller(da, ...)
pl.plot_timeseries(da, ...)
```

### Map overlays: isobaths and vectors

`plot_map` can overlay bathymetry contours and current/wind vectors (needs the
CROCO dataset `ds` for the grid):

```python
sst = pp.field_map(ds, "temp")
u, v = pp.surface_uv(ds); ue, vn = pp.rotate_uv(ds, u, v)

pl.plot_map(sst, ds=ds,
            isobaths=[200, 1000, 2000],   # contour lines
            uv=(ue, vn))                  # current vectors + reference arrow
```

Vectors carry a labelled reference arrow and are auto-scaled by magnitude. Wind
is roughly an order of magnitude faster than currents, so pass `uv_kind="wind"`
(and tune with `uv_scale`, `uv_skip`, `uv_ref` if needed):

```python
# wind on top of SST — see 5.6 for loading the wind field
pl.plot_map(sst, ds=ds, uv=(wu, wv), uv_kind="wind",
            uv_scale=500, uv_ref=10)
```

`uv_scale` is inverse: **larger = shorter arrows**. `uv_ref` sets the reference
arrow's value (m/s) — the legend by which all other arrows are read.

### Building blocks

```python
pl.add_isobaths(ax, ds, isobaths=(200, 1000, 2000))
pl.add_uv(ax, ds, u, v, kind="current"|"wind")
```