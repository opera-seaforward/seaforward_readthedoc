Whichever route you took:

```bash
source ~/seaforward/env.sh
which nf-config
nf-config --prefix
```

**Both must point inside the repo:**

```
/home/<you>/seaforward/opt_seq/bin/nf-config
/home/<you>/seaforward/opt_seq
```

`nf-config` is the small program CROCO's build uses to discover NetCDF (its
compiler flags and library paths). If `--prefix` shows `~/seaforward/opt_seq`,
the model will link correctly. (If it shows a conda or system path, a different
NetCDF is ahead on your `PATH` — re-`source ~/seaforward/env.sh`, and for
compiling later also `conda deactivate`.)

You can see the exact flags CROCO will use:

```bash
nf-config --all          # includes  --flibs  and  --includedir  that jobcomp reads
```

Confirm the Fortran library file exists:

```bash
ls ~/seaforward/opt_seq/lib/libnetcdff.so && echo "NetCDF-Fortran present"
```

!!! note
    **Naming note.** Upstream CROCO documentation often installs into a folder called `opt`. SEA-FORWARD names it **`opt_seq`** to make explicit that this is the *sequential* build (a future *parallel*/MPI build would live in a separate `opt_mpi`). `env.sh` points `SEA_FORWARD_PREFIX` at `opt_seq`, so everything downstream finds it.