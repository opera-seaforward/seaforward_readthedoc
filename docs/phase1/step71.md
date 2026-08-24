Either way, you need the source code. Put the tarballs in
`${SEA_FORWARD_ROOT}/install`:

```bash
mkdir -p ${SEA_FORWARD_ROOT}/install
cd ${SEA_FORWARD_ROOT}/install

wget -c https://support.hdfgroup.org/releases/hdf5/v1_14/v1_14_6/downloads/hdf5-1.14.6.tar.gz
wget -c https://downloads.unidata.ucar.edu/netcdf-c/4.10.0/netcdf-c-4.10.0.tar.gz
wget -c https://downloads.unidata.ucar.edu/netcdf-fortran/4.6.2/netcdf-fortran-4.6.2.tar.gz

# Optional — only if you later build the PARALLEL (MPI) stack; the sequential
# build in this guide does NOT use it:
# wget -c https://download.open-mpi.org/release/open-mpi/v4.1/openmpi-4.1.8.tar.gz
```

!!! important
    `install/00_download_libraries.sh` does exactly these `wget -c`s if you prefer to run the script. **MPI/OpenMPI is not needed** for the sequential stack; it's only for a parallel build (see `install/notes/README_parallel.md`).

You should now have the three `.tar.gz` files:

```bash
ls -1 ${SEA_FORWARD_ROOT}/install/*.tar.gz
```