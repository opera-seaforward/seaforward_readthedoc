# The references

Everything in this chapter compares a run against something. This page covers what those
somethings are, how to get them, and what each cannot do.

## Downloading

One call, sized to the run being validated. It reads the run's dates and grid, widens
them slightly, and fetches only that:

```python
from datetime import datetime, timedelta

clon_full, clat_full, _ = pp.lonlatmask(ds)
DOMAIN = (float(np.nanmin(clon_full)), float(np.nanmax(clon_full)),
         float(np.nanmin(clat_full)), float(np.nanmax(clat_full)))
model_times = pd.to_datetime(pp.times(ds))
START_DATE = model_times[0].to_pydatetime()
END_DATE = model_times[-1].to_pydatetime()
CYCLE_DATE = datetime.strptime(CYCLE, "%Y%m%d")
print(f"Domain: {DOMAIN}")
print(f"Cycle window: {START_DATE} -> {END_DATE}")

# every distinct calendar day covered by this forecast cycle -- Sections 2, 3
# and 4 below each save one figure PER DAY (matching the Section 7 satellite
# comparisons), rather than one figure for just the cycle's last time step.
CYCLE_DAYS = sorted(set(model_times.strftime('%Y-%m-%d')))
print(f"Domain: {DOMAIN}")
print(f"Cycle window: {START_DATE} -> {END_DATE}")
# ---- (i) Copernicus Marine Forecast (Mercator anfc), combined reference file ----
print("\n-- Copernicus Marine Forecast --")
# Daily-mean (P1D-m), not hourly -- the hourly product is far heavier and
# isn't needed here. max_step_hours=30: an existing file's median time step
# should be ~24h (daily) -- anything much coarser means it's a stale/broken
# file, and must be re-downloaded even though its date range looks fine.
if not AVAIL['mercator_forecast']:
    print("unavailable on the CMEMS platform - Sections 2/2b will be skipped.")
elif cmems.netcdf_covers_time_range(REFERENCE, START_DATE, END_DATE, max_step_hours=30):
    print(f"already downloaded and covers the full cycle window at the expected "
         f"resolution: {REFERENCE}")
else:
    if os.path.exists(REFERENCE):
        print(f"{REFERENCE} exists but either doesn't cover the full cycle window "
             f"({START_DATE.date()} -> {END_DATE.date()}) or is at a coarser "
             f"resolution than expected -- re-downloading.")
        os.remove(REFERENCE)
    mercator_dir = os.path.dirname(REFERENCE)
    fdays = max((END_DATE.date() - CYCLE_DATE.date()).days, 0)
    cmems.download_mercator_ops(DOMAIN, CYCLE_DATE, hdays=0, fdays=fdays, outputDir=mercator_dir)

    if cmems.netcdf_covers_time_range(REFERENCE, START_DATE, END_DATE, max_step_hours=30):
        print(f"downloaded -> {REFERENCE}")
    elif os.path.exists(REFERENCE):                                     print(f"download ran but {REFERENCE} still doesn't cover the full cycle window "                                                     f"at the expected resolution -- one or more variable downloads may have "                                                       f"failed; check the log above.")
    else:                                                               print(f"download ran but {REFERENCE} wasn't produced - check {mercator_dir} for the actual filename.")
                                                                # ---- (ii) Satellite SST: OSTIA & ODYSSEA, one file per day ----                                                               print("\n-- Satellite SST --")
SAT_FILES = {}                                                  for product in ("OSTIA", "ODYSSEA"):
    sat_dir = _paths.satellite_dir(MAIN_DIR, CONFIG, CYCLE, product)
    SAT_FILES[product] = cmems.download_satellite_sst(product, DOMAIN, START_DATE, END_DATE, sat_dir)                           
# ---- (ii-b) Satellite SSS: SMOS L4, one file per day ----     print("\n-- Satellite SSS (SMOS) --")
if not AVAIL['smos_l4_sss']:
    print("unavailable on the CMEMS platform - Section 7b will be skipped.")
    SAT_FILES['SMOS'] = {}
else:                                                               smos_dir = _paths.satellite_dir(MAIN_DIR, CONFIG, CYCLE, "SMOS")                                                                SAT_FILES['SMOS'] = cmems.download_satellite_sst("SMOS", DOMAIN, START_DATE, END_DATE, smos_dir)  

    if cmems.netcdf_covers_time_range(REFERENCE, START_DATE, END_DATE, max_step_hours=30):
        print(f"downloaded -> {REFERENCE}")
    elif os.path.exists(REFERENCE):                                     print(f"download ran but {REFERENCE} still doesn't cover the full cycle window "                                                     f"at the expected resolution -- one or more variable downloads may have "                                                       f"failed; check the log above.")
    else:                                                               print(f"download ran but {REFERENCE} wasn't produced - check {mercator_dir} for the actual filename.")
                                                                # ---- (ii) Satellite SST: OSTIA & ODYSSEA, one file per day ----                                                               print("\n-- Satellite SST --")
SAT_FILES = {}                                                  for product in ("OSTIA", "ODYSSEA"):
    sat_dir = _paths.satellite_dir(MAIN_DIR, CONFIG, CYCLE, product)
    SAT_FILES[product] = cmems.download_satellite_sst(product, DOMAIN, START_DATE, END_DATE, sat_dir)                           
# ---- (ii-b) Satellite SSS: SMOS L4, one file per day ----     print("\n-- Satellite SSS (SMOS) --")
if not AVAIL['smos_l4_sss']:
    print("unavailable on the CMEMS platform - Section 7b will be skipped.")
    SAT_FILES['SMOS'] = {}
else:                                                               smos_dir = _paths.satellite_dir(MAIN_DIR, CONFIG, CYCLE, "SMOS")                                                                SAT_FILES['SMOS'] = cmems.download_satellite_sst("SMOS", DOMAIN, START_DATE, END_DATE, smos_dir)  
```

