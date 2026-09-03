We use **TPXO10 atlas** — one NetCDF file per wave, split into elevation (`h_`) and
transport (`u_`) files:

```text
DATASETS_CROCOTOOLS/TPXO10/
    grid_tpxo10atlas_v2.nc
    h_m2_tpxo10_atlas_30_v2.nc   u_m2_tpxo10_atlas_30_v2.nc
    h_s2_tpxo10_atlas_30_v2.nc   u_s2_tpxo10_atlas_30_v2.nc
    ...                          (one pair per wave)
```

The atlas format means `multi_files = True`, `waves_separated = True`, and filename
templates with `<tides>` where the wave name goes.

Write the param file into your config's `CROCO_FILES/`, alongside the Mercator one:

```bash
nano ~/seaforward/forecast/scratch/Canary_12/CROCO_FILES/crocotools_param_tides.py
```

```python
# crocotools_param_tides.py — TPXO10 atlas
inputdata       = 'tpxo10'               # the reader dico in Readers/tides_reader.py
input_file      = ''
input_type      = 'Re_Im'                # TPXO stores real/imaginary parts
multi_files     = True
waves_separated = True
elev_file       = 'h_<tides>_tpxo10_atlas_30_v2.nc'
u_file          = 'u_<tides>_tpxo10_atlas_30_v2.nc'
v_file          = 'u_<tides>_tpxo10_atlas_30_v2.nc'   # not a typo — see below
croco_grd       = 'croco_grd.nc'
tides           = ['M2','S2','N2','K2','K1','O1','P1','Q1','Mf','Mm']
cur             = True                   # tidal currents  -> UV_TIDES
pot             = True                   # tidal potential -> POT_TIDES
Correction_ssh  = True                   # nodal corrections
Correction_uv   = True
```

The atlas ships more waves than you need — `2n2`, `m4` and others are in there. That
`tides` list selects which ten get interpolated onto your grid.

Two things that catch people:

- **`v_file` points at the `u_` file.** That looks like a typo and is not. TPXO10
  stores both eastward and northward transport in the same `u_` file, and the reader
  knows which variable to pull from it.
- **The `_v2` in the filenames must match your download.** If yours are `_v6` or
  unversioned, edit the templates. A mismatch produces a "file not found" naming the
  first wave.

Check yours before running:

```bash
ls ~/seaforward/data/DATASETS_CROCOTOOLS/TPXO10/ | head -6
```

TPXO7 — a single `TPXO7.nc` with `multi_files = False` — works identically; the only
difference is the param file. The rest of this chapter is the same whichever you use.