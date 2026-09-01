This step is entirely diagnostic — you write no config here. You interrogate the
parent's mask until you know where the child can go.

!!! important
    **Read the mask, not a plot.** A saturated colour map will make dry land look like ocean. A box chosen from an SST figure can land hundreds of kilometres inland. The mask is the only authority.

Four checks, in order. Run them from `~/seaforward`.

### 1a — The parent's dimensions

Every index below is relative to this grid, so start by reading it:

```python
import xarray as xr, numpy as np
g   = xr.open_dataset('forecast/scratch/IGOG_12/CROCO_FILES/croco_grd.nc')
lon = g.lon_rho.values
lat = g.lat_rho.values
print('IGOG: xi=%d eta=%d, lon %.2f-%.2fE, lat %.2f-%.2fN'
      % (lon.shape[1], lon.shape[0], lon.min(), lon.max(), lat.min(), lat.max()))
```

```text
IGOG: xi=105 eta=141, lon 3.94-12.56E, lat -6.04-5.54N
```

### 1b — Test a candidate box

This converts a lon/lat box to parent indices and reports what you need to judge it:
the child size, the margin to the parent's edges, the ocean fraction, the depth
range, and the land/water pattern along each of the four edges.

```python
import xarray as xr, numpy as np
g   = xr.open_dataset('forecast/scratch/IGOG_12/CROCO_FILES/croco_grd.nc')
lon = g.lon_rho.values[0, :]     # 1-D along xi
lat = g.lat_rho.values[:, 0]     # 1-D along eta
m   = g.mask_rho.values          # 1 = ocean, 0 = land
h   = g.h.values

def check(name, lo0, lo1, la0, la1, coef=3):
    imin = int(np.argmin(abs(lon - lo0))); imax = int(np.argmin(abs(lon - lo1)))
    jmin = int(np.argmin(abs(lat - la0))); jmax = int(np.argmin(abs(lat - la1)))
    sm = m[jmin:jmax+1, imin:imax+1]
    sh = h[jmin:jmax+1, imin:imax+1]

    print(name)
    print('  lon %.1f-%.1fE lat %.1f-%.1fN' % (lo0, lo1, la0, la1))
    print('  -> imin=%d imax=%d jmin=%d jmax=%d' % (imin, imax, jmin, jmax))
    print('  parent cells: %d x %d   child at %dx: %d x %d'
          % (imax-imin+1, jmax-jmin+1, coef,
             (imax-imin)*coef+1, (jmax-jmin)*coef+1))
    print('  margin to parent edge: W=%d E=%d S=%d N=%d cells'
          % (imin, m.shape[1]-1-imax, jmin, m.shape[0]-1-jmax))
    print('  ocean: %.1f%%   depth: %.0f-%.0f m'
          % (sm.sum()/sm.size*100, sh.min(), sh.max()))
    strip = lambda r: ''.join('O' if v == 1 else '.' for v in r)
    for e, v in [('S', sm[0, :]), ('N', sm[-1, :]),
                 ('W', sm[:, 0]), ('E', sm[:, -1])]:
        pct = v.sum() / len(v) * 100
        tag = ('all water -> OPEN'  if v.all()      else
               'ALL LAND -> CLOSE'  if v.sum() == 0 else
               'MIXED(%d land)' % int((v == 0).sum()))
        print('    %s edge: %3d/%3d ocean (%5.1f%%)  %s'
              % (e, int(v.sum()), len(v), pct, tag))
        print('       ', strip(v))
    print()

check('A) open-ocean SW box',    4.5, 7.5, -4.5, -1.5)
check('B) Sao Tome / Principe',  5.5, 7.8, -0.5,  1.8)
```

```text
A) open-ocean SW box
  lon 4.5-7.5E lat -4.5--1.5N
  -> imin=7 imax=43 jmin=18 jmax=55
  parent cells: 37 x 38   child at 3x: 109 x 112
  margin to parent edge: W=7 E=61 S=18 N=85 cells
  ocean: 100.0%   depth: 1212-4999 m
    S edge:  37/ 37 ocean (100.0%)  all water -> OPEN
    N edge:  37/ 37 ocean (100.0%)  all water -> OPEN
    W edge:  38/ 38 ocean (100.0%)  all water -> OPEN
    E edge:  38/ 38 ocean (100.0%)  all water -> OPEN

B) Sao Tome / Principe
  lon 5.5-7.8E lat -0.5-1.8N
  -> imin=19 imax=47 jmin=67 jmax=95
  parent cells: 29 x 29   child at 3x: 85 x 85
  margin to parent edge: W=19 E=57 S=67 N=45 cells
  ocean: 98.6%   depth: 285-3738 m
    S edge:  29/ 29 ocean (100.0%)  all water -> OPEN
    N edge:  29/ 29 ocean (100.0%)  all water -> OPEN
    W edge:  29/ 29 ocean (100.0%)  all water -> OPEN
    E edge:  29/ 29 ocean (100.0%)  all water -> OPEN
```

Box **B** is the one used in this chapter: four clean edges, the islands safely
interior in that 1.4% land, and a small child (85×85) so the debug cycle is fast.

**Reading the output:**

