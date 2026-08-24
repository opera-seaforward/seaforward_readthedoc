Copy the templates into the hindcast config folder (Phase 2 Step 7), then edit
the four files **by hand in `nano`**. Only the GFS differences are spelled out
here; everything else is exactly Phase 2.

```bash
cd ${CONFIG_DIR}
cp ${CROCO_MODEL_DIR}/OCEAN/{cppdefs.h,param.h,croco.in,jobcomp} .
for f in cppdefs.h param.h croco.in jobcomp; do cp $f $f.orig; done
```

!!! note
    **nano reminders** (same as Phase 2): `Ctrl-W` = search (type text, Enter, it jumps there), edit with arrow keys, `Ctrl-O` then Enter = save, `Ctrl-X` = exit.

### 8.1 `cppdefs.h` — config name, boundaries, and **GFS forcing**

```bash
nano cppdefs.h
```

**Edit 1 — config name.** `Ctrl-W`, type `BENGUELA_LR`, Enter. Change the name on
that line to `CANARY_12`. (Search again with `Ctrl-W` `BENGUELA_LR` for a second
occurrence and change it too, if present.)

- **What:** names your configuration. **Why:** `param.h`, `croco.in`, and jobcomp all key off this name.

**Edit 2 — ONLINE + GFS.** `Ctrl-W`, type `undef  ONLINE`, Enter — this lands in
**your** regional block (the one just below the `BULK_*` lines). Set the block to:
```
#  define ONLINE
#  ifdef ONLINE
#   undef  AROME
#   define ERA_ECMWF
#  endif
```
- **What:** turns on online forcing and selects the **GFS (ECMWF)** format.
  **Why different from forecast:** the forecast used GFS (`ERA_ECMWF` undef); the
  hindcast uses GFS (`ERA_ECMWF` **define**).

**Edit 3 — close the east boundary.** `Ctrl-W`, type `define OBC_EAST`, Enter.
Change `define` to `undef  ` on that line:
```
# undef  OBC_EAST
```
- **What:** closes the eastern boundary (the African coast). **Why:** same Canary
  boundary choice as the forecast — open south/west/north, closed east.

Save: `Ctrl-O`, Enter. Exit: `Ctrl-X`.

!!! check
    ✅ **Verify:**
    ```bash
    grep -nE "define +CANARY_12|define +ONLINE|define +ERA_ECMWF|undef +AROME|OBC_EAST|OBC_WEST|OBC_NORTH|OBC_SOUTH" cppdefs.h
    ```
Want: `CANARY_12` define, `ONLINE` define, `ERA_ECMWF` define, `AROME` undef,
`OBC_EAST` undef, the other three OBC define.

!!! warning
    ⚠️ **WATCH — edit the ONLINE block in YOUR regional config section.** cppdefs.h has several `ONLINE` blocks for different example configs; make sure you edit the one near your `# define CANARY_12` (the one with the `BULK_*` settings), not another config's block. If the verify grep doesn't show `ONLINE`/`ERA_ECMWF`defined, you edited the wrong block — reopen and find the right one.

!!! note
    **Pressure (`msl`) is optional.** CROCO only reads `msl` if `READ_PATM` is defined. Leave `READ_PATM` **undef** for a basic run (you have the `msl` file; enabling it is a later refinement).

### 8.2 `param.h` — grid size (identical to forecast)

```bash
nano param.h
```

`Ctrl-W`, type `YOUR REGIONAL CONFIG`, Enter. Add your branch **above** the
`# else` line:
```
# elif defined  CANARY_12
      parameter (LLm0=79,   MMm0=121,   N=50)   ! Canary_12 hindcast
```
- **What:** sets the interior grid size. **Why these numbers:** they're
  `xi_rho−2`, `eta_rho−2` from your grid (81→79, 123→121), and `N=50` matches
  `sigma_params`.

Save `Ctrl-O` Enter, exit `Ctrl-X`. Verify:
```bash
cpp -DREGIONAL -DCANARY_12 param.h 2>/dev/null | grep "parameter (LLm0"
```

!!! check
    ✅ Expect `parameter (LLm0=79, MMm0=121, N=50)`.

### 8.3 `jobcomp` — source path (identical to forecast)

```bash
nano jobcomp
```

`Ctrl-W`, type `SOURCE1=`, Enter. Set that line to your CROCO source:
```
SOURCE1=/home/<you>/seaforward/code/croco/OCEAN
```
(replace `<you>` with your username). Save `Ctrl-O` Enter, exit `Ctrl-X`.