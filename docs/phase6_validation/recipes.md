# Doing this for your own run

Everything in this chapter is a call on `sftools.validation_obs`, and every example uses
the same three ingredients: a run, a reference, and `Yorig`. This page covers how to get
those for a configuration that is not Canary_12.

## 1. Where the observations go

There is no fixed location, but the examples use:

```text
~/seaforward/data/OBS/
```

alongside `data/DATASETS_CROCOTOOLS/`, which Phase 1 sets up for the static datasets.
Observations differ from those: they are per-run rather than build-once, so they
accumulate. The filenames carry their window — `ostia_2026-07-10_2026-07-17.nc` — which
keeps cycles apart and makes it obvious what can be deleted.

```bash
mkdir -p ~/seaforward/data/OBS
```

## 2. Downloading

`download_obs` reads the run's dates and grid and fetches only that:

```bash
cd ~/seaforward
python3 << 'PYEOF'
import sftools.validation_obs as vo

HIS = 'forecast/model-runs/Canary_12/20260711/fcst/CROCO_FILES/croco_his.nc'
OBS = '~/seaforward/data/OBS'

for src in ('ostia', 'odyssea', 'duacs', 'globcurrent', 'armor3d'):
    print(vo.download_obs(HIS, src, OBS, Yorig=2000))
PYEOF
```

Five files, each covering that one cycle.

**For several cycles, one file each is awkward** — the skill figure needs every cycle
scored against the same reference, and a file that stops short raises. Size the request
against the *last* cycle and pad backwards far enough to reach the first:

```bash
cd ~/seaforward
python3 << 'PYEOF'
import sftools.validation_obs as vo

LAST = 'forecast/model-runs/Canary_12/20260713/fcst/CROCO_FILES/croco_his.nc'
OBS  = '~/seaforward/data/OBS'

for src in ('odyssea', 'duacs', 'globcurrent'):
    print(vo.download_obs(LAST, src, OBS, Yorig=2000, pad_days=6))
PYEOF
```

`pad_days=6` widens the window by six days on each side. One file per product then covers
every cycle, and the filename says so.

!!! note
    `copernicusmarine` writes `name_(1).nc` rather than overwriting when the target exists. `download_obs` deletes first when `force=True`, but a file downloaded by hand into the same name will silently leave you reading the old one. Check the timestamp if a re-download seems to have changed nothing.

## 3. Changing the region

Nothing changes but the paths. The functions read the grid from the file, so the domain,
the resolution and the coastline all follow:

```bash
cd ~/seaforward
python3 << 'PYEOF'
import matplotlib; matplotlib.use('Agg')
import sftools.validation_obs as vo

HIS = 'forecast/model-runs/IGOG_12/20260726_plain/fcst/CROCO_FILES/croco_his.nc'
OBS = '~/seaforward/data/OBS'

ost = vo.download_obs(HIS, 'ostia', OBS, Yorig=2000)
vo.compare(HIS, ost, 'temp', daily_mean=True, Yorig=2000, out='igog_sst.png')
PYEOF
```

Two things to check for a new region.

**Coverage.** A gappy product may see much less of a cloudy domain than of a clear one.
`scorecard` prints the percentage per day; below about 50% the numbers rest on half the
map.

**And whether the reference suits the region.** ARMOR3D over a wide shelf is unreliable
for the reasons the references page gives, and GlobCurrent at 0.25° over a small domain
may leave too few cells to be meaningful — the Canary domain has 2643, which is already
few.

## 4. Validating a hindcast

Two changes: the multi-year reference track, and the year origin.

```bash
cd ~/seaforward
python3 << 'PYEOF'
import matplotlib; matplotlib.use('Agg')
import sftools.validation_obs as vo

HIS = 'hindcast/model-runs/Canary_12/20251225/hcast/CROCO_FILES/croco_his.nc'
OBS = '~/seaforward/data/OBS'

ost = vo.download_obs(HIS, 'ostia', OBS, Yorig=1993, track='my')
vo.compare(HIS, ost, 'temp', daily_mean=True, Yorig=1993, out='hcast_sst.png')
PYEOF
```

