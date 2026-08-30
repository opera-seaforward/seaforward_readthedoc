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
    The CROCO logo and **`CROCO is OK`**, and a `croco` executable.

!!! warning
    **Compile outside conda.** As in Phase 2, `conda deactivate` first so the linker uses `opt_seq` NetCDF, not conda's — this avoids the `libcurl` error.

## A note on spin-up (why the first day looks like the parent)

The child starts from an **interpolated** initial condition — the parent's state,
smoothed onto the finer 1/25° grid. That interpolation cannot contain the
fine-scale structure the child grid is *capable* of resolving: at T0 the child's
ocean is essentially a parent-resolution field sitting on a fine grid.

The child then has to **grow its own fine-scale dynamics** — the sharper fronts,
smaller eddies and filaments that 1/25° can resolve but the smooth initial
condition doesn't contain. These develop over roughly the **first day** of the run.

!!! note
    **The first ~day of a nested run is spin-up.** During it, the child's output still looks much like the parent — the resolution benefit hasn't emerged yet. By day 2–3 the fine-scale structure has developed and the child genuinely resolves more than the parent.

This is worth *watching*: plot the child's SST or surface vorticity on day 1, day 2
and day 3 and you'll see the filaments and eddies sharpen and multiply as the fine
grid spins up its own dynamics. The spin-up isn't a nuisance — it's the resolution
benefit appearing.

**Practical consequences:**

- When you **validate** the child against the parent (next), compare on **day 3–5**,
  not day 1 — day 1 is spin-up and will still look parent-like, understating the
  benefit.
- For a **real forecast** (not a teaching run), give the child a proper spin-up the
  way the parent has one: start it 2 days before T0 (`hdays=2`) so the fine structure
  is already developed when the forecast window begins. That requires the parent
  output to cover those 2 extra days. For this manual example we keep it simple — run
  from T0 and treat the first day as visible spin-up.

## Use the parent's per-cycle GFS

The child has no spin-up, so it reuses the **parent's GFS forcing**. The subtlety —
and a real trap — is *which* GFS folder to point at.

The operational forecast keeps **two** GFS copies:

- a **per-cycle** copy the forecast actually ran with, under its run folder:
  `model-runs/<parent>/<date>/downloaded_data/GFS/for_croco/`
- an older staging copy in **scratch**:
  `scratch/<parent>/downloaded_data/GFS/for_croco/`

**These can cover different time windows.** The per-cycle copy spans the parent's
full forecast window; a stale scratch copy may be shorter. If the child points at a
shorter GFS than the parent used, it runs fine until it reaches the end of that GFS,
then looks for the next month's file — which was never made — and stops:

```
ONLINE_GET_BULK - ERROR: The dataset for the year 9999 month 2 is missing
```

This is *not* a model failure — everything written up to that point is valid. The
forcing simply ran out early, because the child was reading a shorter GFS folder than
the parent's forecast used.

!!! warning
    **Point the child at the parent's per-cycle GFS, not the scratch copy.** Use `model-runs/<parent>/<date>/downloaded_data/GFS/for_croco/` — the folder the parent's forecast actually ran with, which covers the full window. The operational driver below uses the per-cycle folder only and fails clearly if it's missing: deliberately no fallback to scratch, so it can never silently read the wrong forcing.

To check a GFS folder's coverage:

```python
import xarray as xr, glob

GFS_DIR = "forecast/model-runs/Canary_12/<date>/downloaded_data/GFS/for_croco"

fs = sorted(glob.glob(GFS_DIR + "/*.nc"))
g  = xr.open_dataset(fs[0], decode_times=False)
tv = [v for v in ("bulk_time", "time", "tair_time") if v in g.variables][0]
t  = g[tv].values
print(f"GFS covers {t.min():.2f} .. {t.max():.2f} days")   # must span the child's window
```

The child runs over the **same forecast window as the parent** — today's window. Its
date is simply today (`date -u +%Y%m%d`), the same as the forecast driver. Given the
correct per-cycle GFS, the forcing is available across the window.

!!! note
    **Why the child runs 4 days, not the parent's full 5.** The parent's ocean output — which becomes the child's boundary file — and its GFS both span *exactly* `[today, today+5]`. A limited-area model can't integrate to the very last instant of its forcing: to advance the final step *to* `today+5` it needs a record *beyond* `today+5`, and there isn't one. Pushing to the exact end gives `ERROR in get_bry: cannot read variable 'bry_time'` a few hours short of the nominal end. So the child runs **`FDAYS=4`** — comfortably inside the parent's window, with boundary and GFS runway ahead the whole way, finishing cleanly at `MAIN: DONE`. To get a full 5-day child you would have to run the parent 6 days; usually not worth it.