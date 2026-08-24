You need a C/Fortran compiler and a few build utilities. Install them once:

```bash
sudo apt update
sudo apt install -y build-essential gfortran m4 curl wget -c git \
                    libcurl4-openssl-dev zlib1g-dev
```

What these are:

- `build-essential` — the C compiler (`gcc`) and `make`.
- `gfortran` — the Fortran compiler (CROCO is Fortran).
- `m4`, `zlib1g-dev`, `libcurl4-openssl-dev` — needed by the NetCDF build.
- `git` — to clone the repository.

Verify:

```bash
gcc --version
gfortran --version
```

Both should print a version without error.