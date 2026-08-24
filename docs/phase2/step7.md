![build progress](../img/compile.png)

*Step 7 sets the **compile-time features** — the switches baked into the binary.*

`cppdefs.h` is a list of on/off switches that decide which parts of the model get
built. Open it:

```bash
nano cppdefs.h
```

You'll make **three** changes. Use `Ctrl-W` to find each line.

### 7.1 — Name your configuration

`Ctrl-W`, type `BENGUELA_LR`, Enter. You'll land on:

```
# define BENGUELA_LR
```

Change `BENGUELA_LR` to `CANARY_12`:

```
# define CANARY_12
```

**What:** this names your configuration. **Why:** `BENGUELA_LR` is CROCO's
built-in South-Africa example; you're replacing it with your own. Use
**UPPERCASE** (CROCO's convention), and the exact same name must appear in
`param.h` (Step 8).

### 7.2 — Turn on online weather forcing

`Ctrl-W`, type `undef  ONLINE`, Enter. You'll find:

```
#  undef  ONLINE
```

Change `undef` to `define`:

```
#  define ONLINE
```

**What:** turns on the feature that reads your GFS surface forcing. **Why:**
without it, the model wouldn't use the weather files you made in Step 5b. Just
below it, leave `AROME` and `ERA_ECMWF` as `undef` — that selects the default
(GFS-style) forcing format your files are in.

### 7.3 — Close the land boundary

`Ctrl-W`, type `define OBC_EAST`, Enter:

```
# define OBC_EAST
```

Change `define` to `undef` (and fix the spacing so it lines up):

```
# undef  OBC_EAST
```

**What:** makes the eastern edge a solid wall. **Why:** Step 3 showed the east
edge is land (the African coast), so it must be closed. Leave `OBC_WEST`,
`OBC_NORTH`, `OBC_SOUTH` as `define` — those are your open boundaries.

!!! warning
    ⚠️ **WATCH — many blocks contain `OBC_EAST`.** `Ctrl-W` may land in a different configuration's block. Make sure you're editing the one in **your REGIONAL block** (near your `# define CANARY_12`). If unsure, search again to confirm you changed the right one, and that the other three `OBC_*` there are still `define`.

!!! note
    For **your** region: close whichever edges your mask (Step 3) showed as land. This must match the `obc_dict` you wrote in Step 4.

Save (`Ctrl-O`, Enter) and exit (`Ctrl-X`). Then confirm your edits:

```bash
grep -nE "define CANARY_12|define ONLINE|OBC_EAST|OBC_WEST|OBC_NORTH|OBC_SOUTH|undef  TIDES|undef  USE_CALENDAR" cppdefs.h | head
```

!!! check
    ✅ **CHECK** — `CANARY_12` and `ONLINE` are `define`d; `OBC_EAST` is `undef`, the other three `OBC_*` are `define`d; `TIDES` and `USE_CALENDAR` are `undef` (already off in the template — good: we're not using tides, and calendar-off is the mode forecasts use).