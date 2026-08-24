

```bash
cd ${SEA_FORWARD_ROOT}/install
tar -xvf netcdf-fortran-4.6.2.tar.gz
cd netcdf-fortran-4.6.2
mkdir -p build && cd build

CC=gcc FC=gfortran \
  CPPFLAGS=-I${SEA_FORWARD_ROOT}/opt_seq/include \
  LDFLAGS=-L${SEA_FORWARD_ROOT}/opt_seq/lib \
  ../configure \
    --prefix=${SEA_FORWARD_ROOT}/opt_seq \
    2>&1 | tee configure.log

make -j ${NJOBS} all 2>&1 | tee make.log
make install         2>&1 | tee install.log
```

Flags explained: again `CPPFLAGS`/`LDFLAGS` point at the netcdf-c you just built,
so the Fortran layer binds to it.