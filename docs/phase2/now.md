For your region you have a compiled model that has **run to completion**, with all
its inputs and outputs in the run folder:

```
forecast/scratch/Canary_12/
├── croco                       # the compiled program
├── cppdefs.h param.h croco.in jobcomp   # your edited config (also in configs/Canary_12)
├── compile.log
├── run.log                     # the proof it ran to MAIN: DONE
├── CROCO_FILES/
│   ├── croco_grd.nc            # grid + land mask
│   ├── crocotools_param.py     # pre-processing parameters
│   ├── croco_ini_MERCATOR_*.nc # initial condition
│   ├── croco_bry_MERCATOR_*.nc # boundary conditions
│   ├── croco_his.nc            # history output (this run)
│   └── croco_avg.nc            # averages output (this run)
└── downloaded_data/            # Mercator + GFS (+ for_croco forcing)
```

**Next:** the raw output is CROCO NetCDF (`croco_his.nc`, `croco_avg.nc`), and a
restart file (`croco_rst.nc`) that can seed a subsequent run. Turning those raw
files into plots and CF-compliant products is **postprocessing**, covered in its
own chapter.