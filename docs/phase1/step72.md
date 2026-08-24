```bash
cd ${SEA_FORWARD_ROOT}/install
tar -xvf hdf5-1.14.6.tar.gz
cd hdf5-1.14.6
mkdir -p build && cd build

CC=gcc FC=gfortran ../configure \
    --prefix=${SEA_FORWARD_ROOT}/opt_seq \
    --enable-fortran \
    --with-zlib=/usr \
    2>&1 | tee configure.log

make -j ${NJOBS} all 2>&1 | tee make.log
make install         2>&1 | tee install.log
```

Flags explained: `--enable-fortran` builds the Fortran HDF5 interface (needed by
netcdf-fortran); `--with-zlib=/usr` uses the system zlib (from `zlib1g-dev`).

Confirm:

```bash
ls ${SEA_FORWARD_ROOT}/opt_seq/lib/libhdf5.so && echo "HDF5 installed"
```