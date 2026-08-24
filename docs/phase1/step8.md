Two pieces of "the model side" go under `~/seaforward/code/`:

- **`code/croco`** — the CROCO ocean model source (Fortran).
- **`code/croco_pytools`** — the pre-processing toolbox (builds grids, initial
  and boundary conditions).

!!! note
    **Clean names, no versions.** The folders are named exactly `croco` and `croco_pytools` — no version suffix. The version you downloaded is recorded in `install/04_get_croco.sh`; the folder names stay clean so nothing else in the project has to know the version.

The script **`install/04_get_croco.sh` does all of this for you** — it downloads
both, extracts them, renames to the clean names, and compiles the croco_pytools
Fortran tools [Route A](routeA.md). If you'd rather do it by hand [Route B](routeB.md), here are the
exact steps it runs — download the two tarballs, extract, and **rename to the
clean names**:

```bash
cd ~/seaforward/code

# 1. CROCO ocean model (Fortran) — v2.1.3
wget -c https://gitlab.inria.fr/croco-ocean/croco/-/archive/v2.1.3/croco-v2.1.3.tar.gz
tar -xzf croco-v2.1.3.tar.gz
mv croco-v2.1.3 croco
rm croco-v2.1.3.tar.gz

# 2. croco_pytools pre-processing toolbox — v2.0.4
wget -c https://gitlab.inria.fr/croco-ocean/croco_pytools/-/archive/v2.0.4/croco_pytools-v2.0.4.tar.gz
tar -xzf croco_pytools-v2.0.4.tar.gz
mv croco_pytools-v2.0.4 croco_pytools
rm croco_pytools-v2.0.4.tar.gz
```

!!! check
    ✅ **CHECK** — both folders exist with the clean names:
    ```bash
    ls -d ~/seaforward/code/croco ~/seaforward/code/croco_pytools && echo "both present"
    ```

!!! note
    **Clean names, no versions.** The folders are named exactly `croco` and `croco_pytools` — the version you downloaded (v2.1.3 / v2.0.4) is recorded in `install/04_get_croco.sh`; the folder names stay clean so nothing else in the project has to know the version. If you download **different** versions, the `mv` targets are still `croco` and `croco_pytools`.

!!! note
    **Source note.** These tarballs come from the official CROCO GitLab (`gitlab.inria.fr/croco-ocean`). CROCO is also distributed from croco-ocean.org after accepting its licence — either source gives the same code; the GitLab archive links above are the quickest for a scripted download.

### Compile the croco_pytools Fortran helpers

croco_pytools has a small set of Fortran routines (for grid interpolation) that
must be compiled once:

```bash
conda activate seaforward
cd ~/seaforward/code/croco_pytools/prepro/Modules/tools_fort_routines/
make clean && make
```

Confirm the compiled module appeared:

```bash
ls ~/seaforward/code/croco_pytools/prepro/Modules/toolsf*.so && echo "croco_pytools tools compiled"
```

!!! note
    **Note on the pre-processing toolbox.** SEA-FORWARD ships a **vendored** copy of the exact croco_pytools modules its pre-processing code needs, inside `sftools/croco_pytools/`. The CLI uses that vendored copy, so the download and pre-processing tools work even before you install the full `code/croco_pytools`. You still install `code/croco_pytools` for grid-building.