You now have a child grid and a child IC. This step puts every file where CROCO
expects to find it — and the naming is the thing people get wrong.

### 4a — The `.1` convention

CROCO's AGRIF runtime identifies a child's files by a **`.1` suffix**, not a `1_`
prefix.

You don't have to take this on faith — **the build told you**. Look at what jobcomp
left in the run directory after compiling with AGRIF:

```bash
ls ~/seaforward/forecast/scratch/IGOG_AGRIF/
```
```
kRGB61.txt            kRGB61.txt.1              <- AGRIF made a level-1 copy
namelist_pisces_cfg   namelist_pisces_cfg.1
namelist_pisces_ref   namelist_pisces_ref.1
```

AGRIF generated `.1` copies of its input files automatically. That's the convention,
stated by the code itself. croco_pytools follows it too — it wrote `croco_grd.nc.1`,
not `1_croco_grd.nc`. So does somisana (`GRID.1`, `GLORYS.2`, `croco_grd.nc.3`). And
so does the template CROCO ships at `code/croco/OCEAN/croco.in.1`.

!!! note
    If you find yourself renaming things to `1_croco_grd.nc`, stop — that's a different convention from a different code, and nothing will find your files.

### 4b — Stage the files

```bash
D=~/seaforward/forecast/scratch/IGOG_AGRIF
CGEN=$D/child_gen/CROCO_FILES

# child IC -> .1
cp $CGEN/croco_ini_MERCATOR_20260713_00.nc  $D/CROCO_FILES/croco_ini.nc.1

# parent IC + bry, from the forecast run that already made them
RUN=~/seaforward/forecast/model-runs/IGOG_12/20260713/gen_spinup/CROCO_FILES
cp $RUN/croco_ini_MERCATOR_20260713_00.nc   $D/CROCO_FILES/croco_ini.nc
cp $RUN/croco_bry_MERCATOR_20260713_00.nc   $D/CROCO_FILES/croco_bry.nc

# AGRIF_FixedGrids.in must sit in the RUN dir, not CROCO_FILES
cp $D/CROCO_FILES/AGRIF_FixedGrids.in       $D/

ls -la $D/CROCO_FILES/
```

**Which parent IC?** The forecast run left three candidates:

```
gen_spinup/CROCO_FILES/croco_ini_MERCATOR_20260713_00.nc   <- from Mercator
spinup/CROCO_FILES/croco_ini.nc                            <- same, staged
fcst/CROCO_FILES/croco_ini.nc                              <- the spin-up RESTART
```

Take the **Mercator** one. The child's IC came from Mercator at the same instant, so
using the Mercator parent IC keeps the two clocks aligned. The `fcst` restart is two
days later and would put the grids out of sync — which is exactly the failure Step 3
warns about.

### 4c — The layout you should end up with

```
scratch/IGOG_AGRIF/
├── croco                     the AGRIF-enabled executable (Step 6)
├── croco.in                  parent runtime settings
├── croco.in.1                child runtime settings          (Step 5)
├── AGRIF_FixedGrids.in       <- RUN DIR, not CROCO_FILES
├── cppdefs.h  param.h  jobcomp  config.sh
└── CROCO_FILES/
    ├── croco_grd.nc          parent grid
    ├── croco_grd.nc.1        child grid
    ├── croco_ini.nc          parent IC       ┐ same instant,
    ├── croco_ini.nc.1        child IC        ┘ day 9688
    ├── croco_bry.nc          parent boundaries only
    └── AGRIF_FixedGrids.in   (harmless copy; the run dir one is what's read)
```

!!! note
    Note the symmetry: **every child file is its parent's name plus `.1`** — except `croco_bry.nc`, which has no `.1` counterpart, because AGRIF *is* the child's boundary condition.

!!! warning
    ⚠️ **`AGRIF_FixedGrids.in` belongs in the run directory.** croco_pytools writes it into `croco_files_dir` (next to the grids), but CROCO reads it from where you launch the executable. Leave it only in `CROCO_FILES/` and the model will start as if there were no child at all.

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