Either way, you need the source code. Put the tarballs in
`${SEA_FORWARD_ROOT}/install`:

```bash
mkdir -p ${SEA_FORWARD_ROOT}/install
cd ${SEA_FORWARD_ROOT}/install

wget -c https://support.hdfgroup.org/releases/hdf5/v1_14/v1_14_6/downloads/hdf5-1.14.6.tar.gz
wget -c https://downloads.unidata.ucar.edu/netcdf-c/4.10.0/netcdf-c-4.10.0.tar.gz
wget -c https://downloads.unidata.ucar.edu/netcdf-fortran/4.6.2/netcdf-fortran-4.6.2.tar.gz

```

!!! important
    `install/00_download_libraries.sh` does exactly these `wget -c`s if you prefer to run the script.

You should now have the three `.tar.gz` files:

```bash
ls -1 ${SEA_FORWARD_ROOT}/install/*.tar.gz
```

---

*Something not working? [Troubleshooting](trouble.md) collects the errors this phase throws, and what fixes them.*
