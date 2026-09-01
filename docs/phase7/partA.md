The point of the whole exercise is to see the child resolve structure the parent
smooths over. Because the child and parent are **different CROCO runs on different
grids**, use `compare_resolution` — *not* the plain `compare_sst` and friends, which
expect a Mercator-format parent and will fail with `KeyError: 'thetao'` on CROCO
output.

```python
import sftools.validation as val

CHILD  = "forecast/scratch/Canary_25/CROCO_FILES/croco_his.nc"
PARENT = "forecast/model-runs/Canary_12/20260712/fcst/CROCO_FILES/croco_his.nc"

# both are forecast runs -> Yorig=2000; tindex=-1 is the last record, past spin-up
val.compare_resolution(CHILD, PARENT, var="temp",   Yorig=2000)   # SST
val.compare_resolution(CHILD, PARENT, var="vort_f", Yorig=2000)   # vorticity/f — eddies
val.compare_resolution(CHILD, PARENT, var="speed",  Yorig=2000)   # surface currents

# nicer figures: real coastline plus a difference panel
val.compare_resolution(CHILD, PARENT, var="temp", Yorig=2000,
                       coastline=True, diff=True)
```

Adjust the parent path to the folder you have — runs from the current driver carry
its flag tag, `20260712_plain` rather than the bare date.

!!! check
    **What you should see.** Both panels share the **same large-scale pattern** — the same cold tongue, the same warm pool, eddies in the same places. That consistency is the nesting working. But the child **resolves finer detail**: sharper SST fronts, a visibly rolled-up cyclonic eddy at the upwelling front, thin cold filaments peeling off the coast.

    In `vort_f` the difference is starkest — the child is filled with small, tightly-wound eddies and filaments where the parent has a few soft blobs. **That extra structure is what the finer grid adds**, and the reason to nest at all.

!!! note
    **Compare the last record, not the first.** As the previous page explains, the child spends roughly its first day growing the fine-scale dynamics its initial condition couldn't carry. On day 1 it still looks like the parent. `tindex=-1` is the default and gives the last record, which is what you want.

`compare_resolution` takes the same options as the other comparisons — `depth_m` for
a level other than the surface, `vmin`/`vmax` and `cmap` to fix the colour scale,
`normalized=True` for vorticity divided by *f*, and `out=` to write a file. The full
set is in the Validation chapter.