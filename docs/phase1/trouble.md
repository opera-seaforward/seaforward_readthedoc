- **`conda: command not found`** — reopen the terminal, or run
  `source ~/miniconda3/etc/profile.d/conda.sh`.
- **`nf-config --prefix` shows a conda path or a system path** — you have a
  different NetCDF ahead on `PATH`. Re-run `source ~/seaforward/env.sh`; for
  compiling, also `conda deactivate` so conda's NetCDF steps aside.
- **A library build fails on a missing header** — install the dev package it
  names (commonly `zlib1g-dev`, `libcurl4-openssl-dev`, `m4`) and re-run that
  one script.
- **You moved the repo and now compiles fail** — the from-source NetCDF stack
  has absolute paths baked in. Rebuild it (`install/01`→`03`) in the new
  location rather than copying `opt_seq`.
- **Out of memory during a build** — lower parallelism: `export NJOBS=4` (or
  `2`) and re-run the script.