Every extractor returns a labelled `xarray.DataArray` carrying CF attributes and
coordinates, ready to hand to `pl.plot()`.

### Horizontal fields

```python
pp.field_map(ds, var, tindex=-1, level=-1)   # a sigma-level slice (level = sigma index)
pp.field_at_depth(ds, var, depth_m, tindex=-1)  # a TRUE depth (m), interpolated
pp.field(ds, var, depth_m=None, tindex=-1)   # unified: surface if depth_m None, else depth
```

**Sigma level vs true depth — an important distinction.**
`field_map(ds, "temp", level=-30)` selects **sigma index −30**, a
terrain-following layer whose actual depth varies with the bathymetry. To get a
field at a fixed *depth* (e.g. 30 m below the surface), use `field_at_depth` or
`field(..., depth_m=30)`. Points where the sea floor is shallower than the
requested depth come back blank (NaN).

```python
pl.plot(pp.field(ds, "temp"))               # surface (default)
pl.plot(pp.field(ds, "temp", depth_m=30))   # temperature at 30 m
pl.plot(pp.field(ds, "salt", depth_m=100))  # salinity at 100 m
```

### Surface fields and currents

```python
pp.surface(ds, "temp", tindex=-1)   # top sigma level of a 3D field
pp.surface_uv(ds, tindex=-1)        # (u, v) on the rho grid at the surface
pp.rotate_uv(ds, u, v)              # rotate grid-aligned (u,v) to east/north
pp.speed(u, v)                      # sqrt(u^2 + v^2)
```

### Currents & speed at depth

```python
pp.uv_at_depth(ds, depth_m, rotate=True)   # (u, v) at a true depth, east/north
pp.speed_map(ds, depth_m=None)             # current speed as a labelled DataArray
```

```python
pl.plot(pp.speed_map(ds))               # surface speed
pl.plot(pp.speed_map(ds, depth_m=50))   # speed at 50 m
```

### Vorticity

Relative vorticity ζ = ∂v/∂x − ∂u/∂y reveals eddies and filaments. Normalising
by the Coriolis parameter *f* gives a dimensionless field (~±1 for strong
eddies), the usual way to see the mesoscale.

```python
pp.vorticity(ds, depth_m=None, normalized=False)
```

```python
pl.plot(pp.vorticity(ds))                       # raw vorticity (s^-1)
pl.plot(pp.vorticity(ds, normalized=True))      # vorticity / f  (dimensionless)
pl.plot(pp.vorticity(ds, depth_m=50, normalized=True))
```

Positive (red) = cyclonic in the Northern Hemisphere; negative (blue) =
anticyclonic.

### Vertical sections

A section interpolates a field along a straight lon/lat transect and returns it
on `(s_rho, points)` with a `distance_km` coordinate and a 2-D `depth`
coordinate. Land and coastal edge cells are left blank.

```python
pp.section(ds, var, lon0, lat0, lon1, lat1, tindex=-1, npts=200)
```

```python
pl.plot(pp.section(ds, "temp",  -21, 21, -16, 21))   # temperature vs depth
pl.plot(pp.section(ds, "speed", -21, 21, -16, 21))   # speed vs depth
pl.plot(pp.section(ds, "salt",  -21, 21, -16, 21))
```

Works for raw fields (`temp`, `salt`, `u`, `v`) and derived fields (`speed`,
`ke`, `vort`, `vort_f`). SSH (`zeta`) is two-dimensional and has no section.

### Vertical profiles

```python
pp.profile(ds, var, lon0, lat0, tindex=-1)   # value vs depth at a point
```

```python
pl.plot(pp.profile(ds, "temp",  -19, 21))
pl.plot(pp.profile(ds, "speed", -19, 21))
```

### Hovmöller diagrams

Time versus depth (at a point), or time versus latitude/longitude (along a
line):

```python
pp.hovmoller(ds, var, kind="time_depth", lon0=..., lat0=...)   # time vs depth
pp.hovmoller(ds, var, kind="time_lat",   lon0=...)             # time vs latitude
pp.hovmoller(ds, var, kind="time_lon",   lat0=...)             # time vs longitude
```

```python
pl.plot(pp.hovmoller(ds, "temp", "time_lat", lon0=-19))   # coastal SST evolution
pl.plot(pp.hovmoller(ds, "temp", "time_depth", lon0=-19, lat0=21))
```

### Time series

```python
pp.timeseries(ds, var, lon0, lat0, surface_only=True, depth_m=None)
```

```python
pl.plot(pp.timeseries(ds, "temp",  -19, 21))               # surface SST over time
pl.plot(pp.timeseries(ds, "zeta",  -19, 21))               # SSH over time
pl.plot(pp.timeseries(ds, "speed", -19, 21, depth_m=50))   # speed at 50 m over time
```

Works for raw and derived fields, at the surface or any depth.

### Combined "eddy view"

A shaded base field with vorticity contours **or** current vectors on top:

```python
base, ov = pp.eddy_view(ds, base="speed", overlay="vort", depth_m=None)
pl.plot_eddy(base, ov, ds=ds, isobaths=[200, 1000])

base, ov = pp.eddy_view(ds, base="temp", overlay="uv", depth_m=50)
pl.plot_eddy(base, ov, ds=ds)
```

`eddy_view` returns two things: the base field to shade, and an `overlay` tuple
`("vort", vort_da)` or `("uv", (u, v))`. You pass both straight to `plot_eddy`.

### Trimming the sponge band

CROCO damps velocities in a band along the open boundaries (the *sponge*, set by
`X_SPONGE` in `croco.in`). This band appears smoother than the interior and, in
validation, is nudged toward the parent — so for clean figures and honest
statistics you can trim it:

```python
dsi = pp.crop_interior(ds, margin_deg=0.5)    # trim ~0.5° off each edge
dsi = pp.crop_interior(ds, margin_cells=6)    # or trim a number of grid cells
pl.plot(pp.speed_map(dsi))
```