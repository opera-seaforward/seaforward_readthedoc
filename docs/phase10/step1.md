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
TGEN=~/seaforward/forecast/scratch/Agulhas_12/tide_gen/CROCO_FILES
mkdir -p "$TGEN"
cp ~/seaforward/forecast/scratch/Agulhas_12/CROCO_FILES/croco_grd.nc "$TGEN/"

cat > "$TGEN/crocotools_param.py" << 'EOF'
inputdata       = 'tpxo7'
input_file      = 'TPXO7.nc'
input_type      = 'Re_Im'
multi_files     = False
waves_separated = False
croco_grd       = 'croco_grd.nc'
tides           = ['M2','S2','N2','K2','K1','O1','P1','Q1','Mf','Mm']
cur             = True
pot             = True
Correction_ssh  = True
Correction_uv   = True
EOF
```

**Then run it:**

```bash
cd ~/seaforward/sftools
conda activate seaforward

python seaforward.py make_tides \
    --input_dir ~/seaforward/data/DATASETS_CROCOTOOLS/TPXO7 \
    --output_dir "$TGEN" \
    --run_date "$(date -u +'%Y-%m-%d') 00:00:00" \
    --Yorig 2000 \
    --fname_out croco_frc.nc
```

`--run_date` is the phase epoch — the instant the tidal phases are referenced to.

The separate gen directory is the same pattern the AGRIF child's initial condition
uses, and for the same reason: `make_tides` reads an `inputdata` value that is a TPXO
tag, which would clash with the `'mercator'` that `make_ini` and `make_bry` expect
from *their* param file.

It works through the waves one at a time, printing each:

``` { .text .no-copy }
-----------------------
 Processing *Mm* wave
-----------------------
  tides Mm is in the list
  Period of the wave Mm is 661.309208
  Processing tidal elevation
  Processing tidal currents
  Processing equilibrium tidal potential
```

Three blocks per wave, because `cur=True` and `pot=True` in the param file. Ten waves,
so thirty blocks.

**Check what came out:**

```bash
python3 << PY
import xarray as xr, numpy as np
d = xr.open_dataset("${TGEN}/croco_frc.nc", decode_times=False)
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