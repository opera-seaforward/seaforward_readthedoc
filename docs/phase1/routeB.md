This is exactly what the scripts do, one library at a time. A few conventions:

- We build inside a `build/` subfolder to keep the source tree clean.
- `CC=gcc FC=gfortran` forces the compilers (must match what CROCO uses).
- `--prefix=${SEA_FORWARD_ROOT}/opt_seq` is **where it installs** — the same for
  all three, so they find each other.
- `make -j ${NJOBS}` compiles using the processor count you set in [7.0](step70.md). Confirm
  it's still set (`echo ${NJOBS}` — if blank, re-do the `export` in [7.0](step70.md)).
- `2>&1 | tee X.log` saves each step's output to a log you can inspect if
  something fails.

!!! warning
    ⚠️ **Dependencies for netcdf-c.** It needs `libcurl` and `m4` headers. You installed these in [step 2](step2.md) (`libcurl4-openssl-dev m4`). If a configure step complains about curl or m4, install them and re-run that library.