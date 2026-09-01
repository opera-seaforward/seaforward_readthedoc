This is the heart of nesting. Take the parent's `croco_his.nc` and translate it
into a Mercator-format file the ini/bry tools can read.

First, see which parent cycles you have:

```bash
ls ${SEA_FORWARD_ROOT}/forecast/model-runs/Canary_12/
```

Runs made by the current driver carry its flag tag — `20260726_plain`, or
`20260726_plain_tides_rivers` when extensions were on. Older folders are just the
date. Use whichever name your listing shows.

Then convert one:

```bash
cd ~/seaforward
python3 -c "
import sftools.nesting as nest
nest.croco_to_mercator(
    '${SEA_FORWARD_ROOT}/forecast/model-runs/Canary_12/20260712/fcst/CROCO_FILES/croco_his.nc',
    '${FCAST}/downloaded_data/PARENT/parent_20260712.nc',
    Yorig=2000)
"
```

**What this does:** reads the 1/12° output; interpolates temperature, salinity and
currents from sigma levels onto the 50 standard Mercator z-levels; rotates the
currents to east/north; renames everything to Mercator's variable names; and writes
a file with dims `(time, depth, latitude, longitude)` — indistinguishable from a real
Mercator file to the ini/bry tools.

!!! warning
    **Match `Yorig` to the parent's track.** The parent here is a **forecast**, whose CROCO time origin is the year 2000; a hindcast parent would need `Yorig=1993`. The wrong origin doesn't crash anything — every timestamp simply shifts by the difference in reference years, and the child then runs against dates that look plausible and are wrong.

!!! check
    It prints `Created Mercator-format parent: .../parent_20260712.nc` with `21 time(s), 50 depths, grid 123 x 81`.

Verify it really looks like Mercator:

```bash
python3 -c "
import xarray as xr
d = xr.open_dataset('${FCAST}/downloaded_data/PARENT/parent_20260712.nc')
print('vars:', list(d.data_vars))
print('dims:', dict(d.sizes))
print('times:', str(d.time.values[0])[:10], '..', str(d.time.values[-1])[:10])
print('surface temp mean:', round(float(d.thetao.isel(time=0, depth=0).mean()), 2))
"
```

!!! check
    `vars: ['thetao', 'so', 'uo', 'vo', 'zos']`, with sensible dates and a plausible SST. That is a Mercator file — made from your own model.

!!! note
    **The point of all this.** You have just re-expressed your 1/12° forecast as an ocean product. Nesting is nothing more than downscaling from your own model instead of from Mercator, and this file is the proof.