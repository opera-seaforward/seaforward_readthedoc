The tide generator ships inside croco_pytools as `make_tides.py`, and there is a
wrapped, parameter-file-driven version in `sftools/preprocess.py`:
`make_tides(input_dir, output_dir, run_ini_date, Yorig, fname_out)`. It reads the
grid and a set of options from a `crocotools_param.py` in the output directory,
loops the requested waves, interpolates each onto the model grid, and writes
`croco_frc.nc`.

It was not exposed on the `seaforward.py` command line, so we added it — a
subcommand mirroring `make_ini`/`make_bry`:

```bash
python seaforward.py make_tides \
    --input_dir  <TPXO dir> \
    --output_dir <gen dir with crocotools_param.py + croco_grd.nc> \
    --run_date   "YYYY-MM-DD 00:00:00" \
    --Yorig      2000 \
    --fname_out  croco_frc.nc
```

`--run_date` is the phase epoch. `--output_dir` is a gen directory holding the
grid and a tide-specific `crocotools_param.py` — the same pattern the child IC
uses, and for the same reason: `make_tides`'s `inputdata` value is a TPXO tag,
which would clash with the `'mercator'` value that `make_ini`/`make_bry` read
from *their* param file. Keeping the tide params in their own directory avoids
the collision entirely.

The process described above is summarized by the figure below.
<figure style="text-align: center; margin: 20px 0;">
  <img src="../../img/tides_U4.png" alt="Workflow combining CROCO_tools/TPXO10 Atlas tidal data with model_grid.nc" style="max-width: 100%; height: auto;">
  <figcaption style="font-size: 0.9em; color: #555; margin-top: 8px; font-style: italic;">
    Workflow combining CROCO_tools/TPXO10 Atlas tidal data with <code>model_grid.nc</code>, processed by SEA_FORWARD pytools (using <code>-run-date</code>, <code>-reference-date</code>, <code>crocotools_param_tides.py</code>) to produce the <code>tides-upstr-input</code> file, linked downstream to C1, V1, and D1.
  </figcaption>
</figure>