```text
Fetching catalogue 1: 100%|██████████████████████████| 2/2 [00:09<00:00,  4.72s/it]
Domain: (-22.152978897094727, -15.34702205657959, 13.937745094299316, 24.041303634643555)                                       Cycle window: 2026-07-11 00:00:00 -> 2026-07-16 00:00:00
Domain: (-22.152978897094727, -15.34702205657959, 13.937745094299316, 24.041303634643555)
Cycle window: 2026-07-11 00:00:00 -> 2026-07-16 00:00:00

-- Copernicus Marine Forecast --                                already downloaded and covers the full cycle window at the expected resolution: /home/${USER}/seaforward/forecast/model-runs/Canary_12/20260711/downloaded_data/MERCATOR/MERCATOR_20260711_00.nc
-- Satellite SST --
Fetching catalogue 1:   0%|                                  | 0/2 [00:00<?, ?it/s]
Fetching products:   0%|                                     | 0/1 [00:00<?, ?it/s]
Fetching products: 100%|█████████████████████████████| 1/1 [00:02<00:00,  2.04s/it]
Fetching catalogue 1:  50%|█████████████             | 1/2 [00:08<00:08,  8.29s/it]INFO - 2026-09-05T09:03:56Z - Checking if credentials are valid.
  CMEMS product 'ostia_l4' (METOFFICE-GLO-SST-L4-NRT-OBS-SST-V2): available
INFO - 2026-09-05T09:04:01Z - Valid credentials from configuration file.
Fetching catalogue 1: 100%|██████████████████████████| 2/2 [00:18<00:00,  9.23s/it]                                                                                                                                                                             Fetching catalogue 1: 100%|██████████████████████████| 2/2 [00:08<00:00,  4.11s/it]                                               CMEMS product 'odyssea_l3s' (IFREMER-GLOB-SST-L3-NRT-OBS_FULL_TIME_SERIE): available                                          Fetching catalogue 1:   0%|                                  | 0/2 [00:00<?, ?it/s]
Fetching products:   0%|                                     | 0/1 [00:00<?, ?it/s]                                             Fetching products: 100%|█████████████████████████████| 1/1 [00:02<00:00,  2.03s/it]                                             Fetching catalogue 1:  50%|█████████████             | 1/2 [00:09<00:09,  9.44s/it]
  CMEMS product 'smos_l4_sss' (cmems_obs-mob_glo_phy-sss_nrt_multi_P1D): available
                                                             Fetching catalogue 1: 100%|██████████████████████████| 2/2 [00:13<00:00,  6.70s/it]                                             CMEMS: already logged in.
  [OSTIA] 2026-07-11: already downloaded - 2026-07-11.nc          
...
...
```   

The filename carries the window — `2026-07-11_2026-07-16` — so a second cycle does not overwrite the first.

To see what a reference provides before using it:

```python
REFERENCE
```

```text
'/home/${USER}/seaforward/forecast/model-runs/Canary_12/20260711/downloaded_data/MERCATOR/MERCATOR_20260711_00.nc'
```

## What each one is

### OSTIA — SST, gap-free

`METOFFICE-GLO-SST-L4-NRT-OBS-SST-V2`, 0.05°, daily.

An analysis: satellite infrared and microwave observations plus in-situ, optimally
interpolated to fill cloud gaps. Finer than a 1/12° model, so comparing against it
coarsens rather than stretches.

Two things to know. It reports **foundation SST**, the temperature below the diurnal
warm layer, so a midday model SST reads warmer without being wrong — compare daily
means. And it **assimilates in-situ data**, which Mercator also uses, so it is not fully
independent of your boundary conditions.

### ODYSSEA — SST, observations only

