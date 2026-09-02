# Phase 9 — Worked example: Agulhas, end to end

This chapter builds a complete region **from scratch**: the Agulhas parent, an AGRIF
child on the Agulhas Bank, and an operational driver that runs both together every
day.

It is a companion to the reference chapters, not a replacement:

| For the general recipe | See |
|---|---|
| building a regional config by hand | **Phase 2** |
| the operational forecast driver | **Phase 3** |
| AGRIF nesting, and its gotchas | **Phase 8** |

Here we follow those recipes on a real, new region and record what actually happened —
including the numbers, which are the part you cannot guess.

**Why Agulhas?** It stresses things the earlier regions did not. The Agulhas Current is
the strongest western boundary current in the southern hemisphere, over 2 m/s; the
shelf break is steep; and the coastline runs east–west across the top of the domain, so
the northern boundary is land. 

**The target:**

```text
parent  Agulhas_12      17-30 E,  40-32 S    1/12 deg  (~9 km)
child   AGRIF level 1   20-27 E,  38-33 S    1/36 deg  (~2.5 km)   coef=3
```

| | Parent `Agulhas_12` | AGRIF child |
|---|---|---|
| Resolution | 1/12° (~9 km) | 1/36° (~2.5 km) |
| Grid | 159 × 99 × 50 | 248 × 182 × 50 |
| Box | 16.6–30.4°E, 40.0–31.8°S | 20.0–27.0°E, 38.1–33.1°S |
| Timestep | 300 s | 100 s |
| Boundaries | S, W, E open; N closed | AGRIF-supplied |

The chapter is in three phases. **Phase A** builds the parent alone and proves it runs.
**Phase B** adds the AGRIF child. **Phase C** wires both into the operational driver,
with spin-up, tides and a real forecast cycle.

!!! important
    **Complete Phase A before starting Phase B.** A nested run has two grids, two configs, two initial conditions and a coupling between them. If it fails and you have never seen the parent run alone, you do not know which half is broken. Phase A is the control experiment.