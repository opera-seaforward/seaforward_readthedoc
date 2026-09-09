# Setup

Everything in this chapter runs from `~/seaforward`, inside the `seaforward` conda
environment:

```bash
cd ~/seaforward
conda activate seaforward
python3
```

## The modules

```python
import matplotlib; matplotlib.use('Agg')
import sftools.postprocess as pp     # load output, extract fields
import sftools.plotting    as pl     # draw them
import sftools.animation   as anim   # animate them through time
```

| Module | What it does |
| --- | --- |
| `postprocess` (`pp`) | Opens CROCO output, extracts fields, sections, profiles and time series, computes derived quantities (speed, vorticity, kinetic energy), and handles the sigma-to-depth transformation. |
| `plotting` (`pl`) | Turns any labelled array into a figure. `pl.plot()` detects the type — map, section, profile, Hovmöller, time series — from the data itself. |
| `animation` (`anim`) | The same fields animated through the run, inline or written to a GIF. |

`matplotlib.use('Agg')` renders to a file rather than a window, which is what you want on a
machine with no display. Leave it out if you are working in Jupyter and want the figures
inline.

## Opening a run

Two ways in, depending on what you have:

```python
# a single history file — the proving run from Phase 2
ds = pp.open_history('forecast/scratch/Canary_12/CROCO_FILES/croco_his.nc',
                     Yorig=2000)

# a dated run folder produced by the operational driver — Phase 3
ds = pp.open_run('forecast/model-runs/Canary_12/20260711',
                 phase='fcst', Yorig=2000)
```

!!! warning
    **`Yorig` must match the track.** CROCO stores time as seconds since a reference year: **2000** for a forecast, **1993** for a hindcast. The wrong value doesn't crash anything — the fields are right, but every date is wrong by years, which quietly ruins any comparison or animation title. The same applies to `phase`: `'fcst'` for a forecast, `'hcast'` for a hindcast.

Confirm it decoded properly:

```python
print(ds.sizes['time'], 'records')
print(ds.time.values[0], '->', ds.time.values[-1])
```

The dates should be the window you ran. If they read 1993 or 2000, `Yorig` is wrong.

## The parameters the examples use

The pages that follow all assume these, set once:

```python
ds = pp.open_history('forecast/scratch/Canary_12/CROCO_FILES/croco_his.nc',
                     Yorig=2000)

depth    = None                                      # None = surface; or metres
isobaths = [50, 100, 200, 500, 1000, 2000]           # bathymetry contours on maps

lon0, lat0, lon1, lat1 = -21.0, 21.0, -17.2, 21.0    # section: start -> end
plon, plat = -19.0, 21.0                             # the point for profiles
```

- **`depth`** — change it and every map, section and profile follows. That is the point of
  the unified extractor.
- **`isobaths`** — depths to contour on maps. The shelf break shows up between 100 and
  200 m here, which is where the upwelling sits.
- **`lon0, lat0` → `lon1, lat1`** — the two ends of a vertical section, running west to
  east along 21°N across the shelf. It stops at −17.2° rather than the coast: points on
  land produce a spike of nonsense at the end of the figure.
- **`plon, plat`** — one point, used by the profiles and by the time series, so those pages
  describe the same place.

## Depth is set per figure

Every extractor that can work below the surface takes a `depth_m`:

```python
pp.field(ds, 'temp', depth_m=100)                  # a horizontal map at 100 m
pp.speed_map(ds, depth_m=1000)                     # speed at 1000 m
pp.uv_at_depth(ds, depth_m=200)                    # currents at 200 m
pp.timeseries(ds, 'temp', plon, plat, depth_m=50)  # a point through time, at 50 m
```

`depth_m=None` — or leaving it out — gives the surface. A number gives that **true depth in
metres**, interpolated from the model's sigma levels, with blanks where the sea floor is
shallower than you asked for.

!!! note
    **True depth is not a sigma level.** `pp.field_map(ds, 'temp', level=-30)` takes terrain-following layer 30, whose actual depth changes across the domain — shallow over the shelf, deep offshore. `pp.field(ds, 'temp', depth_m=30)` gives a genuine 30 m everywhere, interpolated. Use the first for model diagnostics, the second for anything you would compare against observations.

The pages that follow each choose their own depth: Surface fields works at the surface,
Dynamics at 1000 m where the mesoscale is cleanest, and Vertical structure shows a map at
100 m alongside its sections and profiles.

## Two functions do most of the work

```python
pl.plot(pp.field(ds, 'temp'))                        # surface temperature
pl.plot(pp.field(ds, 'temp', depth_m=50))            # temperature at 50 m
pl.plot(pp.section(ds, 'temp', lon0, lat0, lon1, lat1))
pl.plot(pp.profile(ds, 'temp', plon, plat))
```

`pp.field()` and its relatives return a labelled `xarray.DataArray` carrying CF attributes,
coordinates and a timestamp. `pl.plot()` reads those labels to choose the colour map, the
range, the axis labels and the title — so you rarely have to specify any of them. Every one
can still be overridden:

```python
pl.plot(pp.field(ds, 'temp'), cmap='cividis', vmin=15, vmax=25)
```

## Saving a figure

Without `out=`, the plotters return a matplotlib figure — useful when you want to adjust it
before saving. With `out=`, they write the file and return its path:

```python
fig = pl.plot(pp.field(ds, 'temp'))                  # returns the figure
pl.plot(pp.field(ds, 'temp'), out='sst.png')         # writes sst.png
```

The pages that follow each open a session with these same imports and parameters, then show
snippets that run inside it. Each ends with a block that reproduces all its figures in one
go.