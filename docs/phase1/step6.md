Every working session starts by telling the shell where things live. That's what
`env.sh` does. Look at it:

```bash
cat ~/seaforward/env.sh
```

It sets **shared** paths and the compilers:

```bash
export SEA_FORWARD_ROOT=${HOME}/seaforward
export CROCO_MODEL_DIR=${SEA_FORWARD_ROOT}/code/croco
export CROCO_PYTOOLS_DIR=${SEA_FORWARD_ROOT}/code/croco_pytools
export CROCO_DATA_ROOT=${SEA_FORWARD_ROOT}/data
export SEAFORWARD=${SEA_FORWARD_ROOT}/sftools
export CC=gcc; export FC=gfortran; export F90=gfortran; export F77=gfortran
export SEA_FORWARD_PREFIX=${SEA_FORWARD_ROOT}/opt_seq
export NETCDF=${SEA_FORWARD_PREFIX}
export PATH=${SEA_FORWARD_PREFIX}/bin:${PATH}
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${SEA_FORWARD_PREFIX}/lib
```

You **source** it (run it in your current shell) at the start of each session:

```bash
source ~/seaforward/env.sh
```

It prints `SEA-FORWARD environment set (root: /home/<you>/seaforward)`.

!!! note
    **Sourcing vs running.** `source env.sh` (or `. env.sh`) applies the variables to *your* shell. Running `./env.sh` would set them only inside a throwaway sub-shell and lose them — so always `source` it.

Everything the compiler needs is already here — the compilers and the NetCDF paths —
so once you've sourced `env.sh` you can build the model.

!!! note
    **These paths point at the finished layout.** `env.sh` names where things *will* live — `code/croco`, `opt_seq`, `data/` — but you install those in [Steps 7](step7.md)–[9](step9.md) below. So right after cloning, sourcing `env.sh` is harmless but some of the folders it names are still empty. They fill in as you work through the rest of this document.