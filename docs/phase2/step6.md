You start from CROCO's blank templates. Copy them into your **config** folder
(the recipe), and keep pristine `.orig` backups:

```bash
cd ${CONFIG_DIR}
cp ${CROCO_MODEL_DIR}/OCEAN/cppdefs.h .
cp ${CROCO_MODEL_DIR}/OCEAN/param.h .
cp ${CROCO_MODEL_DIR}/OCEAN/croco.in .
cp ${CROCO_MODEL_DIR}/OCEAN/jobcomp .
for f in cppdefs.h param.h croco.in jobcomp; do cp $f $f.orig; done
```

!!! note
    **No `config.sh` to copy.** In the new setup, the compilers and the `opt_seq` NetCDF paths are already in `env.sh` (which you sourced in Step 0). There is no per-config `config.sh` to copy or source — sourcing `env.sh` at the start of the session is enough to compile later.

You will edit each of these four files by hand over the next steps — `cppdefs.h`, `param.h`, and `jobcomp` before compiling, then `croco.in` for the run. This is the heart of understanding a CROCO configuration.