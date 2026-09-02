M2 has a **12.4-hour period**. The default 6-hourly history barely samples it, and a
6-hour *average* smears half a tidal cycle — averaging a rising tide against a falling
one, losing the signal. So with tides:

| output | tide-free | with tides | why |
|---|---|---|---|
| **history** | 6 h | **1 h** | ~12 samples per M2 cycle to resolve the oscillation |
| **averages** | 6 h | **24 h** | a full tidal day averages the tide *out*, leaving the residual circulation |

At `dt = 300 s`:

```text
history NWRT = 3600/300  = 12     (hourly)
average NAVG = 86400/300 = 288    (daily)
```

The daily average is not just a size convenience — it is the physically correct way to
see the *ocean* underneath the tide. With tides in the model, the raw 3D fields slosh
back and forth twice a day. Average over 24 hours and the semidiurnals, all near 12 h,
and the diurnals cancel, leaving the Agulhas Current, the eddies, the geostrophic
setup — the part you can compare against Mercator.

In the driver this is automatic (see Step 7). By hand, edit `croco.in`:

```text
history: LDEFHIS, NWRT, NRPFHIS / filename
            T      12     0
averages: NTSAVG, NAVG, NRPFAVG / filename
            1      288    0
```