`track='my'` selects the reprocessed twin of each product — the same split as Mercator and
GLORYS, and for the same reason: the near-real-time series is produced quickly and revised
later, the multi-year one is the settled version.

`Yorig=1993` because that is what the hindcast track uses. Passing the forecast's 2000
would put the run three decades from the observations, and the date guard would raise.

Not every product has both. `duacs` is near-real-time only in this registry; asking for
`track='my'` says so rather than failing obscurely.

## 5. Adding a reference

The registry is a dictionary at the top of `validation_obs.py`. An entry looks like:

```python
    "ostia": dict(
        nrt="METOFFICE-GLO-SST-L4-NRT-OBS-SST-V2",
        my="METOFFICE-GLO-SST-L4-REP-OBS-SST",
        vars={"temp": "analysed_sst"},
        offset=-273.15,                 # OSTIA ships kelvin
        scale=1.0,
        has_depth=False,
        note="foundation SST — the temperature below the diurnal warm layer, "
             "so a midday model SST can read warmer without being wrong",
    ),
```

| Field | |
|---|---|
| `nrt`, `my` | the `copernicusmarine` dataset IDs; `None` where a product has only one |
| `vars` | our short names mapped to the product's own variable names |
| `offset`, `scale` | conversion to our units — celsius, metres, m/s |
| `has_depth` | whether `depth_m` applies |
| `gappy` | `True` for an L3 product, which routes comparisons through collocation |
| `qc` | `{"var": ..., "min": ...}` for a quality flag, downloaded and applied automatically |
| `note` | printed after a download; put the product's main caveat here |

Find the dataset ID and the variable names from CMEMS rather than guessing:

```bash
conda activate seaforward
copernicusmarine describe --contains "<product ID>" | grep '"dataset_id"'
copernicusmarine describe --contains "<dataset ID>" | grep '"short_name"'
```

Then download a single day and look at what arrived — units and dimensions included, since
those decide `offset` and `has_depth`:

```bash
cd ~/seaforward
copernicusmarine subset --dataset-id <dataset ID> \
  --start-datetime 2026-07-12 --end-datetime 2026-07-12 \
  --minimum-longitude -22 --maximum-longitude -15.5 \
  --minimum-latitude 14 --maximum-latitude 24 \
  --output-directory /tmp/newref

python3 -c "
import xarray as xr, glob
d = xr.open_dataset(glob.glob('/tmp/newref/*.nc')[0])
for v in d.data_vars:
    print('  %-34s %-10s %s' % (v, d[v].attrs.get('units',''), d[v].dims))
"
```

Finally, `identify()` needs a line so the new product is recognised from its variables —
that is what lets every function take a bare path without being told which product it is.

!!! warning
    **Check the units.** A kelvin product compared without the offset gives a bias of −273, which is obvious. A product in cm rather than m gives a bias that looks plausible and is wrong by a factor of a hundred. The `offset` and `scale` fields exist for this, and the one-day download above is how to find out which are needed.

## What the module gives you

| Function | |
|---|---|
| `download_obs` | fetch a product sized to a run |
| `describe` | what each reference provides |
| `compare` | one map, or one date's statistics |
| `compare_days` | a grid of days, gap-free references |
| `collocate`, `scorecard` | statistics in observation space, for gappy products |
| `collocate_days`, `plot_collocation` | the same, drawn |
| `persistence` | one run against its own initial state |
| `three_way`, `skill_panels` | the model, the parent and persistence together |
| `composite`, `composite_panels` | several cycles pooled by lead time |

Sections and profiles live in `sftools.validation` — `compare_section`, `compare_profile`,
`error_vs_depth` — and are covered on the previous page.