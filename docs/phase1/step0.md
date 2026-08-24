SEA-FORWARD runs the **CROCO** regional ocean model to make short ocean
forecasts. To do that, the machine needs three independent things:

1. **Python tools** (to download global data and shape it for CROCO) — provided
   by the `seaforward` conda environment.
2. **A NetCDF library** (the file format all the ocean data uses) — compiled
   from source into `~/seaforward/opt_seq`.
3. **The CROCO model itself** (Fortran code you compile into a program) — lives
   in `~/seaforward/code/croco`.

The repository ties them together with a few small scripts (`env.sh`,
`install/`, `sftools/`). This document installs all three.