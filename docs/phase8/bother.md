In one-way nesting (offline *or* AGRIF), information flows in exactly one direction:

```
parent  ──boundaries──▶  child
        ◀── nothing ───
```

The child sees everything the parent knows. The parent sees nothing the child
computes. From the parent's point of view, the child does not exist.

That matters more than it sounds. In the worked example below, the child resolves a
cyclonic eddy and an island wake that the parent renders as a smooth smear. Two
different answers, for the same water, at the same instant — and in one-way mode the
parent keeps its wrong one forever, then **advects it downstream** into the rest of
the domain.

Two-way closes the loop:

```
parent  ──boundaries──▶  child
        ◀──feedback────
```

Where the grids overlap, the child's fine cells are averaged back onto the parent's
coarse cells, replacing what the parent computed.

**Where does the correction apply?** Directly, only inside the child's footprint.
But the parent's own dynamics then carry those corrected values outward — so after
a day you see differences well beyond the box, following the flow. The parent does
not gain *resolution* outside the box; it gains **correct values at its own
resolution**, instead of a fabricated smear from a grid too coarse to compute the
feature at all.

| | Offline (Phase 7) | AGRIF one-way | AGRIF two-way |
|---|---|---|---|
| Child boundaries from | parent's **history file** (hourly) | parent, **every barotropic step** | same |
| Parent learns from child | never | never | **yes** |
| Execution | sequential, 2 runs | simultaneous, 1 executable | same |
| Resolution ratio | anything | **3 or 5 only** | **3 or 5 only** |
| Child vertical levels | free | **must equal parent** | **must equal parent** |

Note that even *one-way AGRIF* beats offline nesting: the child gets boundary data at
the barotropic frequency rather than interpolated between hourly snapshots, so fast
waves aren't filtered out. Two-way adds the part that is structurally impossible
offline.

**The costs are real.** You must run both grids together; the ratio is fixed at 3 or
5; the child inherits the parent's vertical grid; and two-way injects fine-grid
values into a coarse grid every step, which can ring or destabilise if the grids
disagree at the interface.
