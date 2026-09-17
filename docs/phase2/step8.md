`param.h` tells the model how big your grid is — and this must match
`croco_grd.nc`. Read the numbers from the grid file rather than from `grid.ini`: the
tools add points, so the two differ.

```bash
cd ~/seaforward
conda activate seaforward
python3 << 'PYEOF'
import xarray as xr
g = xr.open_dataset('forecast/scratch/Canary_12/CROCO_FILES/croco_grd.nc')
xi, eta = g.sizes['xi_rho'], g.sizes['eta_rho']
print('grid file : xi_rho=%d  eta_rho=%d' % (xi, eta))
print('param.h   : LLm0=%d   MMm0=%d   N=50' % (xi - 2, eta - 2))
PYEOF
```

Then open `param.h` in your config folder:

```bash
cd ${CONFIG_DIR}
nano param.h
```

`Ctrl-W`, type `YOUR REGIONAL CONFIG`, Enter. You'll land near this block:

``` { .text .no-copy }
#  elif defined GIBRALTAR_VHR5
       parameter (LLm0=348, MMm0=198,  N=40)
# else
      parameter (LLm0=xx,   MMm0=xx,   N=xx)   ! YOUR REGIONAL CONFIG
# endif
```

Add a new branch **just above the `# else` line**, so the block becomes:

``` { .text .no-copy }
#  elif defined GIBRALTAR_VHR5
       parameter (LLm0=348, MMm0=198,  N=40)
# elif defined  CANARY_12
      parameter (LLm0=79,   MMm0=121,   N=50)   ! Canary_12  81x123
# else
      parameter (LLm0=xx,   MMm0=xx,   N=xx)   ! YOUR REGIONAL CONFIG
# endif
```

**What the three numbers are:**

| | |
|---|---|
| **`LLm0`** | interior grid points in the x direction (west–east) |
| **`MMm0`** | interior grid points in the y direction (south–north) |
| **`N`** | sigma levels in the vertical |

**Why two less than the grid file.** `croco_grd.nc` reports `xi_rho = 81`, but two of
those are boundary rows CROCO adds around the domain it actually computes on. `LLm0`
counts the interior, so it is `xi_rho − 2` — here 79. Same for `MMm0` and `eta_rho`:
123 − 2 = 121.

**Why it must match.** These are compile-time constants, so the binary allocates arrays
of exactly this size. If they disagree with `croco_grd.nc`, the model reads a grid that
does not fit the arrays it built.

`N=50` must equal the `N` in your `sigma_params` from Step 4, and the name `CANARY_12`
must be **identical** to the one you set in `cppdefs.h`.

!!! warning
    **The new `# elif` goes above `# else`, never below it.** An `# elif` after `# else` is a compile error. Put your two lines between the `GIBRALTAR_VHR5` block and the `# else`.

Save (`Ctrl-O`, Enter), exit (`Ctrl-X`), and verify the model will pick up your
numbers:

```bash
cpp -DREGIONAL -DCANARY_12 param.h 2>/dev/null | grep "parameter (LLm0" | head
```

!!! check
    It prints `parameter (LLm0=79, MMm0=121, N=50)` — your numbers. If it shows `xx` or a BENGUELA number, your branch name or placement is off; reopen and fix.