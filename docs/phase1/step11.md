Everything above was **one-time setup**. You will not repeat it. From here on,
each time you open a terminal to work with SEA-FORWARD, you run just these three
lines:

```bash
source ~/seaforward/env.sh                 # shared paths + compilers + NetCDF
source ~/seaforward/forecast/track.sh      # OR hindcast/track.sh — pick the track
conda activate seaforward                  # step into the Python environment
```

That's it — no re-installing, no re-building. To **compile** the model you
additionally `conda deactivate` first (so the system linker uses `opt_seq`'s
NetCDF, not conda's), then run `./jobcomp`.

| Task | When |
|------|------|
| Install Miniconda ([step 1](step1.md)) | once per machine |
| Create `seaforward` env ([step 5](step5.md)) | once per machine |
| Build `opt_seq` NetCDF stack ([step 7](step7.md)) | once per machine |
| Install CROCO + croco_pytools ([step 8](step8.md)) | once per machine |
| Download bathymetry data ([step 9](step9.md)) | once per machine |
| **`source env.sh` + `track.sh` + `conda activate`** | **every session** |