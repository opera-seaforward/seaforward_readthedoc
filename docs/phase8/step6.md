### 6a — `cppdefs.h`

```bash
cd ~/seaforward/forecast/scratch/IGOG_AGRIF
nano cppdefs.h
```

`Ctrl+W` `AGRIF` `Enter`. **The first match is the one you want** — around line 80, in
your config's own block:

```text
# define AGRIF                <- change from "# undef  AGRIF"
# undef  AGRIF_2WAY           <- leave this as undef for now
```

!!! warning
    **Do not edit the match near line 1066.** `Ctrl+W` `Enter` again lands on it:

```text
    !                       Baroclinic Vortex Example (TEST AGRIF)
    # define AGRIF
    # undef  AGRIF_2WAY
```

    That is the VORTEX test case's block, inside a different `#elif defined`. Editing it does nothing for your config and will confuse you later.

Save: `Ctrl+O` `Enter`, `Ctrl+X`. Verify:

```bash
grep -n "AGRIF" cppdefs.h | head -2
```

```text
80:# define AGRIF
81:# undef  AGRIF_2WAY
```

**`AGRIF` on, `AGRIF_2WAY` off** — one-way, the first milestone.

### 6b — `param.h` needs no edit

This surprises people coming from offline nesting, where the child needed its own
`#elif defined` block with `LLm0` and `MMm0`. With AGRIF, add nothing:

```fortran
#ifdef AGRIF
      common /scrum_physical_grid/ LLm,Lm,LLmm2,MMm,Mm,MMmm2
#else
      parameter (LLm=LLm0,  MMm=MMm0)
#endif
```

With `AGRIF` defined, `LLm` and `MMm` stop being compile-time parameters and become
**runtime variables**, computed per grid from `AGRIF_FixedGrids.in`. `param.h` keeps
the parent's values — `LLm0=103, MMm0=139, N=50` for IGOG_12 — and the child's
dimensions are never written anywhere.

### 6c — compile

```bash
conda deactivate                    # the compiler env, not the python one
source ./config.sh
./jobcomp 2>&1 | tee compile_agrif.log | tail -5
```

!!! note
    **`config.sh` or `env.sh`?** IGOG_AGRIF ships a per-config `config.sh`; configs built the Phase 2 way don't, and use `~/seaforward/env.sh` instead. Both set the compiler and the `opt_seq` NetCDF paths. Use whichever your config directory has.

The AGRIF build is heavier than a normal one: `jobcomp` first builds the **`conv`**
preprocessor, then runs it over the whole CROCO source to generate AGRIF-aware code.
It takes noticeably longer.

Success looks like `-lagrif` in the link line, then:

```text
CROCO is OK
```

If it fails, `compile_agrif.log` has the detail — the `conv` step is the usual suspect.

### Keep the binary

Rename it before building anything else, so the two modes don't overwrite each other:

```bash
cp croco croco_1way
```

Step 8 builds `croco_2way` the same way, and the driver picks between them by name.