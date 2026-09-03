You now have a child grid and a child IC. This step puts every file where CROCO
expects to find it — and the naming is the thing people get wrong.

### 4a — The `.1` convention

CROCO's AGRIF runtime identifies a child's files by a **`.1` suffix**, not a `1_`
prefix. The build shows it: compiling with AGRIF leaves these in the run directory.

```bash
ls ~/seaforward/forecast/scratch/Canary_AGRIF/
```

```text
kRGB61.txt            kRGB61.txt.1              <- AGRIF made a level-1 copy
namelist_pisces_cfg   namelist_pisces_cfg.1
namelist_pisces_ref   namelist_pisces_ref.1
```

AGRIF generated those `.1` copies itself. croco_pytools follows the same convention —
it wrote `croco_grd.nc.1`, not `1_croco_grd.nc` — as does the template CROCO ships at
`code/croco/OCEAN/croco.in.1`.

!!! note
    If you find yourself renaming things to `1_croco_grd.nc`, stop — that's a different convention from a different code, and nothing will find your files.

### 4b — Stage the files

```bash
D=~/seaforward/forecast/scratch/Canary_AGRIF
CGEN=$D/child_gen/CROCO_FILES
RUN=~/seaforward/forecast/model-runs/Canary_12/20260711/gen_spinup/CROCO_FILES

# child IC -> .1
cp $CGEN/croco_ini_MERCATOR_20260711_00.nc  $D/CROCO_FILES/croco_ini.nc.1

# parent IC + bry, from the forecast run that already made them
cp $RUN/croco_ini_MERCATOR_20260711_00.nc   $D/CROCO_FILES/croco_ini.nc
cp $RUN/croco_bry_MERCATOR_20260711_00.nc   $D/CROCO_FILES/croco_bry.nc

# AGRIF_FixedGrids.in must sit in the RUN dir, not CROCO_FILES
cp $D/CROCO_FILES/AGRIF_FixedGrids.in       $D/

ls -la $D/CROCO_FILES/ $D/
```

**Which parent IC?** The forecast run left more than one candidate:

```text
gen_spinup/CROCO_FILES/croco_ini_MERCATOR_20260711_00.nc   <- from Mercator
spinup/CROCO_FILES/croco_ini.nc                            <- same, staged
fcst/CROCO_FILES/croco_ini.nc                              <- the spin-up RESTART
```

Take the **Mercator** one. The child's IC came from Mercator at the same instant, so
using the Mercator parent IC keeps the two clocks aligned. The `fcst` restart is two
days later and would put the grids out of sync — exactly the failure Step 3 warns
about.

Note the short names on the left of each `cp`. The files arrive with the dated Mercator
name; staging them as `croco_ini.nc` and `croco_ini.nc.1` is what lets Step 5's
`croco.in` and `croco.in.1` refer to them cleanly.

### 4c — The layout you should end up with

```text
scratch/Canary_AGRIF/
├── croco                     the AGRIF-enabled executable (Step 6)
├── croco.in                  parent runtime settings
├── croco.in.1                child runtime settings          (Step 5)
├── AGRIF_FixedGrids.in       <- RUN DIR, not CROCO_FILES
├── cppdefs.h  param.h  jobcomp
└── CROCO_FILES/
    ├── croco_grd.nc          parent grid
    ├── croco_grd.nc.1        child grid
    ├── croco_ini.nc          parent IC       ┐ same instant,
    ├── croco_ini.nc.1        child IC        ┘ day 9686
    ├── croco_bry.nc          parent boundaries only
    └── AGRIF_FixedGrids.in   (harmless copy; the run dir one is what's read)
```

Note the symmetry: **every child file is its parent's name plus `.1`** — except
`croco_bry.nc`, which has no `.1` counterpart, because AGRIF *is* the child's boundary
condition.

!!! warning
    **`AGRIF_FixedGrids.in` belongs in the run directory.** croco_pytools writes it into `croco_files_dir`, next to the grids, but CROCO reads it from where you launch the executable. Leave it only in `CROCO_FILES/` and the model starts as if there were no child at all.

### 4d — What each file does

| File | Read by | Purpose |
|---|---|---|
| `AGRIF_FixedGrids.in` | AGRIF, at startup | defines the child: which parent cells, what refinement |
| `croco.in` | parent grid | its timestep, dates, output, forcing paths |
| `croco.in.1` | child grid | same, with `.1` filenames and its own `dt` |
| `croco_grd.nc[.1]` | each grid | bathymetry, mask, metrics |
| `croco_ini.nc[.1]` | each grid | starting state |
| `croco_bry.nc` | parent only | Mercator boundaries for the outer domain |

The parent still needs its own boundary conditions from Mercator — AGRIF only supplies
the **child's**. The outermost grid always talks to the outside world the normal way.