You start from CROCO's blank templates. Copy the four you will edit into your config
folder. The originals stay in `${CROCO_MODEL_DIR}/OCEAN/`, so you can always re-copy one
if an edit goes wrong.

```bash
cd ${CONFIG_DIR}
cp ${CROCO_MODEL_DIR}/OCEAN/cppdefs.h .
cp ${CROCO_MODEL_DIR}/OCEAN/param.h .
cp ${CROCO_MODEL_DIR}/OCEAN/croco.in .
cp ${CROCO_MODEL_DIR}/OCEAN/jobcomp .
```

## What each file is

| file | what it controls |
|---|---|
| **`cppdefs.h`** | Which physics goes into the binary — your region's name, its open boundaries, and where the atmospheric forcing comes from. |
| **`param.h`** | The grid's size: points in each horizontal direction, and sigma levels in the vertical. |
| **`jobcomp`** | The build script — where the CROCO source and the NetCDF libraries are. |
| **`croco.in`** | The run itself: timestep, run length, which input files to read, how often to write output. |

The first three are read **when you compile**; `croco.in` is read **when you run**. So a
change to `cppdefs.h` or `param.h` means compiling again, while a change to `croco.in`
does not.

You edit each of them over the next steps — `cppdefs.h`, `param.h` and `jobcomp` before
compiling, then `croco.in` for the run.

The compilers and the `opt_seq` NetCDF paths already came from `env.sh` in
[Step 0](step0.md), so nothing else has to be sourced before compiling.