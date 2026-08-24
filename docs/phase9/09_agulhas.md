# Worked example — Agulhas, from nothing to a nested forecast

This chapter builds a complete region **from scratch**: the Agulhas parent, an AGRIF
child on the Agulhas Bank, and an operational driver that runs both together every
day.

It is a companion to the reference chapters, not a replacement:

| For the general recipe | See |
|---|---|
| building a regional config by hand | **Phase 2** |
| the operational forecast driver | **Phase 3** |
| AGRIF nesting, all the gotchas | **Phase 8** |

Here we follow those recipes on a real, new region and record what actually happened —
including the numbers, which are the part you can't guess.

**Why Agulhas?** It stresses things the earlier regions didn't. The Agulhas Current is
the strongest western boundary current in the southern hemisphere (2+ m/s); the shelf
break is steep; and the coastline runs east–west across the top of the domain, so the
northern boundary is land. Canary and IGOG are gentle by comparison.

**The target:**

```
parent  Agulhas_12      17-30 E,  40-32 S    1/12 deg  (~9 km)
child   AGRIF level 1   20-27 E,  38-33 S    1/36 deg  (~2.5 km)   coef=3
```
