### Opening files

```python
pp.open_history(fname, Yorig=None)          # a single history/average file
pp.open_run(run_root, phase="hcast", Yorig=None)  # concatenate all cycles of a run
```

`open_history` opens one `croco_his.nc`. `open_run` finds and concatenates every
cycle under `run_root/*/<phase>/CROCO_FILES/croco_his.nc` into one continuous,
time-sorted dataset (dropping duplicate timestamps at cycle joins) — useful for
looking at a whole multi-cycle hindcast at once.

```python
ds = pp.open_run("hindcast/model-runs/Canary_12", phase="hcast", Yorig=1993)
```

### Small helpers

```python
pp.times(ds)                 # the time coordinate (datetime64 if decoded)
pp.extent(ds, pad=0.0)       # [lon_min, lon_max, lat_min, lat_max] for map extents
pp.lonlatmask(ds)            # (lon2d, lat2d, mask) on the rho grid
pp.bathymetry(ds)            # labelled sea-floor depth h
pp.nearest_index(ds, lon, lat)  # (eta, xi) index nearest a lon/lat point
```

### Sigma-to-depth machinery

CROCO uses terrain-following sigma coordinates. These functions convert them to
metric depths (adapted from the CROCO/somisana tooling), and underpin every
depth interpolation in the toolkit:

```python
pp.depths(ds, tindex=0)      # depth (m, negative down) of every sigma cell
pp.z_levels(...)             # the underlying sigma->z transform (Vtransform 1 & 2)
pp.csf(...)                  # sigma stretching function
```

You rarely call these directly — `field_at_depth`, `uv_at_depth`, `profile`,
`section` and the validation functions use them internally.