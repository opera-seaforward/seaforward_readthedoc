Four rules you cannot work around. Each one constrains the domain you can choose, so
read them before you pick a box rather than after.

### 1. The refinement ratio must be 3 or 5

Not 2, not 4, not anything between. AGRIF sub-cycles the child in time by the same
integer factor it refines in space, and the implementation supports odd ratios 3 and
5 only.

**This is how you choose the child's resolution — indirectly.** You never type a
resolution anywhere. You set `coef` in the zoom config, and the resolution follows:

```text
child resolution = parent resolution / coef
child timestep   = parent timestep   / coef
```

From a 1/12° parent (≈9.2 km at the equator) you have exactly two options:

| `coef` | Child grid | At the equator | At 35°S | Child dt (parent 300 s) |
|---|---|---|---|---|
| **3** | 1/36° | ≈3.06 km | ≈2.6 km | 100 s |
| **5** | 1/60° | ≈1.85 km | ≈1.6 km | 60 s |

The resolution in km depends on **latitude** — a degree of longitude shrinks as
cos(lat). The same 1/36° grid is 3.06 km at São Tomé (0°N) and 2.5 km at Cape Town
(34°S). Check the actual metrics after building rather than assuming.

This is a real loss of freedom compared to offline nesting. The Phase 7 nest went
1/12° → 1/25°, a 2.08× jump chosen because it suited the region. AGRIF gives you 3 or
5 and nothing between.

**Choosing between 3 and 5.** Two considerations pull opposite ways.

*What does the physics need?* The question is whether your feature is resolved — you
want several cells across it, not one. Island wakes and mesoscale eddies live at tens
of km, so 3 km resolves them well. Submesoscale fronts and filaments want ~1 km, which
argues for 5. The internal Rossby radius is the usual yardstick: at mid-latitudes it's
20–30 km, so 3 km gives about 8 cells across it — comfortably eddy-resolving.

*What does it cost?* Badly. The cell count scales as `coef²` **and** the timestep count
as `coef`, so the total work scales as **`coef³`**:

| `coef` | cells | timesteps | **total work** |
|---|---|---|---|
| 3 | 9× | 3× | **27×** |
| 5 | 25× | 5× | **125×** |

Per unit area, relative to covering the same box at parent resolution. A `coef=5`
child is roughly **4.6× more expensive** than the same box at `coef=3`.

**Start with 3.** It's eddy-resolving at mid-latitudes, it's what somisana uses for
all three of their operational children, and the debug cycle is fast enough to
iterate. Go to 5 only when you can say which physical scale you're missing at 3.

The other lever is the **box size**, and it's the cheaper one: halving the child's
width quarters the cell count at the same resolution. A small `coef=5` child often
beats a large `coef=3` one for the same cost.

### 2. The child's `N` must equal the parent's

IGOG_12 has `N=50`, so its AGRIF child has `N=50`. The two grids exchange data every
barotropic step, and that exchange is column-by-column — mismatched vertical grids
would need an interpolation AGRIF doesn't do.

You'll notice the zoom config has **no `[Sigma_Params]` section at all**. That's not
an omission; it's the constraint made physical. There is nowhere to type a different
number.

This is the one place offline nesting wins outright: a Phase 7 child can have 75
levels against its parent's 50, and often should when it resolves a shelf the parent
covered in a handful of layers.

### 3. The child is defined by *parent grid indices*

Not longitude and latitude. `AGRIF_FixedGrids.in` says `20 48 68 96` — parent cells,
not degrees. The child's position, extent and resolution are all derived from the
parent plus that index box.

This is why Step 1 exists: you think in lon/lat, AGRIF thinks in parent cells, and
something has to convert.

### 4. The child must sit strictly inside the parent, with margin

AGRIF fills the child's open boundaries by interpolating from the parent, which
requires parent cells *outside* the child on every open edge. A child whose edge
touches the parent's own edge has nothing to read from.

How much margin? Enough that the parent's own boundary conditions — themselves
interpolated from Mercator, and imperfect near the edge — aren't feeding straight
into your child. The São Tomé child has 19–57 parent cells on each side. A margin in
single digits is worth questioning.

### What this means in practice

Choosing an AGRIF domain is more constrained than choosing a standalone region. You
pick:

- a **factor**, 3 or 5, which fixes the resolution,
- a **box in parent indices**, which must sit inside with margin,
- and you inherit `N`, `theta_s`, `theta_b` and `hc` from the parent.

Everything else — where exactly, which edges are open, how smooth the bathymetry —
is yours. Step 1 is how you find the "where exactly".