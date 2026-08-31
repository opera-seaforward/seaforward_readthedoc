# Setup

Everything in this chapter runs from `~/seaforward`, inside the `seaforward` conda
environment:

```bash
cd ~/seaforward
conda activate seaforward
jupyter lab            # or python3, or a script — the toolkit does not need Jupyter
```

## The modules

```python
import sftools.postprocess as pp     # load output, extract fields
import sftools.plotting    as pl     # draw them
import sftools.animation   as anim   # animate them through time
```

| Module | What it does |
| --- | --- |
| `postprocess` (`pp`) | Opens CROCO output, extracts fields, sections, profiles and time series, computes derived quantities (speed, vorticity, kinetic energy), and handles the sigma-to-depth transformation. |
| `plotting` (`pl`) | Turns any labelled array into a figure. `pl.plot()` detects the type — map, section, profile, Hovmöller, time series — from the data itself. |
| `animation` (`anim`) | The same fields animated through the run, inline or written to a GIF. |

!!! tip
    **Working in Jupyter?** Add `importlib.reload()` after the imports so edits to the toolkit take effect without restarting the kernel:

```python
    import importlib
    for m in (pp, pl, anim):
        importlib.reload(m)
```

## Opening a run

Two ways in, depending on what you have:

```python
# a single history file
ds = pp.open_history("forecast/scratch/Canary_12/CROCO_FILES/croco_his.nc",
                     Yorig=2000)

# a dated run folder produced by the operational driver
ds = pp.open_run("forecast/model-runs/Canary_12/20260711",
                 phase="fcst", Yorig=2000)
```

!!! warning
    **`Yorig` must match the run.** A forecast uses **2000**, a hindcast **1993**. Get it wrong and nothing crashes — the fields are right but every timestamp is wrong by years, which quietly ruins any comparison or animation title. The same applies to `phase`: `"fcst"` for a forecast, `"hcast"` for a hindcast.

Check it took:

```python
print(ds.sizes["time"], "records")
print(ds.time.values[0], "->", ds.time.values[-1])
```

The dates should be the window you ran. If they read 1993 or 2000, `Yorig` is wrong.

## The variables the examples use

The pages that follow all assume these three, set once:

```python
ds       = pp.open_history("forecast/scratch/Canary_12/CROCO_FILES/croco_his.nc",
                           Yorig=2000)
depth    = None                 # None = surface; or a depth in metres, e.g. 50
isobaths = [200, 1000, 2000]    # bathymetry contours to overlay on maps
```

Change `depth` and every map, section and profile follows it — that is the point of
the unified extractor.

## Two functions do most of the work

```python
pl.plot(pp.field(ds, "temp"))               # surface temperature
pl.plot(pp.field(ds, "temp", depth_m=50))   # temperature at 50 m
pl.plot(pp.section(ds, "temp", -21, 21, -16, 21))   # a vertical section
pl.plot(pp.profile(ds, "temp", -19, 21))            # a profile
```

`pp.field()` and its relatives return a labelled `xarray.DataArray` carrying CF
attributes, coordinates and a timestamp. `pl.plot()` reads those labels to choose
the colour map, the range, the axis labels and the title — so you rarely have to
specify any of them. Every one of them can still be overridden:

```python
pl.plot(pp.field(ds, "temp"), cmap="cividis", vmin=15, vmax=25)
```

## Saving a figure

Without `out=`, the plotters return a matplotlib figure — useful in a notebook, or
when you want to adjust it before saving. With `out=`, they write the file and
return its path:

```python
fig = pl.plot(pp.field(ds, "temp"))                  # returns the figure
pl.plot(pp.field(ds, "temp"), out="sst.png")         # writes sst.png
```