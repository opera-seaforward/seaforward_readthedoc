Run the three scripts **in order**:

```bash
cd ~/seaforward
bash install/01_build_hdf5.sh           # HDF5
bash install/02_build_netcdf_c.sh       # netcdf-c
bash install/03_build_netcdf_fortran.sh # netcdf-fortran
```

Each script untars its library, configures it to install into
`${SEA_FORWARD_ROOT}/opt_seq`, compiles with `-j ${NJOBS}`, and installs. The
last one prints `>>> sequential NetCDF stack complete`. **Skip to
[Verify the stack](step75.md).**

---

*Something not working? [Troubleshooting](trouble.md) collects the errors this phase throws, and what fixes them.*
