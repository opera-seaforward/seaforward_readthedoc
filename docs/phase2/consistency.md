Three sets of numbers and one name must agree across files, or the run fails or is
wrong:

1. **Config name:** `# define CANARY_12` (`cppdefs.h`) = `# elif defined CANARY_12`
   (`param.h`). If they differ, the model compiles with the wrong grid size.
2. **Grid size:** `croco_grd.nc` (`xi_rho`, `eta_rho`) → `param.h`
   (`LLm0 = xi_rho − 2`, `MMm0 = eta_rho − 2`).
3. **Vertical grid:** `sigma_params` (`crocotools_param.py`) = S-coord
   (`croco.in`) = `N` (`param.h`).
4. **Boundaries:** the mask (Step 3) = `obc_dict` (`crocotools_param.py`) =
   `OBC_*` (`cppdefs.h`) = what the boundary file contains.

If a run misbehaves, check these four first — most problems are one of them
disagreeing.