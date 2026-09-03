Four rules you cannot work around. Each one shapes the domain you can choose, so read
them before you pick a box rather than after.

### 1. The refinement ratio must be 3 or 5

AGRIF sub-cycles the child in time by the same integer factor it refines in space,
and the implementation supports only those two odd ratios.

**This is how you choose the child's resolution — indirectly.** You never type a
resolution anywhere. You set `coef` in the zoom config, and the resolution follows:

```text
child resolution = parent resolution / coef
child timestep   = parent timestep   / coef
```

From a 1/12° parent (≈9.2 km at the equator) you have exactly two options:

| `coef` | Child grid | At the equator | At 20°N | Child dt (parent 300 s) |
|---|---|---|---|---|
| **3** | 1/36° | ≈3.06 km | ≈2.88 km | 100 s |
| **5** | 1/60° | ≈1.85 km | ≈1.73 km | 60 s |

The resolution in km depends on **latitude** — a degree of longitude shrinks as
cos(lat). The same 1/36° grid is 3.06 km at the equator, 2.88 km over the Canary
upwelling at 20°N, and 2.5 km off Cape Town at 34°S. Check the actual metrics after
building rather than assuming.

Offline nesting takes any ratio — the Phase 7 nest went 1/12° → 1/25°, a 2.08× jump
chosen to suit the region. AGRIF takes one of two, and in exchange gives you boundary
exchange every barotropic step and, if you want it, feedback to the parent.

**Choosing between them.** Two considerations pull opposite ways.

*What does the physics need?* The question is whether your feature is resolved — you
want several cells across it, not one. Mesoscale eddies live at tens of km, so 3 km
resolves them well. Submesoscale fronts and filaments want ~1 km, which argues for the
finer option. The internal Rossby radius is the usual yardstick: at mid-latitudes it's
20–30 km, so 3 km gives about 8 cells across it — comfortably eddy-resolving.

*What does it cost?* The cell count scales as `coef²` and the timestep count as
`coef`, so the total work scales as **`coef³`**:

| `coef` | cells | timesteps | **total work** |
|---|---|---|---|
| 3 | 9× | 3× | **27×** |
| 5 | 25× | 5× | **125×** |

Per unit area, relative to covering the same box at parent resolution. A `coef=5`
child costs roughly 4.6× what the same box costs at `coef=3`.

**Start with 3.** It is eddy-resolving at mid-latitudes and the debug cycle is fast
enough to iterate on. Go finer once you can say which physical scale you are missing.

The other lever is the **box size**, and it is the cheaper one: halving the child's
width quarters the cell count at the same resolution. A small fine child often beats
a large coarse one for the same cost.

### 2. The child's `N` must equal the parent's

Canary_12 has `N=50`, so its AGRIF child has `N=50`. The two grids exchange data every
barotropic step, and that exchange is column-by-column — mismatched vertical grids
would need an interpolation AGRIF doesn't do.

The zoom config has no `[Sigma_Params]` section, which is the constraint made
physical: there is nowhere to set a different number.

If the child needs its own vertical grid — more layers over a shelf the parent covered
in a handful — that is what offline nesting (Phase 7) is for.

### 3. The child is defined by *parent grid indices*

Not longitude and latitude. `AGRIF_FixedGrids.in` says `13 75 50 111` — parent cells,
not degrees. The child's position, extent and resolution are all derived from the
parent plus that index box.

This is why Step 1 exists: you think in lon/lat, AGRIF thinks in parent cells, and
something has to convert.

### 4. The child must sit strictly inside the parent, with margin

AGRIF fills the child's open boundaries by interpolating from the parent, which
requires parent cells *outside* the child on every open edge. A child whose edge
touches the parent's own edge has nothing to read from.

How much margin? Enough that the parent's own boundary conditions — themselves
interpolated from Mercator, and least reliable near the edge — aren't feeding straight
into the child. The Canary child has 12 parent cells to the west, 49 to the south and
12 to the north. Its east margin is only 6, which matters less because that edge is
closed on the African coast and has no interpolation to do.

### What this means in practice

An AGRIF domain is defined by three choices:

- a **factor**, which fixes the resolution,
- a **box in parent indices**, which must sit inside with margin,
- and the vertical grid, inherited from the parent: `N`, `theta_s`, `theta_b`, `hc`.

Everything else — where exactly, which edges are open, how smooth the bathymetry —
is yours. Step 1 is how you find the "where exactly".