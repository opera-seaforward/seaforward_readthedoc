Run the three scripts **in order**:

```bash
cd ~/seaforward
bash install/01_build_hdf5.sh           # HDF5           (~3-8 min)
bash install/02_build_netcdf_c.sh       # netcdf-c       (~3-5 min)
bash install/03_build_netcdf_fortran.sh # netcdf-fortran (~2-3 min)
```

Each script untars its library, configures it to install into
`${SEA_FORWARD_ROOT}/opt_seq`, compiles with `-j ${NJOBS}`, and installs. The
last one prints `>>> sequential NetCDF stack complete`. **Skip to [7.5](step75.md) to
verify.**