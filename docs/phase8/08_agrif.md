# Phase 8 — AGRIF nesting

Phase 7 built an **offline** nest: the parent runs, writes history files, and a
converter turns those into boundary conditions for a child that runs afterwards.
Information flows one way, from parent to child, filtered through hourly snapshots.

This chapter builds an **AGRIF** nest instead: parent and child run *simultaneously*,
inside a single executable, exchanging data every barotropic timestep — and, if you
enable it, the child's solution feeds **back** into the parent.

## How this chapter works

AGRIF has two modes, and we build them **in order**:

1. **One-way** (`AGRIF_2WAY` undefined) — parent and child run together, the parent
   feeds the child's boundaries every barotropic step, the child does not feed back.
   Steps 1–7 get you here.
2. **Two-way** (`AGRIF_2WAY` defined) — the child's solution is averaged back onto
   the parent where they overlap. Step 8 adds this on top.

**Always build one-way first.** Two-way can destabilise, and an
AGRIF nest has plenty of other things to get wrong before you get there — grid
alignment, file conventions, timestep bookkeeping, initial conditions. If you enable
feedback from the outset and it fails, you cannot tell which of those it was. One-way
isolates the variable. Once the nest runs cleanly one-way, switching to two-way is a
one-line change and a recompile, and any new problem is unambiguously the feedback.

The one-way run also gives you the **baseline**. Without it you have nothing to
difference the two-way result against, and no way to demonstrate the feedback did
anything at all.

## Editing conventions in this chapter

Every file you touch here is edited **by hand in nano**. The chapter gives you the
search string and the change, not a `sed` one-liner, because you should see what
you're changing — several of these files have near-identical lines in different
sections, and a blind `sed` will hit the wrong one.

The nano keys used throughout:

| Key | Does |
|---|---|
| `Ctrl+W` | **Where is** — search. Type the string, press `Enter`. |
| `Alt+W` | repeat the last search — jump to the next match |
| `Ctrl+K` | cut the current line |
| `Ctrl+U` | paste (uncut) the line |
| `Ctrl+O` then `Enter` | **write Out** — save, keeping the filename |
| `Ctrl+X` | exit (prompts to save if you haven't) |
| `Ctrl+C` | show the current line number |
| `Alt+G` | go to a line number |

So when the chapter says:

!!! note
    `nano cppdefs.h` → `Ctrl+W` `AGRIF_2WAY` `Enter` → change `# undef  AGRIF_2WAY` to `# define AGRIF_2WAY` → `Ctrl+O` `Enter` → `Ctrl+X`

that means: open the file, search for `AGRIF_2WAY`, edit the line the cursor lands
on, save, exit.

**After every edit, verify with `grep`.** The chapter shows the grep and the expected
output. This is not optional — one of the gotchas below (the child's `dt`) produces a
run that succeeds while being silently wrong, and the only defence is checking the
file says what you think it says.

!!! important
    **This chapter builds the nest by hand.** The operational driver *can* run an AGRIF nest — `run_forecast_cycle.sh --child 1way` — but it expects the child grid, its initial condition and its `croco.in.1` to exist already, and a binary compiled with `AGRIF` defined. This chapter is how you make all of those. Once they exist, the driver takes over and runs the nest every cycle.