This is where the **upstream data sources become model inputs**. You do it in the
order you actually run it: **download the forcing data first, then shape it** into
what the model reads. The workflow diagram has exactly these two columns — the
downloads on the left, the prepared inputs in the middle.

The sources involved:

- **Global ocean forecast** (Mercator) → the initial condition and boundaries
- **Atmosphere** (GFS) → the surface forcing
- **Tides** (TPXO) → *optional*, skipped in this tide-free forecast

(Bathymetry was the fourth source — already wired in at the grid, Step 2.) This
guide produces the **tide-free** forecast, so you download and prepare the ocean
and atmosphere, and stop.

First set up the shared bits:

```bash
cd ${SEAFORWARD}
export RUN_DT="$(date -u +'%Y-%m-%d') 00:00:00"
```

!!! warning
    ⚠️ **WATCH — negative longitudes need `--domain=` with an equals sign.** Because your box is west of Greenwich, the domain string starts with `-`, and the command reader mistakes it for an option unless you attach it with `=`. Use `--domain="${EXTENTS}"`.

### 5a — Download the forcing data

![build progress](../img/atmosphere_ocean.png)

*First, pull down both global datasets — the ocean and the atmosphere. Nothing is shaped yet; you're just fetching the raw data your region sits inside.*

**Download the global ocean** (Mercator). It asks for your Copernicus Marine login the first time, then remembers it.

```bash
python seaforward.py download_ocean \
    --domain="${EXTENTS}" --run_date "${RUN_DT}" \
    --hdays ${HDAYS} --fdays ${FDAYS} \
    --outputDir ${FCAST}/downloaded_data/MERCATOR
```

**Download the global weather** (GFS).

```bash
python seaforward.py download_atmosphere \
    --domain="${EXTENTS}" --run_date "${RUN_DT}" \
    --hdays ${HDAYS} --fdays ${FDAYS} \
    --outputDir ${FCAST}/downloaded_data/GFS
```

!!! check
    ✅ **CHECK** — both `downloaded_data/MERCATOR` and `downloaded_data/GFS` now hold raw global files covering your download box.


### 5b — Prepare the model inputs

Now shape the raw downloads onto your grid. Each source becomes its own model
input: the **ocean** becomes the initial and boundary conditions, the
**atmosphere** becomes the surface forcing. Do them in turn.

**From the ocean → initial + boundary conditions**

![build progress](../img/init_bound_conditions.png)

*The global ocean forecast supplies the state your model starts from and the values that flow in at the open edges the one Mercator file you downloaded. The figure below shows how this is functionally implemented.*

![Workflow for ingesting Global Ocean Forecast (OM) data alongside model_grid.nc and -run-date, processed via SEA_FORWARD pytools (subset-clim-oce, subset-mod-oce, format-converter-oce) and the Ocean-to-model step (extrapolation → interpolation → processing-oce), producing ocean-model, ocean-model-initial-input, and ocean-model-obc (open boundary conditions)-input outputs linked to V1, C1, and D1.](../img/ocean_model_U2.png)

