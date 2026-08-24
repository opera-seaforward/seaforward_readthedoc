We use **TPXO10 atlas** — one NetCDF file per wave, split into elevation (`h_`)
and transport (`u_`) files:

```
DATASETS_CROCOTOOLS/TPXO10/
    h_m2_tpxo10_atlas_30_v2.nc   u_m2_tpxo10_atlas_30_v2.nc
    h_s2_tpxo10_atlas_30_v2.nc   u_s2_tpxo10_atlas_30_v2.nc
    ...                          (one pair per wave)
    grid_tpxo10atlas_v2.nc
```

The atlas format means `multi_files = True`, `waves_separated = True`, and
filename templates with `<tides>` where the wave name goes. The tide param file:

```python
# crocotools_param_tides.py — TPXO10 atlas
inputdata      = 'tpxo10'               # the reader dico in Readers/tides_reader.py
input_file     = ''
input_type     = 'Re_Im'                # TPXO stores real/imaginary parts
multi_files    = True
waves_separated = True
elev_file      = 'h_<tides>_tpxo10_atlas_30_v2.nc'
u_file         = 'u_<tides>_tpxo10_atlas_30_v2.nc'
v_file         = 'u_<tides>_tpxo10_atlas_30_v2.nc'   # not a typo: both u,v live in the u_ file
croco_grd      = 'croco_grd.nc'
tides          = ['M2','S2','N2','K2','K1','O1','P1','Q1','Mf','Mm']
cur            = True                    # tidal currents  -> UV_TIDES
pot            = True                    # tidal potential -> POT_TIDES
Correction_ssh = True                   # nodal corrections
Correction_uv  = True
```

Two things that catch people:

- **`v_file` points at the `u_` file.** TPXO10 stores both eastward and
  northward transport in the same `u_` file; the reader knows which variable to
  pull. Copy somisana's setting rather than second-guessing it.
- **The `_v2` in the filenames must match your download.** If yours are `_v6` or
  unversioned, edit the templates. A mismatch produces a "file not found" naming
  the first wave.

TPXO7 (a single `TPXO7.nc`, `multi_files = False`) works identically; the only
difference is the param file. The rest of this chapter is the same whichever you
use — the data source is the last thing that changes, not the first.