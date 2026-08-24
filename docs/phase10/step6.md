A one-day run with the retimed output. The proof is not `MAIN: DONE` — it is the
tidal signal itself. Track sea level at a shelf point across the 24 hourly
records:

```
SSH at a shelf point (hourly):
   0.0h  +0.713
   3.0h  +0.600
   9.0h  +0.253   <- low
  15.0h  +0.956   <- high
  21.0h  +0.029   <- low
  24.0h  +0.594
swing: 0.927 m
```

Two full rise-and-fall cycles in 24 hours — a **~12.4 h period**. That is M2.
The tide-free run at the same point drifted slowly with no oscillation; this one
breathes. Tides are forcing the model.

The domain-wide tidal range (max − min over the 24 hourly records) confirms it
spatially:

```
tidal range: mean 0.94 m   max 3.65 m
```

Near-zero in deep water, 2–3.6 m on the Agulhas Bank. That is the defining
signature of shelf tides — the wave amplifies as it shoals, because the same
energy is squeezed into shallower water. A uniform range would mean something was
wrong; this concentration on the shelf is the physics being right.

### The daily mean matches Mercator — tides didn't break the circulation

The key regression check: does adding tides degrade the slow ocean? Compare the
daily-mean SSH against Mercator's daily mean.

```
daily-mean SSH anomaly RMSE vs Mercator:  0.052 m   (tide-free run: 0.048 m)
```

Essentially unchanged. The tide lives in the hourly output and vanishes cleanly
in the 24-hour average, leaving circulation that agrees with Mercator as well as
it did before. Nothing lost, tidal physics gained.

!!! important
    **A comparison you must not make.** Mercator has no tides. Comparing your *hourly* (tide-carrying) SSH against Mercator shows differences up to metres on the shelf — that is the entire tide Mercator lacks, not a model error. Only the daily mean is a fair comparison, and only because averaging removes the one thing Mercator doesn't have.