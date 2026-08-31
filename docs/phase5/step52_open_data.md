# Open data

Load a CROCO history file with `pp.open_history()`. The forecast you built in
Phase 3 lives under `forecast/model-runs/`:

```python
H  = "forecast/model-runs/Canary_12/20260711/fcst/CROCO_FILES/croco_his.nc"
ds = pp.open_history(H, Yorig=2000)
```

Or open the proving run from Phase 2 directly:

```python
ds = pp.open_history("forecast/scratch/Canary_12/CROCO_FILES/croco_his.nc",
                     Yorig=2000)
```

!!! warning
    **`Yorig` must match the track.** CROCO stores time as seconds since a reference year: **2000** for a forecast, **1993** for a hindcast. The wrong value doesn't crash anything — the fields are right, but every date is wrong by years.

Confirm it decoded properly:

```python
print(ds.sizes["time"], "records")
print(ds.time.values[0], "->", ds.time.values[-1])
```

## Parameters used throughout

```python
isobaths = [50, 100, 200, 500, 1000, 2000]           # bathymetry contours on maps

lon0, lat0, lon1, lat1 = -21.0, 21.0, -17.2, 21.0    # section: start -> end
plon, plat = -19.0, 21.0                              # the point for profiles
```

- **`isobaths`** — depths to contour on maps. The shelf break shows up between 100
  and 200 m here, which is where the upwelling sits.
- **`lon0, lat0` → `lon1, lat1`** — the two ends of a vertical section, running west
  to east along 21°N across the shelf. It stops at −17.2° rather than the coast: the
  last points on land produce a spike of nonsense at the end of the figure.
- **`plon, plat`** — one point, used by the profiles and by the time series, so those
  pages describe the same place.

## Depth is set per figure

Every extractor that can work below the surface takes a `depth_m`:

```python
pp.field(ds, "temp", depth_m=100)                  # a horizontal map at 100 m
pp.speed_map(ds, depth_m=1000)                     # speed at 1000 m
pp.uv_at_depth(ds, depth_m=200)                    # currents at 200 m
pp.timeseries(ds, "temp", plon, plat, depth_m=50)  # a point through time, at 50 m
```

`depth_m=None` — or leaving it out — gives the surface. A number gives that **true
depth in metres**, interpolated from the model's sigma levels, with blanks where the
sea floor is shallower than you asked for.

!!! note
    **True depth is not a sigma level.** `pp.field_map(ds, "temp", level=-30)` takes terrain-following layer 30, whose actual depth changes across the domain — shallow over the shelf, deep offshore. `pp.field(ds, "temp", depth_m=30)` gives a genuine 30 m everywhere, interpolated. Use the first for model diagnostics, the second for anything you would compare against observations.

The pages that follow each choose their own depth: Surface fields works at the
surface, Dynamics at 1000 m where the mesoscale is cleanest, and Vertical structure
shows a map at 100 m alongside its sections and profiles.