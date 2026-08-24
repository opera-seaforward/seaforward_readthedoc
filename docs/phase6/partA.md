The point of the whole exercise is to see the child resolve structure the parent
smooths over. Because the child and parent are **different CROCO runs on different
grids**, use the `compare_*_resolution` helpers (Phase 5 §5.6), *not* the plain
`compare_*` (those expect a Mercator parent and will raise `KeyError: 'thetao'`).

```python
import sftools.validation as val
CHILD  = "forecast/scratch/Canary_25/CROCO_FILES/croco_his.nc"
PARENT = "forecast/model-runs/Canary_12/20260712/fcst/CROCO_FILES/croco_his.nc"

# both are forecast runs -> Yorig=2000; tindex=-1 = last record (past spin-up)
val.compare_resolution(CHILD, PARENT, var="temp",   Yorig=2000)   # SST
val.compare_resolution(CHILD, PARENT, var="vort_f", Yorig=2000)   # vorticity/f — eddies
val.compare_resolution(CHILD, PARENT, var="speed",  Yorig=2000)   # surface currents

# nicer figures: real coastline + a difference panel
val.compare_resolution(CHILD, PARENT, var="temp", Yorig=2000, coastline=True, diff=True)
```

!!! check
    ✅ **What you should see.** Both panels share the **same large-scale pattern** (the nesting is consistent — same cold tongue, same warm pool, eddies in the same places). But the child **resolves finer detail**: sharper SST fronts, a visibly rolled-up cyclonic eddy at the upwelling front, thin cold filaments peeling off the coast. In `vort_f` the difference is starkest — the child is filled with small, tightly-wound eddies and filaments where the parent has a few soft blobs. **That extra structure is the value the finer grid adds** — the reason to nest.

!!! important
    Remember the spin-up note: compare the **last record** (day 3–5), not day 1. On day 1 the child still looks like the parent because the fine dynamics haven't grown yet.