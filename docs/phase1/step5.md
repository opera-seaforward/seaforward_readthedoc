This installs every Python library the tools need (xarray, copernicusmarine for
Mercator downloads, cfgrib for GFS, netCDF4, numpy, scipy, and the CROCO
pre-processing dependencies).

!!! note
    **Create once, activate every time.**
    ```bash 
    conda env create
    ```
    below builds the environment **one time**. After that you never run it again — each session you only 
    ```bash 
    conda activate seaforward
    ```
    to step into it. (If you ever need to start over, 
    ```bash 
    conda env remove -n seaforward
    ```
    then create it again.)

```bash
cd ~/seaforward
conda env create -f environment.yml
```

This downloads and solves the packages — it takes a few minutes. When it
finishes, activate it:

```bash
conda activate seaforward
python -c "import xarray, copernicusmarine, netCDF4, numpy, scipy; print('seaforward env OK')"
```

You should see `seaforward env OK`. Your prompt now shows `(seaforward)`.

!!! note
    **Why a named environment?** Keeping everything in an environment called `seaforward` means you can always return to a known-good set of libraries with 
    ```bash 
    conda activate seaforward
    ```
    and you never pollute your system Python.