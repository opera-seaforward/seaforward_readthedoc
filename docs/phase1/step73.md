```bash
cd ${SEA_FORWARD_ROOT}/install
tar -xvf netcdf-c-4.10.0.tar.gz
cd netcdf-c-4.10.0
mkdir -p build && cd build

CC=gcc FC=gfortran \
  CPPFLAGS=-I${SEA_FORWARD_ROOT}/opt_seq/include \
  LDFLAGS=-L${SEA_FORWARD_ROOT}/opt_seq/lib \
  LIBS=-ldl \
  ../configure \
    --prefix=${SEA_FORWARD_ROOT}/opt_seq \
    --enable-hdf5 \
    --disable-libxml2 \
    --enable-curl \
    2>&1 | tee configure.log

make -j ${NJOBS} all 2>&1 | tee make.log
make install         2>&1 | tee install.log
```

Flags explained: `CPPFLAGS`/`LDFLAGS` point at the **HDF5 you just built** (so
netcdf-c finds it); `LIBS=-ldl` links the dynamic-loading library that some
configure checks need; `--enable-hdf5` turns on the HDF5 backend;
`--disable-libxml2` avoids an optional dependency; `--enable-curl` allows reading
remote datasets.

Confirm:

```bash
ls ${SEA_FORWARD_ROOT}/opt_seq/bin/nc-config \
   ${SEA_FORWARD_ROOT}/opt_seq/lib/libnetcdf.so && echo "netcdf-c installed"
```