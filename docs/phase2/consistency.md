Three sets of numbers must agree across files, or the run fails or is wrong:

1. **Grid size:** `croco_grd.nc` (`xi_rho`,`eta_rho`) → `param.h`
   (`LLm0=xi_rho−2`, `MMm0=eta_rho−2`).
2. **Vertical grid:** `sigma_params` (`crocotools_param.py`) = S-coord
   (`croco.in`) = `N` (`param.h`).
3. **Boundaries:** the mask (Step 3) = `obc_dict` (`crocotools_param.py`) =
   `OBC_*` (`cppdefs.h`) = what the boundary file contains.

If a run misbehaves, check these three first — most problems are one of them
disagreeing.