`IFREMER-GLOB-SST-L3-NRT-OBS_FULL_TIME_SERIE`, 0.1°, daily.

Merged satellite observations, inter-calibrated across sensors but not interpolated.
Cloud leaves gaps: coverage over the Canary domain in July runs 46–69% of the grid.

More independent than OSTIA, and the harder test. Because of the gaps it must be
compared by **collocation**, not by regridding — see the next page.

It carries a `quality_level` flag, and this product defines exactly one good level:

```text
flag_meanings: missing invalid not_used not_used not_used clear
```

so only level 5 is used. `download_obs` fetches the flag automatically and the
comparison applies it.

### SMOS — SSS, gap-free

`cmems_obs-mob_glo_phy-sss_nrt_multi_P1D`, 0.125°, daily.

Passive-microwave salinity retrieval, gridded and gap-filled onto a regular grid the
same way OSTIA gap-fills SST. Salinity retrievals are noisier than SST ones — the
brightness-temperature signal SMOS measures is far less sensitive to salinity than to
temperature — so day-to-day SMOS variability includes more retrieval noise than day-to-day
CROCO variability does; a mismatch on a single day is weaker evidence of a real model
error than the same-size SST mismatch against OSTIA would be.

Coastal cells are the weak point: L-band retrievals near land are contaminated by
land-emission in the antenna footprint, so SMOS is systematically less reliable close to
shore — exactly the region a coastal-upwelling configuration like this one cares about
most. Treat open-ocean SMOS agreement as more informative than coastal SMOS agreement.

### Mercator and GLORYS — the parent

The product that supplied the initial and boundary conditions. Mercator's
analysis-and-forecast for the forecast track, GLORYS reanalysis for hindcasts.

!!! tips
The following are downloaded via `sftools.validation_obs.download_obs`

### DUACS — sea level

`SEALEVEL_GLO_PHY_L4_NRT_008_046`, 0.125°, daily.

Gridded altimetry: along-track passes mapped onto a regular grid. That mapping smooths
heavily, so it sees far less mesoscale structure than a 1/12° model produces.

`sla` is an anomaly about a mean sea surface; CROCO's `zeta` is elevation about the
model's own reference level. Only the anomalies compare, and the module removes each
field's mean before differencing.

Its geostrophic velocities exclude Ekman flow — use GlobCurrent for currents.

### GlobCurrent — surface currents

`MULTIOBS_GLO_PHY_MYNRT_015_003`, 0.25°, 0 m and 15 m.

**Total** surface current: geostrophic from altimetry plus modelled Ekman from ERA5
wind stress. That total is what CROCO produces, which makes it the right reference for
velocity — unlike DUACS, which gives the geostrophic part alone.

Coarse at 0.25°, so the double penalty applies strongly here.

### ARMOR3D — the subsurface

`MULTIOBS_GLO_PHY_TSUV_3D_MYNRT_015_012`, 1/8°, 50 levels to the bottom.

Temperature, salinity, sea level and mixed-layer depth at depth. Not observations: a
reconstruction that projects surface altimetry downward using covariances derived from
Argo profiles. Real skill in the upper ocean where Argo is dense, less below.

The only depth-resolved reference here that is not the parent product, so it is what
makes a subsurface comparison possible at all.

!!! warning
    **ARMOR3D over a shelf is unreliable.** Argo floats avoid shallow water, so the covariances it relies on are thin there, and at 1/8° a narrow shelf is barely resolved. Comparing at 100 m over the Canary slope gives a bias of +1.2 °C against −0.3 °C in deep water — the difference is a property of the reference, not the model. Use `min_depth=500` to exclude it.


!!! note
Used two ways in this chapter, and the difference matters:

- **As a reference**, it measures consistency — did the downscaling stay close to what
forced it. Useful for catching a run that has gone somewhere strange, but agreement is
partly guaranteed.

- **As a competitor**, scored against the same independent observations as the model. That
is the comparison that answers whether the downscaling improved anything, and it is what
the skill page does.


## Which to use for what

| Comparison | Reference | Why |
|---|---|---|
| SST map, error growth | OSTIA | fine, gap-free, straightforward |
| SST skill | ODYSSEA | independent of in-situ, so the harder test |
| SSS map | SMOS | sea surface salinity observation product |
| Sea level | DUACS | the only altimetry option, but smoothed |
| Surface currents | GlobCurrent | total flow, matching what the model produces |
| Profiles, sections, error against depth | ARMOR3D | the only depth-resolved observation-based product |
| Did the downscaling stay sane? | Mercator | consistency check |
| Did the downscaling help? | Mercator, as a competitor against observations | the question that matters |

## Sizing the download to the run

When several cycles are being compared together, one file covering all of them is simpler than one per cycle: the files are merged then meaned by leading day `(sp1, sp2, fcst1, fcst2, ...)`