| Field | What it tells you |
|---|---|
| `imin/imax/jmin/jmax` | goes straight into the zoom `.ini` |
| `child at 3x` | the cost — cells scale as the square, and the child sub-steps 3× as well |
| `margin` | parent cells between the child and the parent's own edge; under 10 leaves AGRIF little room to supply boundary data |
| `ocean %` | how much of the box is water — low means cells spent on land |
| `depth` | the child's `hmax`, and a warning of steep bathymetry |
| edge strips | the decisive check — see *Reading the edges* below |

### 1c — Scan for a clean edge

If an edge comes back MIXED with holes, scan rather than guess. This walks a
candidate edge across a range of latitudes and flags which are contiguous:

```python
import xarray as xr, numpy as np
g   = xr.open_dataset('forecast/scratch/IGOG_12/CROCO_FILES/croco_grd.nc')
lon = g.lon_rho.values[0, :]; lat = g.lat_rho.values[:, 0]; m = g.mask_rho.values
i0 = int(np.argmin(abs(lon - 6.0)))       # the box's west limit
i1 = int(np.argmin(abs(lon - 10.5)))      # the box's east limit
strip = lambda r: ''.join('O' if v == 1 else '.' for v in r)
for la in [4.5, 4.2, 4.0, 3.8, 3.6, 3.4, 3.2, 3.0]:
    j = int(np.argmin(abs(lat - la)))
    v = m[j, i0:i1+1]
    # "clean" = all the water is contiguous, land only at the far end
    lastO = np.max(np.where(v == 1)[0]) if v.sum() else -1
    clean = v[:lastO+1].all() if lastO >= 0 else False
    print('%.1fN: %2d/%d water  %s  %s'
          % (lat[j], int(v.sum()), len(v), strip(v),
             'CLEAN' if clean else 'has holes'))
```

```text
4.5N:  3/55 water  ..............O.............OO.......   has holes   <- mainland
4.2N: 36/55 water  OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO...  CLEAN
4.0N: 40/55 water  OOOO...OOOO....O.......                  has holes  <- Bioko
3.8N: 44/55 water  OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO...  CLEAN
3.6N: 40/55 water  OOOO....OOOOOOOO......                   has holes  <- Bioko
3.4N: 42/55 water  OOOO....OOOOOOOOOOO...                   has holes  <- Bioko
3.2N: 47/55 water  OOOO.OOOOOOOOOOOOOOO..                   has holes  <- Bioko
3.0N: 48/55 water  OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO.......  CLEAN
```

Three clean options, and the pattern is legible. **Bioko** (≈3.2–4.0°N, 8.7°E)
punches holes in every edge in that band; the mainland fills 4.5°N. 4.2°N is the
highest clean edge, threading between the island and the coast.

The `clean` test checks that all the water is contiguous from the west, with land
only after the last water cell — the "open boundary that terminates at a coast"
shape, which is fine. Holes in the middle are not.

### 1d — Sample a specific line

When a result surprises you, sample along the line directly:

```python
import xarray as xr, numpy as np
g   = xr.open_dataset('forecast/scratch/IGOG_12/CROCO_FILES/croco_grd.nc')
lon = g.lon_rho.values[0, :]; lat = g.lat_rho.values[:, 0]; m = g.mask_rho.values
for la in [4.5, 3.0]:
    j = int(np.argmin(abs(lat - la)))
    print('=== along %.1fN ===' % lat[j])
    for lo in [6.0, 6.5, 7.0, 7.5, 8.0, 9.0, 10.0, 10.5]:
        i = int(np.argmin(abs(lon - lo)))
        print('   %.1fE : %s' % (lon[i], 'OCEAN' if m[j, i] == 1 else 'land'))
```

```text
=== along 4.5N ===
   6.0E : land
   6.5E : land
   7.0E : land
   ...
   10.5E : land
=== along 3.0N ===
   6.0E : OCEAN
   6.5E : OCEAN  ...  9.0E : OCEAN
   10.0E : land      <- meets the Cameroon coast
   10.5E : land
```

4.5°N is not a marginal case or a tuning problem — it is the African continent.

!!! warning
    **This coarse 0.5° sampling misses narrow gaps.** It steps straight over the 4.2°N channel that the fine scan in 1c found. Use 1d to confirm a suspicion, not to search.

### Reading the edges

An AGRIF child edge must be one of:

| Edge mask | Setting | Verdict |
|---|---|---|
| All water | **open** | parent supplies data across the whole edge |
| All land | **closed** | a coastal wall, which is true |
| Water then land, **contiguous** | open | an open boundary that terminates at a coast |
| Water with land **holes** in the middle | — | **bad** — the edge slices through an island |

The last case is the one to avoid: parent and child disagree about land and sea
exactly where they exchange data.

**Mixed edges are fine.** The parent IGOG_12's own south boundary is 98% water with
two land cells at its east end, and it works.

The case that cannot be made to work is an edge **mostly land with a few water
holes**. You cannot close it — those cells are real ocean the parent flows through —
and you cannot open it, because there is no parent water behind most of the edge to
read from. That was 4.5°N: 3 water cells out of 55.

### What this ruled out

The first candidate here was `6–10.5°E, 2°S–4.5°N`, chosen because the parent's SST
plot showed apparent ocean near 4.5°N. The mask gave 3 water cells out of 55 on that
north edge, and 1d confirmed the whole line was land. Scanning southward (1c) found
Bioko punching holes through 3.2–4.0°N, with clean edges only at 4.2, 3.8 and 3.0°N.

The general lesson: scan candidate edges at fine latitude spacing rather than
guessing, and watch for islands, not just the mainland.