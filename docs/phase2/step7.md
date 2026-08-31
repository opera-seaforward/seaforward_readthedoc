![build progress](../img/compile.png)

*Step 7 sets the **compile-time features** — the switches baked into the binary.*

`cppdefs.h` is a list of on/off switches that decide which parts of the model get
built. Open it:

```bash
nano cppdefs.h
```

For Canary_12 you make **three** changes. Use `Ctrl-W` to find each line.

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
(GFS-style) forcing format your files are in. A hindcast defines `ERA_ECMWF`
instead (Phase 4).

### 7.3 — Close the land boundaries

Save what you have so far and leave nano: **Ctrl-O**, **Enter**, **Ctrl-X**.

Every configuration in `cppdefs.h` has its own `OBC_*` block — there are four in the
file — so this is the one edit you should not search for. Find yours first:

```bash
grep -nE "define CANARY_12|^# *(define|undef) +OBC_(EAST|WEST|NORTH|SOUTH)" cppdefs.h | head -12
```

```
72:# define CANARY_12
98:# define OBC_EAST
99:# define OBC_WEST
100:# define OBC_NORTH
101:# define OBC_SOUTH
456:# define OBC_EAST
457:# define OBC_WEST
...
```

The block you want is the one **just below your config name** — here lines 98–101.
Everything from 456 on belongs to other configurations and never compiles. These
line numbers are the same for any new region, since every config starts from the
same template.

Reopen the file with the cursor already on that line — `nano +N` jumps straight to
line N:

```bash
nano +98 cppdefs.h
```

Change the edges your mask showed as land. For Canary_12 that is the east edge only:

```
# undef  OBC_EAST
# define OBC_WEST
# define OBC_NORTH
# define OBC_SOUTH
```

**What:** makes the eastern edge a solid wall. **Why:** Step 3 showed the east edge
is land (the African coast). A region whose coast wraps two edges closes two — this
must match the `obc_dict` you wrote in Step 4.

!!! warning
    **Never search for `OBC_EAST` with `Ctrl-W`.** It lands on the first match, and there are four blocks in the file. Editing the wrong one is silent: the model still compiles, the boundaries are wrong, and a grep afterwards still looks plausible. Work from the line numbers.

Save (`Ctrl-O`, Enter) and exit (`Ctrl-X`). Then confirm your edits:

```bash
grep -nE "define CANARY_12|define ONLINE|^# *(define|undef) +OBC_(EAST|WEST|NORTH|SOUTH)|undef  TIDES|undef  USE_CALENDAR" cppdefs.h | head
```

!!! check
    `CANARY_12` and `ONLINE` are `define`d; `OBC_EAST` is `undef` and the other three `OBC_*` are `define`d — **and those four `OBC_*` lines are the ones immediately below your `CANARY_12` line**, not matches further down the file. `TIDES` and `USE_CALENDAR` are `undef` (already off in the template: we're not using tides, and calendar-off is the mode forecasts use).