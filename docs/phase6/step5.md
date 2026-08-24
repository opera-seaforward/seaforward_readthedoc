The child needs its own `cppdefs.h`, `param.h`, `croco.in`, `jobcomp`. Start from
the **parent's working config** and change only what differs.

```bash
cd ${CONFIG_DIR}
cp ${CROCO_CONFIGS_ROOT}/Canary_12/{cppdefs.h,param.h,croco.in,jobcomp} .
for f in cppdefs.h param.h croco.in jobcomp; do cp $f $f.orig; done
```

### 5.1 — `param.h`: the grid size

```bash
nano param.h
```
`Ctrl-W` → `CANARY_12`. Add a **new branch below** the parent's:

```
# elif defined  CANARY_12
      parameter (LLm0=79,   MMm0=121,   N=50)   ! Canary_12  81x123
# elif defined  CANARY_25
      parameter (LLm0=148,  MMm0=236,   N=75)   ! Canary_25  150x238
```

**What / Why:** the child is 150×238 (interior 148×236) with 75 levels — from
Step 1's grid and Step 2's `N`. The name `CANARY_25` must match `cppdefs.h`.

Verify: `cpp -DREGIONAL -DCANARY_25 param.h 2>/dev/null | grep "parameter (LLm0"`
→ prints `parameter (LLm0=148, MMm0=236, N=75)`.

### 5.2 — `cppdefs.h`: the config name

```bash
nano cppdefs.h
```
`Ctrl-W` → `define CANARY_12`, change to `# define CANARY_25`.

**What / Why:** just the name. **Everything else stays** — the child has the same
boundaries (E closed), same forcing (GFS `ONLINE`), same physics as the parent.
Only the identity changes.

### 5.3 — `croco.in`: timestep, sponge, files

```bash
nano croco.in
```

**Title** (`Ctrl-W` → `CANARY_12`): change to `CANARY_25 NEST`.

**S-coord** (`Ctrl-W` → `S-coord`): confirm `7.0d0  2.0d0  200.0d0` (matches N=75).

**time_stepping** (`Ctrl-W` → `time_stepping:`), the line below:
```
                2880      150      60      1
```

!!! note
    **Why a smaller timestep.** The child's grid cells are ~half the parent's size. The CFL stability condition ties timestep to cell size — halve the grid, halve the timestep. Parent ran `dt=300`; child uses `dt=150`. `NTIMES=2880` gives a 5-day run (`2880 × 150 s = 432000 s`). **Too large a `dt` at 1/25° blows up.**

**boundary** (`Ctrl-W` → `boundary:`), the filename line:
```
    CROCO_FILES/croco_bry_NEST_20260712_00.nc
```

**initial** (`Ctrl-W` → `initial:`), NRREC=1 then filename:
```
          1
    CROCO_FILES/croco_ini_NEST_20260712_00.nc
```

**sponge** (`Ctrl-W` → `X_SPONGE`), the line below:
```
                    25000.            400.
```
!!! note
    **Sponge for a nested child.** The sponge damps signals near the open boundaries so they don't reflect inward. A child is forced by the parent's *sharp mesoscale* features, so the sponge matters more than for a parent forced by smooth global data. Width scales with the grid: the parent's ~50 km sponge becomes ~25 km at 1/25°. **You can experiment with `0. 0.` (off), but a nested child is more prone to boundary instability without it — start with the sponge on.**

**online** (`Ctrl-W` → `online:`), the two lines below the header:
```
           9999   1      24            9999     1
    ${SEA_FORWARD_ROOT}/seaforward/forecast/model-runs/Canary_12/<DATE>/downloaded_data/GFS/for_croco/
```
Replace `<DATE>` with the parent forecast's date tag (e.g. `20260712`). **Use the
parent's per-cycle GFS** under `model-runs/<parent>/<date>/`, *not* the copy in
`scratch/` — see the warning below.

!!! important
    **Why reuse the parent's GFS forcing.** Surface weather (wind, heat, etc.) doesn't need refining — the child covers the same box, so it reads the **same GFS forcing** the parent used. `9999 1 24 9999 1` is the dummy-date convention (24 = hourly records) with `USE_CALENDAR` off.

!!! warning
    ⚠️ **Use the PER-CYCLE GFS, not the scratch copy.** Point at `model-runs/<parent>/<date>/downloaded_data/GFS/for_croco/` — the GFS the parent's forecast actually ran with, which covers the full window. A stale `scratch/<parent>/…` copy can be shorter and will cut the child off early with `ONLINE_GET_BULK ... dataset ... missing`. (This is covered in detail in the GFS section below.)

!!! important
    **Why the atmosphere isn't converted (unlike the ocean).** You may wonder why the ocean needed the converter + make_ini/make_bry, but the atmosphere is just reused as-is. They use different mechanisms. The **ocean** is interpolated *offline*, ahead of the run, into grid-specific ini/bry files — so it had to be regridded onto the child's exact grid. The **atmosphere** uses CROCO's `ONLINE` feature, which interpolates the raw GFS onto whatever grid is running, *live, every timestep*. So CROCO regrids the same GFS onto the finer child grid automatically — no offline conversion needed. The only requirement is that the GFS box **covers** the child domain, which it does, since the child sits inside the parent (whose GFS was downloaded for the larger parent box). Note this means the child's *atmosphere* is the same resolution as the parent's (both use GFS) — nesting refines the **ocean**, not the atmosphere.

### 5.4 — `jobcomp`: source path

```bash
grep "SOURCE1=" jobcomp
```
Confirm `SOURCE1=${SEA_FORWARD_ROOT}/seaforward/code/croco/OCEAN` (same as parent). If
not, `nano jobcomp` and fix it.