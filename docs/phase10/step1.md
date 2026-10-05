The tide generator ships inside croco_pytools as `make_tides.py`, and there is a
wrapped, parameter-file-driven version in `sftools/preprocess.py`:
`make_tides(input_dir, output_dir, run_ini_date, Yorig, fname_out)`. It reads the grid
and a set of options from a `crocotools_param.py` in the output directory, loops the
requested waves, interpolates each onto the model grid, and writes `croco_frc.nc`.

It was not exposed on the `seaforward.py` command line, so we added it — a subcommand
mirroring `make_ini` and `make_bry`:

``` { .text .no-copy }
python seaforward.py make_tides \
    --input_dir  <TPXO dir> \
    --output_dir <gen dir with crocotools_param.py + croco_grd.nc> \
    --run_date   "YYYY-MM-DD 00:00:00" \
    --Yorig      2000 \
    --fname_out  croco_frc.nc
```

**Set up the generation directory first** — `make_tides` reads the grid and a
tide-specific `crocotools_param.py` from `--output_dir`, and fails without them:

```bash
TGEN=~/seaforward/forecast/scratch/Canary_12/tide_gen/CROCO_FILES
mkdir -p "$TGEN"
cp ~/seaforward/forecast/scratch/Canary_12/CROCO_FILES/croco_grd.nc "$TGEN/"

cat > "$TGEN/crocotools_param.py" << 'EOF'
inputdata       = 'tpxo7_croco'   # must be one of the tags in Readers/tides_reader.py
input_file      = 'TPXO7.nc'
input_type      = 'Re_Im'
multi_files     = False
waves_separated = False
elev_file       = ''      # required by the reader, but unused when
u_file          = ''      # multi_files = False - the single-file path
v_file          = ''      # reads input_file instead
croco_grd       = 'croco_grd.nc'
tides           = ['M2','S2','N2','K2','K1','O1','P1','Q1']
cur             = True
pot             = True
Correction_ssh  = True
Correction_uv   = True
EOF
```

!!! important
    **Two values here are not free choices.**

    `inputdata` must be a tag the reader knows — `tpxo7_croco`, `tpxo9`,
    `tpxo9_lowres` or `tpxo10`, listed in
    `croco_pytools/prepro/Readers/tides_reader.py`. Anything else, including the
    plausible-looking `'tpxo7'`, stops with *"No 'tpxo7' dico available"*. (That
    message names `Modules/tides_readers.py`, which does not exist — the file is
    `Readers/tides_reader.py`.)

    `tides` must only list waves the file actually contains. **TPXO7 carries the
    eight diurnal and semi-diurnal constituents above and no long-period ones**,
    so asking for `Mf` or `Mm` stops with *"Did not find wave Mf in input file"*
    after the first eight have already been written. The atlas products do carry
    them — see [Step 2](step2.md).

**Then run it:**

```bash
cd ~/seaforward/sftools
conda activate seaforward

python seaforward.py make_tides \
    --input_dir ~/seaforward/data/DATASETS_CROCOTOOLS/TPXO7/ \
    --output_dir "$TGEN" \
    --run_date "$(date -u +'%Y-%m-%d') 00:00:00" \
    --Yorig 2000 \
    --fname_out croco_frc.nc
```

`--run_date` is the phase epoch — the instant the tidal phases are referenced to.

The separate gen directory is the same pattern the AGRIF child's initial condition
uses, and for the same reason: `make_tides` imports its parameters from a module named
`crocotools_param`, whose `inputdata` is a TPXO tag — which would clash with the
`'mercator'` that `make_ini` and `make_bry` read from *their* `crocotools_param.py` in
`CROCO_FILES/`. Two param files cannot share a directory under that name, so the tide
one gets a directory of its own.

It works through the waves one at a time, printing each:

``` { .text .no-copy }
-----------------------
 Processing *Q1* wave
-----------------------
  tides Q1 is in the list
  Period of the wave Q1 is 26.868357
  Processing tidal elevation
  Processing tidal currents
  Processing equilibrium tidal potential
```

Three blocks per wave, because `cur=True` and `pot=True` in the param file. Eight
waves, so twenty-four blocks.

**Check what came out:**

```bash
python3 << 'PY'
import os, xarray as xr, numpy as np
d = xr.open_dataset(os.path.join(os.environ['TGEN'], 'croco_frc.nc'), decode_times=False)
print("vars:", list(d.data_vars))
print("dims:", dict(d.sizes))
m2 = d.tide_Eamp.isel(tide_period=0).values
print("M2 amp: mean %.3f m  max %.3f m" % (np.nanmean(m2), np.nanmax(m2)))
PY
```

The first tidal period is M2, the principal lunar semi-diurnal — the largest
constituent almost everywhere, so its amplitude is the quickest sanity check.

<figure style="text-align: center; margin: 20px 0;">
  <img src="../../img/tides_U4.png" alt="TPXO atlas and the model grid combined into a per-cycle tide file" style="max-width: 100%; height: auto;">
  <figcaption style="font-size: 1em; color: #555; margin-top: 8px; font-style: italic;">
    TPXO10 atlas data and the model grid, processed with a run date and a reference
    date, produce the per-cycle tide file.
  </figcaption>
</figure>
