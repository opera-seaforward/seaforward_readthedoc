```python
import sftools.postprocess as pp
import sftools.plotting    as pl
import sftools.validation  as val

# open a run (see the note on Yorig below)
H = "hindcast/model-runs/Canary_12/20251225/hcast/CROCO_FILES/croco_his.nc"
ds = pp.open_history(H, Yorig=1993)

# a surface temperature map — colour and labels come from the variable
pl.plot(pp.field_map(ds, "temp"))

# temperature at a true depth of 50 m
pl.plot(pp.field(ds, "temp", depth_m=50))

# a vertical section across the shelf
pl.plot(pp.section(ds, "temp", -21, 21, -16, 21))

# validate the forecast against Mercator
F    = "forecast/model-runs/Canary_12/20260712/fcst/CROCO_FILES/croco_his.nc"
MERC = "forecast/scratch/Canary_12/downloaded_data/MERCATOR/MERCATOR_20260711_00.nc"
val.compare_sst(F, MERC, date="2026-07-11", Yorig=2000)
```

### A note on `Yorig` (important)

CROCO writes its `time` variable as *seconds since a reference date* — the
`Yorig` set in the run. SEA-FORWARD's tracks use **different reference years**:

| Track | `Yorig` |
| --- | --- |
| Hindcast | `1993` |
| Forecast | `2000` |

If a CROCO file has CF-compliant time units, the toolkit decodes them
automatically. If not (common), you must pass the right `Yorig` so dates decode
correctly:

```python
ds = pp.open_history(H, Yorig=1993)   # hindcast
ds = pp.open_history(F, Yorig=2000)   # forecast
```

Passing the wrong `Yorig` shifts all dates by the difference in reference years
(e.g. 1993 vs 2000 → a 7-year shift), which mainly matters for time-axis plots
and date-matched comparisons. When in doubt, check:

```python
import xarray as xr
raw = xr.open_dataset(F, decode_times=False)
print(raw["time"].attrs.get("units", "NONE"), float(raw["time"].values[0]))
```

### Using the toolkit in a notebook

The modules use matplotlib's non-interactive backend for saving files. In a
Jupyter notebook, put the inline magic **alone on its own line** (a trailing
comment breaks it) and omit `out=` so the figure returns and displays inline:

```python
%matplotlib inline

fig = pl.plot(pp.field_map(ds, "temp"))   # no out= -> returns the figure
fig
```

Pass `out="something.png"` instead to save the figure to disk and close it.

After editing a module you must copy it into `sftools/` **and** reload it
(reload only reads what is on disk):

```python
import importlib, sftools.postprocess
importlib.reload(sftools.postprocess)
import sftools.postprocess as pp
```