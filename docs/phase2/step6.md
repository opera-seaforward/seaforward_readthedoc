You start from CROCO's blank templates. Copy the four you will edit into your
config folder. The originals stay in `${CROCO_MODEL_DIR}/OCEAN/`, so you can always
re-copy one if an edit goes wrong.

```bash
cd ${CONFIG_DIR}
cp ${CROCO_MODEL_DIR}/OCEAN/cppdefs.h .
cp ${CROCO_MODEL_DIR}/OCEAN/param.h .
cp ${CROCO_MODEL_DIR}/OCEAN/croco.in .
cp ${CROCO_MODEL_DIR}/OCEAN/jobcomp .
```

These four files are all you need. The compilers and the `opt_seq` NetCDF paths
already came from `env.sh` in Step 0, so nothing else has to be sourced before
compiling.

You edit each of them over the next steps — `cppdefs.h`, `param.h` and `jobcomp`
before compiling, then `croco.in` for the run.