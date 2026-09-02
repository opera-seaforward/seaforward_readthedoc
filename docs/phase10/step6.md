A run with the retimed output. The proof is not `MAIN: DONE` — it is the tidal signal
itself. Track sea level at a shelf point across the hourly records:

```bash
cd ~/seaforward
python3 << 'PYEOF'
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, xarray as xr, numpy as np

D = 'forecast/model-runs/IGOG_12/20260726_plain_tides/fcst/CROCO_FILES/'
d = xr.open_dataset(D + 'croco_his.nc', decode_times=False)

# a shelf point: wet, and the shallowest cell deeper than 30 m
h = d.h.values; m = d.mask_rho.values
j, i = np.unravel_index(np.argmin(np.where((m > 0) & (h > 30), h, 1e9)), h.shape)
z = d.zeta.isel(eta_rho=j, xi_rho=i).values
t = (d.scrum_time.values - d.scrum_time.values[0]) / 3600.
print('point: %.2fE %.2fN, depth %.0f m' % (d.lon_rho[j,i], d.lat_rho[j,i], h[j,i]))
print('swing over the run: %.3f m' % (z.max() - z.min()))

fig, ax = plt.subplots(figsize=(11, 4))
ax.plot(t, z, lw=1.5)
ax.axhline(0, color='0.7', lw=0.8)
ax.set_xlabel('hours into the run'); ax.set_ylabel('sea level (m)')
ax.set_title('Tidal sea level at %.2f°E %.2f°S, %.0f m depth'
             % (d.lon_rho[j,i], -d.lat_rho[j,i], h[j,i]))
ax.grid(alpha=0.3)
fig.savefig('docs/img/tides_timeseries.png', dpi=110, bbox_inches='tight')
PYEOF
```

```text
point: 11.98E -6.03N, depth 50 m
swing over the run: 1.321 m
```

![Tidal sea level at a shelf point](../img/tides_timeseries.png)

*Sea level at 11.98°E, 6.03°S in 50 m of water, hourly through the forecast.*

Ten rise-and-fall cycles in five days — **that is M2**, at a 12.4-hour period. A
tide-free run at the same point drifts slowly with no oscillation; this one breathes.

Look also at the envelope: the amplitude grows from about ±0.3 m at the start to ±0.6 m
by the end. That is M2 and S2 drifting into phase with each other — the spring–neap
cycle, and evidence that the multi-constituent forcing is working rather than M2 alone.

### Where the tide is largest

```bash
cd ~/seaforward
python3 << 'PYEOF'
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, xarray as xr, numpy as np
from matplotlib.colors import ListedColormap

D = 'forecast/model-runs/IGOG_12/20260726_plain_tides/fcst/CROCO_FILES/'
d = xr.open_dataset(D + 'croco_his.nc', decode_times=False)
z   = d.zeta.where(d.mask_rho == 1)
rng = (z.max('time') - z.min('time'))

print('tidal range: mean %.2f m   max %.2f m'
      % (float(rng.mean()), float(rng.max())))
h = d.h.values; m = d.mask_rho.values > 0
for lo, hi in [(0,100), (100,500), (500,2000), (2000,9000)]:
    s = m & (h >= lo) & (h < hi)
    print('  %5d-%5d m: mean range %.2f m  (%d cells)'
          % (lo, hi, np.nanmean(rng.values[s]), s.sum()))

lo = float(np.nanpercentile(rng, 2))      # scale to the data, not to zero,
hi = float(np.nanpercentile(rng, 98))     # or a near-uniform field looks flat

fig, ax = plt.subplots(figsize=(7, 7))
ax.pcolormesh(d.lon_rho, d.lat_rho, np.where(d.mask_rho.values == 0, 1, np.nan),
              cmap=ListedColormap(['0.8']), vmin=0, vmax=1)
mm = ax.pcolormesh(d.lon_rho, d.lat_rho, rng, cmap='YlOrRd', vmin=lo, vmax=hi)
ax.contour(d.lon_rho, d.lat_rho, d.h, levels=[200], colors='k', linewidths=0.8)
ax.set_aspect('equal')
ax.set_xlabel('longitude'); ax.set_ylabel('latitude')
ax.set_title('Tidal range over the forecast')
fig.colorbar(mm, ax=ax, label='max - min sea level (m)', shrink=0.8, pad=0.02,
             extend='both')
fig.savefig('docs/img/tides_range.png', dpi=110, bbox_inches='tight')
PYEOF
```

```text
tidal range: mean 1.38 m   max 1.84 m
      0-  100 m: mean range 1.47 m  (715 cells)
    100-  500 m: mean range 1.43 m  (815 cells)
    500- 2000 m: mean range 1.42 m  (1466 cells)
   2000- 9000 m: mean range 1.35 m  (6753 cells)
```

![Tidal range across the domain](../img/tides_range.png)

*Maximum minus minimum sea level over the forecast, with the 200 m isobath.*

The range grows from about 1.28 m in the south-west to over 1.55 m in the north-east
corner of the Bight — the tidal wave amplifying as it propagates into the embayment.
The variation with depth is small, 1.47 m on the shelf against 1.35 m in deep water,
because this domain has little shelf. A wide, shallow shelf gives a far stronger
contrast: tides amplify as they shoal, since the same energy is squeezed into less
water.

Note the colour scale is set from the data's own range rather than from zero. A
near-uniform field plotted from zero looks flat and tells you nothing.

### Does the daily mean still match Mercator?

Compare the daily-mean SSH against Mercator's, and against the same comparison from a
tide-free run. If adding tides hasn't degraded the slow ocean, the two should be close.

!!! important
    **Compare daily means, not hourly.** Mercator has no tides, so an hourly comparison shows the whole tidal signal as error — metres on a shelf. Averaging over 24 hours removes it, which makes the daily mean the only fair comparison.