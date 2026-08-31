CROCO reads and writes **NetCDF** files (the standard format for gridded
geophysical data). NetCDF is actually **three** libraries stacked on top of each
other, and we build them **in this order** because each needs the one before it:

1. **HDF5** — the low-level binary container format.
2. **netcdf-c** — the C NetCDF library, built *on top of* HDF5.
3. **netcdf-fortran** — the Fortran interface, built *on top of* netcdf-c. This
   is the one CROCO (Fortran) actually calls.

We build all three from source into **`~/seaforward/opt_seq`** ("opt" =
optional/installed software, "seq" = the **sequential**, non-MPI build). The
result is a self-contained NetCDF that lives in the repo.

!!! important
    **Why from source and not `apt install`?** Two reasons. First, the **Fortran** interface must be built with the *same* `gfortran` used to compile CROCO — a mismatched compiler causes cryptic link errors. Second, a self-contained stack in the repo means the identical build works on any machine.

!!! warning
    **A from-source stack cannot be moved.** The install path (`.../opt_seq`) is baked into the compiled binaries and libraries. If you ever relocate the repo, **rebuild** this stack in the new place — do not copy `opt_seq`.