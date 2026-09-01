The child needs its own `cppdefs.h`, `param.h`, `croco.in` and `jobcomp`. Start from
the **parent's working config** and change only what differs.

```bash
cd ${CONFIG_DIR}
cp ${CROCO_CONFIGS_ROOT}/Canary_12/{cppdefs.h,param.h,croco.in,jobcomp} .
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

**What / Why:** the child is 150×238 (interior 148×236) with 75 levels — from Step
1's grid and Step 2's `N`. The name `CANARY_25` must match `cppdefs.h`.

Verify:

```bash
cpp -DREGIONAL -DCANARY_25 param.h 2>/dev/null | grep "parameter (LLm0"
```

!!! check
    `parameter (LLm0=148, MMm0=236, N=75)`.

### 5.2 — `cppdefs.h`: the config name

```bash
nano cppdefs.h
```

`Ctrl-W` → `define CANARY_12`, change to `# define CANARY_25`.

**What / Why:** just the name. **Everything else stays** — the child has the same
boundaries (east closed), the same forcing (`ONLINE` reading GFS) and the same
physics as the parent. Only the identity changes.

### 5.3 — `croco.in`: timestep, sponge, files

```bash
nano croco.in
```

**Title** (`Ctrl-W` → `CANARY_12`): change to `CANARY_25 NEST`.

**S-coord** (`Ctrl-W` → `S-coord`): confirm `7.0d0  2.0d0  200.0d0`, matching `N=75`.

**time_stepping** (`Ctrl-W` → `time_stepping:`), the line below:

```
                2880      150      60      1
```

!!! note
    **Why a smaller timestep.** The child's cells are about half the parent's size, and the CFL condition ties timestep to cell size — halve the grid, halve the timestep. The parent ran `dt=300`; the child uses `dt=150`. `NTIMES=2880` gives a 5-day run (2880 × 150 s = 432000 s). Too large a `dt` at 1/25° blows up.

**boundary** (`Ctrl-W` → `boundary:`), the filename line:

```
    CROCO_FILES/croco_bry_NEST_20260712_00.nc
```

**initial** (`Ctrl-W` → `initial:`), NRREC then the filename:

```
          1
    CROCO_FILES/croco_ini_NEST_20260712_00.nc
```

**sponge** (`Ctrl-W` → `X_SPONGE`), the line below:

```
                    25000.            400.
```

!!! note
    **A nested child wants a sponge, unlike the parent.** Phase 2 turned it off — a parent forced by a global product at the same resolution has little boundary mismatch to absorb. A child is different: it is forced by the parent's **sharp mesoscale** features, which arrive at the boundary with structure the child must accommodate, so reflection is a real risk. Width scales with the grid — the usual 50 km becomes about 25 km at 1/25°. Start with it on; turn it off only if you have checked the boundaries stay quiet without it.

**online** (`Ctrl-W` → `online:`), the two lines below the header:

```
           9999   1      24            9999     1
    ${SEA_FORWARD_ROOT}/forecast/model-runs/Canary_12/<DATE>/downloaded_data/GFS/for_croco/
```

Replace `<DATE>` with the parent forecast's folder name — `20260712`, or
`20260712_plain` for a run made by the current driver.

!!! warning
    **Use the parent's per-cycle GFS, not the scratch copy.** Point at `model-runs/<parent>/<date>/downloaded_data/GFS/for_croco/` — the forcing the parent's forecast actually ran with, which covers the full window. A stale `scratch/<parent>/…` copy can be shorter and will cut the child off early with `ONLINE_GET_BULK ... dataset ... missing`.

**Why the atmosphere isn't converted, when the ocean was.** The two use different
mechanisms. The **ocean** is interpolated *offline*, ahead of the run, into
grid-specific ini and bry files — so it had to be regridded onto the child's exact
grid. The **atmosphere** uses CROCO's `ONLINE` feature, which interpolates the raw
GFS onto whatever grid is running, live, every timestep. CROCO therefore regrids the
same GFS onto the finer child grid automatically. The only requirement is that the
GFS box covers the child domain, which it does, since the child sits inside the
parent whose GFS was downloaded for the larger box.

One consequence worth noticing: the child's *atmosphere* is at the same resolution as
the parent's. Nesting refines the **ocean**, not the weather driving it.

### 5.4 — `jobcomp`: source path

```bash
grep "SOURCE1=" jobcomp
```

It should read `SOURCE1=${SEA_FORWARD_ROOT}/code/croco/OCEAN`, the same as the
parent's. If not, `nano jobcomp` and fix it.