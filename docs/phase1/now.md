``` { .text .no-copy }
~/seaforward/
├── README.md                  # project overview
├── env.sh                     # sourced each session (paths + compilers + NetCDF)
├── environment.yml            # the conda environment definition
├── install/                   # 00..04 build scripts (the downloaded sources are git-ignored)
├── sftools/                   # the Python CLI + SEA-FORWARD's croco_pytools
├── docs/                      # the step-by-step guides
├── code/                      # obtained by install/04 — git-ignored
│   ├── croco/                 # CROCO model source
│   └── croco_pytools/         # pre-processing toolbox (Fortran helpers compiled)
├── opt_seq/                   # NetCDF/HDF5 stack (built from source — git-ignored)
├── data/DATASETS_CROCOTOOLS/  # bathymetry + coastline (downloaded — git-ignored)
├── forecast/                  # the forecast track: configs/, scratch/, model-runs/, driver
└── hindcast/                  # the hindcast track: configs/, scratch/, model-runs/, driver
```



!!! note
    **Next:** [Phase 2](../phase2/02_forecast_config.md) — *Building a Forecast Config*, where you build a region's grid, decide its open boundaries, and prepare the ocean and atmosphere data. Those steps are identical for forecasts and hindcasts, which is why they're a document of their own.

---

*Something not working? [Troubleshooting](trouble.md) collects the errors this phase throws, and what fixes them.*
