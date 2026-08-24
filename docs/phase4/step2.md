Create the pre-processing parameters in `CF`. It's like the forecast's, with
GLORYS-specific values:

```bash
nano ${CF}/crocotools_param.py
```

```python
inputdata     = 'mercator'                                  # GLORYS reads through the 'mercator' reader
Nzgoodmin     = 4
multi_files   = False
tracers       = ['temp', 'salt']
croco_grd     = 'croco_grd.nc'
sigma_params  = dict(theta_s=7, theta_b=2, N=50, hc=200)    # same vertical grid as forecast
ini_prefix    = 'croco_ini_GLORYS'
bry_prefix    = 'croco_bry_GLORYS'
obc_dict      = dict(south=1, west=1, east=0, north=1)      # same Canary boundaries
cycle_bry     = 0
```

**Line by line — what's different from the forecast:**

- `inputdata = 'mercator'` — **not** `'glorys'`. GLORYS from CMEMS uses the same variable names as Mercator (`zos, thetao, so, uo, vo`), so it reads through the reader's `'mercator'` branch. (Verified: the reader `ibc_class.py` maps `'mercator'` → `ssh:zos, temp:thetao, salt:so, u:uo, v:vo` — exactly GLORYS.)
- `ini_prefix`/`bry_prefix` → `GLORYS` so hindcast files are distinct from forecast `MERCATOR` ones.
- `sigma_params`, `obc_dict` — **identical** to the forecast (same grid, same boundaries).

!!! warning
    ⚠️ **WATCH — it's `'mercator'`, not `'glorys'`.** There is no `'glorys'` key in the reader. GLORYS's CMEMS variable names match the `'mercator'` mapping, so that's the one to use. `'mercator_croco'` is a *different* mapping (renamed variables) — not your raw GLORYS.