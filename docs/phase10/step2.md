**TPXO10 atlas** is the finer alternative — one NetCDF file per wave, split into
elevation (`h_`) and transport (`u_`) files:

``` { .text .no-copy }
DATASETS_CROCOTOOLS/TPXO10/
    grid_tpxo10atlas_v2.nc
    h_m2_tpxo10_atlas_30_v2.nc   u_m2_tpxo10_atlas_30_v2.nc
    h_s2_tpxo10_atlas_30_v2.nc   u_s2_tpxo10_atlas_30_v2.nc
    ...                          (one pair per wave)
```

The atlas format means `multi_files = True`, `waves_separated = True`, and filename
templates with `<tides>` where the wave name goes.

Everything else is exactly [Step 1](step1.md) — same generation directory, same
command. Only the param file's contents change:

```bash
TGEN=~/seaforward/forecast/scratch/Canary_12/tide_gen/CROCO_FILES

cat > "$TGEN/crocotools_param.py" << 'EOF'
inputdata       = 'tpxo10'               # a tag from Readers/tides_reader.py
input_file      = ''                     # unused when multi_files = True
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
EOF
```

Then the same command as Step 1, pointed at the atlas directory:

```bash
cd ~/seaforward/sftools
conda activate seaforward

python seaforward.py make_tides \
    --input_dir ~/seaforward/data/DATASETS_CROCOTOOLS/TPXO10/ \
    --output_dir "$TGEN" \
    --run_date "$(date -u +'%Y-%m-%d') 00:00:00" \
    --Yorig 2000 \
    --fname_out croco_frc.nc
```

Three things that catch people:

- **`v_file` points at the `u_` file.** That looks like a typo and is not. TPXO10
  stores both eastward and northward transport in the same `u_` file, and the reader
  knows which variable to pull from it.
- **The `_v2` in the filenames must match your download.** If yours are `_v6` or
  unversioned, edit the templates. A mismatch produces *"Elevation file ... for wave
  M2 is missing"*, naming the exact path it tried — read it and compare.
- **The `tides` list must match what you actually downloaded.** The atlas ships more
  waves than you need (`2n2`, `m4` and others), but it may also ship fewer than the ten
  above. A wave you ask for and do not have stops the run *after* the earlier ones have
  been written, so a partial `croco_frc.nc` is not evidence it worked.

Check what you have before running:

```bash
ls ~/seaforward/data/DATASETS_CROCOTOOLS/TPXO10/
```

## Which one to use

| | TPXO7 | TPXO10 atlas |
| --- | --- | --- |
| where it comes from | ships with the CROCO datasets, Phase 1 | Oregon State University, on request |
| layout | one `TPXO7.nc` | one `h_` + `u_` pair per wave |
| param file | `multi_files = False` | `multi_files = True`, `waves_separated = True` |
| constituents | the eight diurnal and semi-diurnal | more, including the long-period `Mf` and `Mm` |

TPXO7 is enough to get tidal forcing working and is already on your machine, so start
there. TPXO10 is finer and carries the long-period constituents, which matter if you
care about fortnightly and monthly signals. The rest of this chapter is the same
whichever you use.

!!! tip
    **Keeping both.** `make_tides` imports a module named `crocotools_param`, so only
    one can live in a directory under that name. To hold both, name them differently
    and say which to use:

```bash
    cp tpxo7_params.py  "$TGEN/crocotools_param_tpxo7.py"
    cp tpxo10_params.py "$TGEN/crocotools_param_tpxo10.py"

    python seaforward.py make_tides ... --param_file crocotools_param_tpxo10.py
```
