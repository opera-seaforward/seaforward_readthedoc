Copy the templates into the hindcast config folder (Phase 2 Step 6), then edit the
four files **by hand in `nano`**. Only the differences from the forecast are spelled
out here; everything else is exactly Phase 2.

```bash
cd ${CONFIG_DIR}
cp ${CROCO_MODEL_DIR}/OCEAN/{cppdefs.h,param.h,croco.in,jobcomp} .
```

!!! note
    **nano reminders** (same as Phase 2): `Ctrl-W` = search (type text, Enter, it jumps there), edit with arrow keys, `Ctrl-O` then Enter = save, `Ctrl-X` = exit.

### 8.1 `cppdefs.h` — config name, boundaries, and **ERA5 forcing**

```bash
nano cppdefs.h
```

**Edit 1 — config name.** `Ctrl-W`, type `BENGUELA_LR`, Enter. Change the name on
that line to `CANARY_12`.

- **What:** names your configuration. **Why:** `param.h`, `croco.in` and `jobcomp`
  all key off this name.

**Edit 2 — ONLINE + ERA5.** `Ctrl-W`, type `undef  ONLINE`, Enter — this lands in
**your** regional block, just below the `BULK_*` lines. Set it to:

```
#  define ONLINE
#  ifdef ONLINE
#   undef  AROME
#   define ERA_ECMWF
#  endif
```

- **What:** turns on online forcing and selects the **ERA5 (ECMWF)** file format.
  **Why different from the forecast:** the forecast reads GFS, which is the default
  format, so it leaves `ERA_ECMWF` undef. The hindcast reads ERA5, so it must be
  **defined**. This is a compile-time switch, which means a hindcast binary and a
  forecast binary are different builds.

**Edit 3 — close the east boundary.** Don't search for `OBC_EAST` — there are four
blocks in the file and `Ctrl-W` lands on the first. Save and exit nano, then find
yours:

```bash
grep -nE "define CANARY_12|^# *(define|undef) +OBC_(EAST|WEST|NORTH|SOUTH)" cppdefs.h | head
```

The block just below your config name is the one to edit. Reopen there — `nano +N`
puts the cursor on line N — and set:

```
# undef  OBC_EAST
```

- **What:** closes the eastern boundary (the African coast). **Why:** the same
  boundary choice as the forecast — open south, west and north, closed east.

Save: `Ctrl-O`, Enter. Exit: `Ctrl-X`.

!!! check
    ```bash
    grep -nE "define +CANARY_12|define +ONLINE|define +ERA_ECMWF|undef +AROME|^# *(define|undef)+OBC_" cppdefs.h
    ```

    You want `CANARY_12` define, `ONLINE` define, `ERA_ECMWF` define, `AROME` undef, `OBC_EAST` undef and the other three OBC define — **and the OBC lines must be the ones immediately below your `CANARY_12` line**, not matches further down.

!!! note
    **Pressure (`msl`) is optional.** CROCO only reads `msl` if `READ_PATM` is defined. Leave it **undef** for a basic run; you have the file, and enabling it is a later refinement.

### 8.2 `param.h` — grid size (identical to forecast)

```bash
nano param.h
```

`Ctrl-W`, type `YOUR REGIONAL CONFIG`, Enter. Add your branch **above** the `# else`
line:

```
# elif defined  CANARY_12
      parameter (LLm0=79,   MMm0=121,   N=50)   ! Canary_12 hindcast
```

- **What:** sets the interior grid size. **Why these numbers:** they are `xi_rho−2`
  and `eta_rho−2` from your grid (81→79, 123→121), and `N=50` matches `sigma_params`.

Save `Ctrl-O` Enter, exit `Ctrl-X`. Verify:

```bash
cpp -DREGIONAL -DCANARY_12 param.h 2>/dev/null | grep "parameter (LLm0"
```

!!! check
    Expect `parameter (LLm0=79, MMm0=121, N=50)`.

### 8.3 `jobcomp` — source path (identical to forecast)

```bash
nano jobcomp
```

`Ctrl-W`, type `SOURCE1=`, Enter. Set that line to your CROCO source:

```
SOURCE1=/home/<you>/seaforward/code/croco/OCEAN
```

Replace `<you>` with your username. Save `Ctrl-O` Enter, exit `Ctrl-X`.