# The references

Everything in this chapter compares a run against something. This page covers what those
somethings are, how to get them, and what each cannot do.

## Downloading

One call, sized to the run being validated. It reads the run's dates and grid, widens
them slightly, and fetches only that:

```python
import sftools.validation_obs as vo

HIS = "forecast/model-runs/Canary_12/20260711/fcst/CROCO_FILES/croco_his.nc"

ost = vo.download_obs(HIS, "ostia", "~/seaforward/data/OBS", Yorig=2000)
```

```text
ostia: METOFFICE-GLO-SST-L4-NRT-OBS-SST-V2
  2026-07-10 .. 2026-07-17   lon -22.65..-14.85  lat 13.44..24.54
```

The filename carries the window — `ostia_2026-07-10_2026-07-17.nc` — so a second cycle
does not overwrite the first.

`track="nrt"` is the default, for forecasts. Hindcasts want `track="my"`, the multi-year
reprocessed twin, the same split as Mercator and GLORYS.

!!! warning
    **`Yorig` is required.** A CROCO file written without CF time units carries raw seconds, and without a reference year the download would silently request the wrong decade. Pass 2000 for the forecast track, 1993 for hindcasts. Every function in the module raises rather than guessing.

To see what a reference provides before using it:

```python
vo.describe("armor3d")
```

## What each one is

### OSTIA — SST, gap-free

`SST_GLO_SST_L4_NRT_OBSERVATIONS_010_001`, 0.05°, daily.

An analysis: satellite infrared and microwave observations plus in-situ, optimally
interpolated to fill cloud gaps. Finer than a 1/12° model, so comparing against it
coarsens rather than stretches.

Two things to know. It reports **foundation SST**, the temperature below the diurnal
warm layer, so a midday model SST reads warmer without being wrong — compare daily
means. And it **assimilates in-situ data**, which Mercator also uses, so it is not fully
independent of your boundary conditions.

### ODYSSEA — SST, observations only

`SST_GLO_SST_L3S_NRT_OBSERVATIONS_010_010`, 0.1°, daily.

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

### Mercator and GLORYS — the parent

The product that supplied the initial and boundary conditions. Mercator's
analysis-and-forecast for the forecast track, GLORYS reanalysis for hindcasts.

Used two ways in this chapter, and the difference matters:

**As a reference**, it measures consistency — did the downscaling stay close to what
forced it. Useful for catching a run that has gone somewhere strange, but agreement is
partly guaranteed.

**As a competitor**, scored against the same independent observations as the model. That
is the comparison that answers whether the downscaling improved anything, and it is what
the skill page does.

## Which to use for what

| Comparison | Reference | Why |
|---|---|---|
| SST map, error growth | OSTIA | fine, gap-free, straightforward |
| SST skill | ODYSSEA | independent of in-situ, so the harder test |
| Sea level | DUACS | the only altimetry option, but smoothed |
| Surface currents | GlobCurrent | total flow, matching what the model produces |
| Profiles, sections, error against depth | ARMOR3D | the only depth-resolved observation-based product |
| Did the downscaling stay sane? | Mercator | consistency check |
| Did the downscaling help? | Mercator, as a competitor against observations | the question that matters |

## Sizing the download to the run

`download_obs` derives its request from the run itself:

```python
vo.run_window(HIS, Yorig=2000)     # ('2026-07-10', '2026-07-17')
vo.run_domain(HIS, Yorig=2000)     # (-22.65, -14.85, 13.44, 24.54)
```

The window is padded by a day on each side, because a daily mean is centred at noon
while a run starts at midnight — the first model record needs the previous day's field
to bracket it. The domain is widened by 0.5°, so interpolation onto the model grid has
reference points beyond the edge rather than extrapolating.

When several cycles are being compared together, one file covering all of them is
simpler than one per cycle:

```python
# the last cycle runs latest; pad backwards to reach the first cycle's start
vo.download_obs(LAST_HIS, "odyssea", "~/seaforward/data/OBS",
                Yorig=2000, pad_days=6)
```

!!! note
    A reference that does not span the run raises rather than substituting the nearest available day. That guard exists because a silent nearest-match compares one day's model against another day's observations and reports it as a result — the difference is small enough to look plausible and large enough to change the answer.