Build the **initial condition** (the ocean's state at the start):

```bash
export MERC=${FCAST}/downloaded_data/MERCATOR/MERCATOR_$(date -u +'%Y%m%d')_00.nc
python seaforward.py make_ini \
    --input_file ${MERC} --output_dir ${CF} \
    --run_date "${RUN_DT}" --hdays ${HDAYS} --Yorig ${YORIG}
```

!!! check
    ✅ **CHECK** — it interpolates temp/salt/u/v onto the sigma layers and prints `Initial file created … croco_ini_MERCATOR_<date>_00.nc`.

Build the **boundary conditions** (what flows in at the open edges over time):

```bash
python seaforward.py make_bry \
    --input_file ${MERC} --output_dir ${CF} \
    --run_date "${RUN_DT}" --hdays ${HDAYS} --fdays ${FDAYS} --Yorig ${YORIG}
```

!!! check
    ✅ **CHECK** — it processes **south, west, north** and **skips east**. That's your `obc_dict` in action: it only builds data for the *open* boundaries. The mask, `obc_dict`, and the `OBC_*` switches all describe the same set of open edges.

**From the atmosphere → surface forcing**

![build progress](../img/surface_forcing.png)

*The global weather becomes the surface forcing — the ten files (wind, heat, radiation, pressure, humidity, precipitation) CROCO reads at every timestep. The figure below shows how this is functionally implemented*

![Workflow for preparing atmospheric forcing from the Global Forecasting System (ATM), -run-date, and model_grid.nc, run through SEA_FORWARD pytools (subset-mod-atm, format-converter-atm) and the Ocean-to-model chain (extrapolation → processing-atm → interpolation → grid-transformation), yielding atm-upstr-input and atm-model outputs linked to C1, V1, and D1.](../img/atmosphere_U3.png)

Build the **surface forcing**:

```bash
python seaforward.py make_forcing \
    --gfsDir ${FCAST}/downloaded_data/GFS \
    --outputDir ${FCAST}/downloaded_data/GFS/for_croco \
    --Yorig ${YORIG}
ls ${FCAST}/downloaded_data/GFS/for_croco/*.nc | wc -l   # expect 10
```

!!! check
    ✅ **CHECK** — it works through Temperature, Humidity, Precipitation, the four radiation fluxes, U/V wind, and pressure, then `10` files exist.

**Fix the GFS longitudes — only for western-hemisphere regions.** GFS labels
longitude from 0 to 360; your model uses −180 to 180. For a region west of
Greenwich these don't match, and the model would crash reading the weather
forcing. Check whether you're affected:

```bash
python3 -c "
import xarray as xr
g = xr.open_dataset('${CF}/croco_grd.nc')
f = xr.open_dataset('${FCAST}/downloaded_data/GFS/for_croco/TEMPERATURE_HEIGHT_ABOVE_GROUND_Y9999M01.nc')
print('MODEL   lon: %.2f .. %.2f' % (float(g.lon_rho.min()), float(g.lon_rho.max())))
print('FORCING lon: %.2f .. %.2f' % (float(f.lon.min()), float(f.lon.max())))
print('covers?', float(f.lon.min())<=float(g.lon_rho.min()) and float(f.lon.max())>=float(g.lon_rho.max()))
"
```

If it says `covers? False` and the forcing lon numbers are big (like 336..346),
run the one-time conversion that shifts the axis to −180..180:

```bash
cd ${FCAST}
python3 << 'PYEOF'
import xarray as xr, glob, os
for f in sorted(glob.glob('downloaded_data/GFS/for_croco/*.nc')):
    d = xr.open_dataset(f); lon = d['lon'].values
    if lon.max() > 180:
        d = d.assign_coords(lon=((lon + 180) % 360) - 180).sortby('lon')
        tmp=f+'.tmp'; d.to_netcdf(tmp); d.close(); os.replace(tmp, f)
        print('fixed', os.path.basename(f))
    else:
        d.close()
print('done')
PYEOF
```

!!! check 
    ✅ **CHECK** — re-run the check above; it should now say `covers? True` with forcing lon around your box. Eastern-hemisphere regions skip this — their GFS longitudes already fall in range.


### 5c — Tides

![build progress](../img/tidal_forcing.png)

*Tides are the one forcing no global ocean product carries. If your domain has a shelf or coast where the tide is a large signal, you add it from a tidal atlas (TPXO); deep open-ocean domains skip it.*

This guide builds the **tide-free** forecast, so you do not build this source here.
For completeness, in the same download-then-shape pattern:

- **There is nothing to download per cycle** — the TPXO atlas is a fixed dataset —
  but the tide file *is* regenerated each cycle, because its phase is keyed to the
  run's start date.
- **Shape the atlas onto your grid** with a single tool (`make_tides`), which writes
  a `croco_frc.nc` tidal-forcing file.
- **Turn tides on at compile time** with the `TIDES` switch in `cppdefs.h`, so a
  tidal run is a *different binary* — the same compile-time-vs-run-time distinction
  you meet at Step 7.

Because tides touch both the data preparation *and* the compile step, they are a
chapter of their own. **See Phase 10 (Tides)** for the full build. You leave this
source out of the tide-free forecast.

### 5d — Confirm your inputs are in place

```bash
ls -lh ${CF}/croco_ini_MERCATOR*.nc ${CF}/croco_bry_MERCATOR*.nc
ls ${FCAST}/downloaded_data/GFS/for_croco/*.nc | wc -l   # 10
```

You now have the two sources this forecast needs: the **ocean** (ini + bry) and the **atmosphere** (surface forcing). **Bathymetry** was already wired in at the grid (Step 2). **Tides** are the optional third source, skipped here. That is the full upstream picture for a forecast.