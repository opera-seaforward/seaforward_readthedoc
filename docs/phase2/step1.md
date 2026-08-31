You run a helper that writes a small text file describing the grid. The config
generators live under `sftools/config`:

```bash
cd ${SEAFORWARD}/config
python3 make_grid_config.py "${CONFIG_NAME}" \
        ${LON_MIN} ${LON_MAX} ${LAT_MIN} ${LAT_MAX} ${RES} ${RES}
```

It prints where it saved the file and an estimated size, e.g.
`Config saved to: .../forecast/configs/Canary_12/grid.ini (79x121 points)`.

Now **open the file it made** and read it, so you see what a grid definition is:

```bash
nano ${CONFIG_DIR}/grid.ini
```

Look for `lon_min`, `lon_max`, `lat_min`, `lat_max`, `dlon`, `dlat` — your box
and spacing. Also notice `topo_file` and `shp_file`: they point at your
`DATASETS_CROCOTOOLS` bathymetry and coastline (via `CROCO_DATA_ROOT`), and
`croco_files_dir`, which is where the grid will be written. `Ctrl-X` to exit
(don't change anything).

!!! note
    **`topo_file` is a decision point.** It is the only place the bathymetry source is chosen. Once Step 2 has run, that choice is baked into `croco_grd.nc` — and any nested child grid you build later inherits it. If you want a different bathymetry than the default, change it here.

!!! check
    The box matches what you set, and `dlon = dlat ≈ 0.083333` (that's 1/12°). The "(79x121 points)" is only an **estimate** — the real size comes from the next step.