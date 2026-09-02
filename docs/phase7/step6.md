Same as Phase 2 Step 10. Stage the config into the run folder and build:

```bash
cd ${FCAST}
cp ${CONFIG_DIR}/{cppdefs.h,param.h,croco.in,jobcomp} .
conda deactivate
source ~/seaforward/env.sh
which nf-config          # must show opt_seq, not conda
./jobcomp 2>&1 | tee compile.log | tail -40
```

!!! check
    The CROCO logo and **`CROCO is OK`**, and a `croco` executable appears.

!!! warning
    **Compile outside conda.** As in Phase 2, `conda deactivate` first so the linker uses `opt_seq`'s NetCDF rather than conda's — otherwise the build fails with a confusing `libcurl` error.