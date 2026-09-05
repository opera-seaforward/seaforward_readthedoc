# Route B — build by hand

Three libraries, in order, each installed into the same prefix so they find each other:

```text
HDF5  →  netcdf-c  →  netcdf-fortran
```

!!! note
    **Each step needs the one before it.** netcdf-c will not configure without HDF5 in `opt_seq`, and netcdf-fortran will build against a netcdf-c that is not there and report success. If a configure step fails with a message about a missing or misconfigured dependency, check that the previous library actually installed before troubleshooting the message itself.

A few conventions:

- We build inside a `build/` subfolder to keep the source tree clean.
- `CC=gcc FC=gfortran` forces the compilers, which must match what CROCO uses.
- `--prefix=${SEA_FORWARD_ROOT}/opt_seq` is where it installs — the same for all three,
  so they find each other.
- `make -j ${NJOBS}` compiles using the processor count you set in
  [The two ways to build](step70.md). Confirm it is still set (`echo ${NJOBS}`; if blank,
  redo the `export` there).
- `2>&1 | tee X.log` saves each step's output to a log you can inspect if something fails.

## 1. HDF5

```bash
ls /usr/include/zlib.h || echo "MISSING — sudo apt install zlib1g-dev"

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

Flags explained: `--enable-fortran` builds the Fortran HDF5 interface, needed by
netcdf-fortran; `--with-zlib=/usr` uses the system zlib from `zlib1g-dev`.

Confirm — both that the library is there and that zlib was actually found:

```bash
ls ${SEA_FORWARD_ROOT}/opt_seq/lib/libhdf5.so && echo "HDF5 installed"
grep -i "zlib" configure.log | tail -2
```

!!! check
    The grep should show zlib being found, not `no`. If it says otherwise, install `zlib1g-dev`, delete the `build/` directory — configure caches its answers — and run this step again.

## 2. netcdf-c

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

Flags explained: `CPPFLAGS`/`LDFLAGS` point at the **HDF5 you just built**, so netcdf-c
finds it; `LIBS=-ldl` links the dynamic-loading library that some configure checks need;
`--enable-hdf5` turns on the HDF5 backend; `--disable-libxml2` avoids an optional
dependency; `--enable-curl` allows reading remote datasets.

Confirm:

```bash
ls ${SEA_FORWARD_ROOT}/opt_seq/bin/nc-config \
   ${SEA_FORWARD_ROOT}/opt_seq/lib/libnetcdf.so && echo "netcdf-c installed"
```

## 3. netcdf-fortran

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

Flags explained: again `CPPFLAGS`/`LDFLAGS` point at the netcdf-c you just built, so the
Fortran layer binds to it.

## Check the whole stack

Do this before moving on. It is a few lines and it catches every way the chain can be
incomplete:

```bash
for f in libhdf5.so libnetcdf.so libnetcdff.so; do
    [ -f ${SEA_FORWARD_ROOT}/opt_seq/lib/$f ] && echo "ok      $f" || echo "MISSING $f"
done
for f in nc-config nf-config; do
    [ -x ${SEA_FORWARD_ROOT}/opt_seq/bin/$f ] && echo "ok      $f" || echo "MISSING $f"
done
${SEA_FORWARD_ROOT}/opt_seq/bin/nf-config --flibs
```

!!! check
    Five `ok` lines, and `nf-config --flibs` naming `-lnetcdff` **and** `-lnetcdf`, both under `opt_seq/lib`.

    A missing `libnetcdf.so` alongside a present `libnetcdff.so` is the specific failure this page's ordering exists to prevent: the Fortran bindings built against a netcdf-c that is not there. `jobcomp` then fails in Phase 2 with `cannot find -lnetcdf`, several chapters from the cause.