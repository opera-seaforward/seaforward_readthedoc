Set up a gen directory (grid + tide params), then run the tool:

```bash
TGEN=~/seaforward/forecast/scratch/Agulhas_12/tide_gen/CROCO_FILES
mkdir -p "$TGEN"
cp CROCO_FILES/croco_grd.nc "$TGEN/"
cp crocotools_param_tides.py "$TGEN/crocotools_param.py"

cd ~/seaforward/sftools
python seaforward.py make_tides \
    --input_dir ~/seaforward/data/DATASETS_CROCOTOOLS/TPXO10/ \
    --output_dir "$TGEN" \
    --run_date "2026-07-17 00:00:00" \
    --Yorig 2000 --fname_out croco_frc.nc
```

It loops the ten waves, printing each. Then **check the output before trusting
it** — the single most useful number is the M2 elevation amplitude, which should
be physically sensible for your region:

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

For the Agulhas parent this gave:

```
vars: ['tide_Ephase','tide_Eamp','tide_Cmin','tide_Cmax','tide_Cangle','tide_Cphase','tide_Pamp','tide_Pphase']
dims: {'tide_period': 10, 'eta_rho': 99, 'xi_rho': 159}
M2 amp: mean 0.371 m  max 0.593 m
```

Eight variables — elevation amplitude and phase (`tide_E*`), current ellipse parameters (`tide_C*`, present because `cur=True`), and tidal potential (`tide_P*`, present because `pot=True`). Ten waves, on the model grid. M2 mean 0.37 m, max 0.59 m — spot on for the Agulhas region.

### A fill-value check worth doing once

`tide_Cmin` (the current-ellipse minor axis, a signed quantity) can carry the
NetCDF fill value `9.969e+36` on some cells. Check where they are:

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

For Agulhas this printed `fill on ocean: 0   fill on land: 170` — every fill is
on a land cell, which CROCO masks. Cosmetic. If any fills land on **ocean**
cells, that is a real problem to fix before running (the same class of bug as
fill values in an initial condition).