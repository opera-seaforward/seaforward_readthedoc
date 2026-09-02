The tide generator ships inside croco_pytools as `make_tides.py`, and there is a
wrapped, parameter-file-driven version in `sftools/preprocess.py`:
`make_tides(input_dir, output_dir, run_ini_date, Yorig, fname_out)`. It reads the grid
and a set of options from a `crocotools_param.py` in the output directory, loops the
requested waves, interpolates each onto the model grid, and writes `croco_frc.nc`.

It was not exposed on the `seaforward.py` command line, so we added it — a subcommand
mirroring `make_ini` and `make_bry`:

```bash
python seaforward.py make_tides \
    --input_dir  <TPXO dir> \
    --output_dir <gen dir with crocotools_param.py + croco_grd.nc> \
    --run_date   "YYYY-MM-DD 00:00:00" \
    --Yorig      2000 \
    --fname_out  croco_frc.nc
```

`--run_date` is the phase epoch. `--output_dir` is a gen directory holding the grid and
a tide-specific `crocotools_param.py` — the same pattern the AGRIF child's initial
condition uses, and for the same reason: `make_tides` reads an `inputdata` value that
is a TPXO tag, which would clash with the `'mercator'` that `make_ini` and `make_bry`
expect from *their* param file. Keeping the tide params in their own directory avoids
the collision entirely.

<figure style="text-align: center; margin: 20px 0;">
  <img src="../../img/tides_U4.png" alt="TPXO atlas and the model grid combined into a per-cycle tide file" style="max-width: 100%; height: auto;">
  <figcaption style="font-size: 1em; color: #555; margin-top: 8px; font-style: italic;">
    TPXO10 atlas data and the model grid, processed with a run date and a reference
    date, produce the per-cycle tide file.
  </figcaption>
</figure>