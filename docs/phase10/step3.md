Set up a gen directory (grid + tide params), then run the tool:

```bash
cd ~/seaforward/forecast/scratch/Canary_12
TGEN=$PWD/tide_gen/CROCO_FILES
mkdir -p "$TGEN"
cp CROCO_FILES/croco_grd.nc "$TGEN/"
```

Then write the TPXO10 param file into that directory **as** `crocotools_param.py` — its
contents are in [Step 2](step2.md).

!!! important
    **The name is not free, and the Mercator file is not a starting point.**
    `make_tides` imports a module called `crocotools_param`, so a file named
    anything else is never read unless you pass `--param_file`. And the
    `crocotools_param.py` already in `CROCO_FILES/` is the Mercator one — `inputdata =
    'mercator'`, no `tides` list, no `cur`/`pot`, no file templates — so
    `make_tides` has nothing to work with and stops on it.

```bash
cd ~/seaforward/sftools
conda activate seaforward
python seaforward.py make_tides \
    --input_dir ~/seaforward/data/DATASETS_CROCOTOOLS/TPXO10/ \
    --output_dir "$TGEN" \
    --run_date "2026-07-11 00:00:00" \
    --Yorig 2000 --fname_out croco_frc.nc
```

It loops the ten waves, printing each. Then **check the output before trusting it** —
the single most useful number is the M2 elevation amplitude, which should be physically
sensible for your region:

```bash
python3 -c "
import xarray as xr, numpy as np
d = xr.open_dataset('$TGEN/croco_frc.nc', decode_times=False)
print('vars:', [v for v in d.data_vars])
print('dims:', dict(d.sizes))
m2 = d.tide_Eamp.isel(tide_period=0).values
print('M2 amp: mean %.3f m  max %.3f m' % (np.nanmean(m2), np.nanmax(m2)))
"
```

For the Canary parent this gave:

``` { .text .no-copy }
vars: ['tide_Ephase','tide_Eamp','tide_Cmin','tide_Cmax','tide_Cangle','tide_Cphase','tide_Pamp','tide_Pphase']
dims: {'tide_period': 10, 'eta_rho': 123, 'xi_rho': 81}
M2 amp: mean 0.307 m  max 0.858 m
```

Eight variables: elevation (`tide_E*`), the current ellipse (`tide_C*`, because
`cur=True`) and the potential (`tide_P*`, because `pot=True`) — as the overview
describes. Ten waves, on the model grid.

M2 mean 0.31 m with a maximum of 0.86 m is right for this coast: the tide is modest
offshore and grows toward the shelf. A mean near zero would mean the interpolation
found nothing; several metres would mean something is wrong with the atlas paths.

### A fill-value check worth doing once

Any of the eight variables can carry the NetCDF fill value `9.969e+36`, and in
practice it is the current ellipse that does. Count them per variable:

```bash
python3 -c "
import xarray as xr, numpy as np
d = xr.open_dataset('$TGEN/croco_frc.nc', decode_times=False)
g = xr.open_dataset('$TGEN/croco_grd.nc')
mask = g.mask_rho.values.astype(bool)
for n in d.data_vars:
    v = d[n].values; fill = v > 1e30
    m = np.broadcast_to(mask, v.shape)
    print('%-12s ocean %6d   land %6d' % (n, (fill&m).sum(), (fill&~m).sum()))
"
```

``` { .text .no-copy }
tide_Ephase  ocean      0   land      0
tide_Eamp    ocean      0   land      0
tide_Cmin    ocean      3   land    492
tide_Cmax    ocean      0   land      0
tide_Cangle  ocean      0   land      0
tide_Cphase  ocean      0   land      0
tide_Pamp    ocean      0   land      0
tide_Pphase  ocean      0   land      0
```

The 492 on land are cosmetic — CROCO masks those cells. The three on ocean are worth
looking at:

```bash
python3 -c "
import xarray as xr, numpy as np
d = xr.open_dataset('$TGEN/croco_frc.nc', decode_times=False)
g = xr.open_dataset('$TGEN/croco_grd.nc')
cmin = d.tide_Cmin.values
fill = cmin > 1e30
mask = np.broadcast_to(g.mask_rho.values.astype(bool), cmin.shape)
lon = g.lon_rho.values; lat = g.lat_rho.values; h = g.h.values
for k, j, i in np.argwhere(fill & mask):
    print('wave %d at %.2fE %.2fN, depth %.0f m' % (k, lon[j,i], lat[j,i], h[j,i]))
"
```

``` { .text .no-copy }
wave 9 at -16.05E 18.32N, depth 74 m
wave 9 at -16.92E 21.14N, depth 50 m
wave 9 at -16.04E 23.36N, depth 50 m
```

All three are **wave 9 — Mm**, the lunar monthly, at shallow cells against the coast.
Mm is the weakest constituent in the set and the nine that carry the tidal energy are
clean, so this is not worth stopping for.

**What would be worth stopping for** is fills scattered across the main semidiurnal or
diurnal waves, or in open water away from the coast. It is the same defect as
fill values in an initial condition, which [Phase 8](../phase8/08_agrif.md) Step 3b documents: the model reads 9.969e+36 as a physical amplitude.

The shipped TPXO7 is that case: on this grid it fills `tide_Cmin` and
`tide_Cmax` on 989 of 8391 ocean cells, the same cells in every wave, at
depths from 50 to 2292 m — the shelf and the slope. Eighteen of them sit on the
south and north open-boundary rows, which is where `SSH_TIDES` and `UV_TIDES` read
the harmonics. [Step 2](step2.md) has the comparison against the atlas.
