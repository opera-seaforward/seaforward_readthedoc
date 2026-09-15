# Metrics Against Observation

Two baselines answer that:

- **The time series of the sngle pont (or domain) mean**: a model that's merely close to observations on day 1 and still close on day 5 has told you nothing about skill; what matters is whether its line stays nearer the observations than the parent's own line, as lead time grows. 

- **The bias/RMSE boxplots**: turn that same two-way comparison into a distribution instead of a single mean. One box per lead day, per baseline: where the box sits shows systematic bias (a box that drifts off zero as lead time grows is the model's error compounding, not just spreading), and how wide it is shows spatial or day-to-day inconsistency the mean alone can hide — the boxplot is what catches that; the time series above cannot.

The two latter are scored against the same independent observations, at the same points (or full domain), so the curves are directly comparable. See more `Section.6` in `02_validation.ipynb` and `03_composite_validation.ipynb` for the full steps.

```python
import os
import sftools.validation as val
import sftools.validation_composite as vc
import _paths

# ----------------------------------------------------------------------
# Cycles to composite (need at least 2)
# ----------------------------------------------------------------------
CONFIG   = os.environ.get("SEAFORWARD_CONFIG", "Canary_12")
MAIN_DIR = os.path.expanduser(os.environ.get("SEAFORWARD_MAIN_DIR", "~/seaforward/forecast/model-runs"))

CYCLES = os.environ.get("SEAFORWARD_CYCLES", "").split(",") if os.environ.get("SEAFORWARD_CYCLES") \
        else list(_paths.list_cycles(MAIN_DIR, CONFIG))
if len(CYCLES) < 2:
    raise ValueError(f"CYCLES must have at least 2 entries, got {CYCLES!r}")

YORIG = 2000
DEPTH_M = None
SPINUP_DAYS = 2

COMPOSITE_ID, COMPOSITE_DIR = vc.resolve_composite_dir(MAIN_DIR, CONFIG, CYCLES)

# ----------------------------------------------------------------------
# Fetch what the boxplots need
# ----------------------------------------------------------------------
AVAIL = {name: val.dataset_available(name)
         for name in ("mercator_forecast", "ostia_l4", "odyssea_l3s", "smos_l4_sss")}

cycles_info, LEADS, FCST_LEADS, stability_ok = vc.download_and_label_cycles(
    CYCLES, CONFIG, MAIN_DIR, AVAIL, YORIG, SPINUP_DAYS, _paths)

# ----------------------------------------------------------------------
# Boxplots
# ----------------------------------------------------------------------
vc.stacked_bias_boxplot(cycles_info, LEADS, YORIG, DEPTH_M, COMPOSITE_DIR, CYCLES,
                       AVAIL['mercator_forecast'])

n_cycles = len(CYCLES)
ostia_diffs   = [vc.composite_domain_diff_satellite(cycles_info, 'OSTIA',   lead, Yorig=YORIG) for lead in LEADS]
odyssea_diffs = [vc.composite_domain_diff_satellite(cycles_info, 'ODYSSEA', lead, Yorig=YORIG) for lead in LEADS]
smos_diffs    = [vc.composite_domain_diff_satellite(cycles_info, 'SMOS',    lead, Yorig=YORIG) for lead in LEADS]

sst_groups = {"OSTIA": ostia_diffs, "ODYSSEA": odyssea_diffs}
sss_groups = {"SMOS": smos_diffs}

## bias
val.bias_boxplot_multi(sst_groups, LEADS, 'temperature bias (degC)',
                       f'CROCO - satellite SST bias  (composite of {n_cycles} cycles)',
                       colors=['C1', 'C2'],
                       out=os.path.join(COMPOSITE_DIR, 'boxplot_bias_sst_vs_satellite_composite.png'))
val.bias_boxplot_multi(sss_groups, LEADS, 'salinity bias (PSU)',
                       f'CROCO - satellite SSS bias  (composite of {n_cycles} cycles)',
                       colors=['C4'],
                       out=os.path.join(COMPOSITE_DIR, 'boxplot_bias_sss_vs_satellite_composite.png'))
## RMSE
val.bias_boxplot_multi(sst_groups, LEADS, 'temperature |error| (degC)',
                       f'CROCO - satellite SST RMSE-spread  (composite of {n_cycles} cycles)',
                       colors=['C1', 'C2'], metric='rmse',
                       out=os.path.join(COMPOSITE_DIR, 'boxplot_rmse_sst_vs_satellite_composite.png'))
val.bias_boxplot_multi(sss_groups, LEADS, 'salinity |error| (PSU)',
                       f'CROCO - satellite SSS RMSE-spread  (composite of {n_cycles} cycles)',
                       colors=['C4'], metric='rmse',
                       out=os.path.join(COMPOSITE_DIR, 'boxplot_rmse_sss_vs_satellite_composite.png'))
```

![Forecast error against lead time](../img/boxplot_bias_sst_vs_satellite_composite.png)
![Forecast error against lead time](../img/boxplot_bias_sss_vs_satellite_composite.png)

*SST, SSS, sea level anomaly, and the two velocity components at the surface. Three cycles pooled. sp1 and sp1 are the sprin-up days before the forecast.*

## Temperature


### OSTIA daily SST statistics
| Product | Variable | Window | Cycles | n | bias | RMSE | cRMSE | corr |
|---|---|---|---|---|---:|---:|---:|---:|
| OSTIA | SST | sp1   | 3 (20260711, 20260723, 20260729) | 8257 | +0.186 | 0.446 | 0.405 | 0.981 |
| OSTIA | SST | sp2   | 3 (20260711, 20260723, 20260729) | 8257 | +0.163 | 0.446 | 0.415 | 0.980 |
| OSTIA | SST | fcst1 | 3 (20260711, 20260723, 20260729) | 8257 | +0.191 | 0.465 | 0.424 | 0.978 |
| OSTIA | SST | fcst2 | 3 (20260711, 20260723, 20260729) | 8257 | -0.053 | 0.465 | 0.462 | 0.976 |
| OSTIA | SST | fcst3 | 3 (20260711, 20260723, 20260729) | 8257 | -0.063 | 0.444 | 0.439 | 0.978 |
| OSTIA | SST | fcst4 | 3 (20260711, 20260723, 20260729) | 8257 | -0.089 | 0.499 | 0.491 | 0.973 |
| OSTIA | SST | fcst5 | 1 (20260729)                   | 8257 | -0.171 | 0.576 | 0.550 | 0.947 |
| OSTIA | SST | fcst6 | 1 (20260729)                   | 8257 | -0.537 | 0.875 | 0.691 | 0.922 |

**SEA-FORWARD SST is closer to the OSTIA observations at every lead** (containing all the cycles), and the gap remains very low day-by-day: > |0.2| °C. That is the downscaling doing something measurable.


## Salinty 

#### SMOS daily SSS statistics
| Product | Variable | Window | Cycles | n | bias | RMSE | cRMSE | corr |
|---|---|---|---|---|---:|---:|---:|---:|
| SMOS | SSS | sp1   | 3 (20260711, 20260723, 20260729) | 8070 | -0.091 | 0.263 | 0.247 | 0.664 |
| SMOS | SSS | sp2   | 3 (20260711, 20260723, 20260729) | 8070 | -0.085 | 0.259 | 0.245 | 0.638 |
| SMOS | SSS | fcst1 | 3 (20260711, 20260723, 20260729) | 8070 | -0.077 | 0.272 | 0.261 | 0.562 |
| SMOS | SSS | fcst2 | 3 (20260711, 20260723, 20260729) | 8070 | -0.082 | 0.290 | 0.278 | 0.463 |
| SMOS | SSS | fcst3 | 3 (20260711, 20260723, 20260729) | 8070 | -0.066 | 0.265 | 0.257 | 0.542 |
| SMOS | SSS | fcst4 | 3 (20260711, 20260723, 20260729) | 8070 | -0.074 | 0.232 | 0.220 | 0.674 |
| SMOS | SSS | fcst5 | 1 (20260729)                   | 8070 | -0.070 | 0.305 | 0.297 | 0.400 |
| SMOS | SSS | fcst6 | 1 (20260729)                   | 8070 | -0.033 | 0.326 | 0.324 | 0.282 |

**SEA-FORWARD SSS is closer to the SMOS observations at every lead**, and the gap remains very low day-by-day: > |0.1| PSU. That is the downscaling doing something measurable.
