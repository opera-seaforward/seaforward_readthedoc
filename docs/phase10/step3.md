Set up a gen directory (grid + tide params), then run the tool:

```bash
cd ~/seaforward/forecast/scratch/Canary_12
TGEN=$PWD/tide_gen/CROCO_FILES
mkdir -p "$TGEN"
cp CROCO_FILES/croco_grd.nc              "$TGEN/"
cp CROCO_FILES/crocotools_param_tides.py "$TGEN/crocotools_param.py"

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

```text
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

`tide_Cmin` — the current-ellipse minor axis, a signed quantity — can carry the NetCDF
fill value `9.969e+36` on some cells. Check where they are:

```bash
python3 -c "
import xarray as xr, numpy as np
d = xr.open_dataset('$TGEN/croco_frc.nc', decode_times=False)
g = xr.open_dataset('$TGEN/croco_grd.nc')
cmin = d.tide_Cmin.values; fill = cmin > 1e30
mask = np.broadcast_to(g.mask_rho.values.astype(bool), cmin.shape)
print('fill on ocean: %d   fill on land: %d' % ((fill&mask).sum(), (fill&~mask).sum()))
"
```

```text
fill on ocean: 3   fill on land: 492
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

```text
wave 9 at -16.05E 18.32N, depth 74 m
wave 9 at -16.92E 21.14N, depth 50 m
wave 9 at -16.04E 23.36N, depth 50 m
```

All three are **wave 9 — Mm**, the lunar monthly, at shallow cells against the coast.
Mm is the weakest constituent in the set and the nine that carry the tidal energy are
clean, so this is not worth stopping for.

**What would be worth stopping for** is fills scattered across the main semidiurnal or
diurnal waves, or in open water away from the coast. That is the same class of bug as
fill values in an initial condition, which Phase 8 Step 3b documents, and it would
poison the run.