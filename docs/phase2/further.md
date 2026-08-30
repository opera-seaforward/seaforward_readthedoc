![AGRIF nest](../img/run_parent_child.png)

*An AGRIF child is a finer grid nested inside the parent. Parent and child run **together** in one execution, and the child's boundaries come from the **parent model itself**, not from the global ocean — CROCO forcing CROCO.*

What you built above is a single-grid forecast — one domain, one resolution. When
you need **high resolution over just part of the domain** — a bay, a shelf, an
island wake — rebuilding the whole thing at fine resolution is expensive and
usually unnecessary. Instead you add a **child grid**: a finer grid inside the
parent that resolves the small-scale detail only where you want it.

SEA-FORWARD offers two ways to do this. **Offline nesting** (Phase 6) runs the
parent first, then builds the child's boundaries from the parent's saved output and
runs the child afterwards. **AGRIF** (Phase 8), described here, runs both grids in
one execution with the parent feeding the child every timestep.

### The one idea to hold onto

**The parent forces the child.** Where your single-grid model took its boundaries
from Mercator, the child takes its boundaries from the parent CROCO run, every
timestep. The child takes *everything* from the parent — its initial state
interpolated from the parent, its open edges updated by the parent as the run
proceeds. Mercator never touches the child directly. That coupling is what makes it
a *nest* rather than just a second, separate run, and it's why parent and child
must run in the **same execution**: the child needs the parent's solution live, as
it's computed.

### What building a nest actually involves

It reuses the parent you just built and adds a child on top. The shape of the work,
step by step (the full detail is Phase 8):

1. **Choose the child box** — a rectangle *inside* the parent, given in **parent
   grid indices** (not lon/lat), with margin to the parent's edges so the parent
   has room to supply boundary data. You read the parent's land mask to place it.
2. **Pick the refinement ratio** — **3 or 5**, nothing else. The child's resolution
   and timestep are the parent's divided by that ratio (a 1/12° parent at ratio 3
   gives a 1/36° child; `dt` 300 s → 100 s).
3. **Build the child grid** — a zoom-grid tool refines the parent over your index
   box and writes `croco_grd.nc.1` (the `.1` suffix is the AGRIF convention for
   child files) plus an `AGRIF_FixedGrids.in` that records the box.
4. **Build the child's initial condition** — interpolated from the same global
   ocean the parent used, onto the child grid, as `croco_ini.nc.1`. The child needs
   **no boundary file** — AGRIF *is* its boundary condition.
5. **Give the child its run-time file** — a `croco.in.1`, a copy of the parent's
   with `.1` filenames and the child's own (smaller) `dt`.
6. **Turn AGRIF on and recompile** — `# define AGRIF` in `cppdefs.h`. This is a
   compile-time switch (Step 7's lesson again), so a nested run is a **different
   binary**. Start one-way (`AGRIF_2WAY` undefined); add two-way feedback only once
   the nest runs cleanly.
7. **Run the parent** — you launch only `croco croco.in`; AGRIF reads
   `AGRIF_FixedGrids.in`, finds the child, and steps both grids together, three (or
   five) child sub-steps per parent step.

Two hard constraints fall out of the coupling and are worth knowing before you pick
a domain:

- **The child's vertical grid equals the parent's** (`N`, `theta_s`, `theta_b`,
  `hc` are all inherited) — the two grids exchange data column-by-column every step,
  so they must share the vertical. Offline nesting has no such constraint, which is
  one reason to prefer it if you want more vertical levels in the child.
- **The ratio is 3 or 5 only** — AGRIF sub-cycles the child in time by the same
  integer it refines in space.

And if you run tides on a nest, **each grid reads its own tide file** — the parent's
`croco_frc.nc` and the child's `croco_frc.nc.1` — because tidal forcing has to be
defined on each grid.

Building a nest is its own phase because of this new machinery — the child grid, the
index box, the ratio, the `.1` files, the coupling switches. This chapter got you
the parent that a child needs. To build the child:

- **[Phase 6 — Nesting (offline)](../phase6/06_nesting.md)** builds the child from
  the parent's saved output, running the two separately. It allows a different
  vertical grid.
- **[Phase 8 — AGRIF nesting](../phase8/08_agrif.md)** is the step-by-step how-to for
  the online route: choosing the box against the parent's mask, building the child
  grid, its initial condition, the `croco.in.1`, turning AGRIF on, and running
  one-way then two-way.
- **[Phase 9 — Worked example](../phase9/09_agulhas.md)** shows the whole thing done
  end-to-end: a parent *and* an AGRIF child built from nothing and run together, if
  you'd rather see a complete case before building your own.

Whether you run a single grid or a nest, the last step is the same: turn the
manual run into an automatic daily forecast. That is next.