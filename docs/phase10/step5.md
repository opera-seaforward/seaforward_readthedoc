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
and the diurnals cancel, leaving the upwelling front, the coastal jet and the eddies —
the part you can compare against Mercator.

In the driver this is automatic (see Step 7). By hand, edit `croco.in`:

```bash
cd ~/seaforward/forecast/scratch/Canary_12
grep -n -A1 "^history:\|^averages:" croco.in
```

```text
39:history: LDEFHIS, NWRT, NRPFHIS / filename
40-            T      12     0
42:averages: NTSAVG, NAVG, NRPFAVG / filename
43-            1      288    0
```

Both numbers start at 72 in a tide-free config — 6 hours at `dt = 300`. Change them to
12 and 288.

Set `NTIMES` for the run while you are here. A one-day run shows the oscillation; a
seven-day run also shows the **spring–neap cycle**, as M2 and S2 drift in and out of
phase, and gives the daily average more than one record to work with:

```text
time_stepping: NTIMES   dt[sec]  NDTFAST  NINFO
                2016      300      60      1
```