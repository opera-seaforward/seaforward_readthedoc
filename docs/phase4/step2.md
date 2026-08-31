Create the pre-processing parameters in `CF`. It's the forecast's file with
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

Keep a copy with the recipe: `cp ${CF}/crocotools_param.py ${CONFIG_DIR}/`.

**What's different from the forecast:**

- `ini_prefix` / `bry_prefix` → `GLORYS`, so the hindcast files are distinct from the
  forecast's `MERCATOR` ones.
- `sigma_params` and `obc_dict` are **identical** — same grid, same boundaries.
- `inputdata` is **unchanged**, and that surprises people. See the warning below.

!!! warning
    **It stays `'mercator'` — there is no `'glorys'` key in the reader.** GLORYS from CMEMS uses the same variable names as Mercator (`zos`, `thetao`, `so`, `uo`, `vo`), so it reads through the `'mercator'` branch: `ibc_class.py` maps `'mercator'` → `ssh:zos, temp:thetao, salt:so, u:uo, v:vo`, which is exactly GLORYS. Note that `'mercator_croco'` is a *different* mapping with renamed variables — not your raw GLORYS.