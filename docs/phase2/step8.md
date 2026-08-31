`param.h` tells the model how big your grid is — and this must match
`croco_grd.nc`. Open it:

```bash
nano param.h
```

`Ctrl-W`, type `YOUR REGIONAL CONFIG`, Enter. You'll land near this block:

```
#  elif defined GIBRALTAR_VHR5
       parameter (LLm0=348, MMm0=198,  N=40)
# else
      parameter (LLm0=xx,   MMm0=xx,   N=xx)   ! YOUR REGIONAL CONFIG
# endif
```

Add a new branch **just above the `# else` line**, so the block becomes:

```
#  elif defined GIBRALTAR_VHR5
       parameter (LLm0=348, MMm0=198,  N=40)
# elif defined  CANARY_12
      parameter (LLm0=79,   MMm0=121,   N=50)   ! Canary_12  81x123
# else
      parameter (LLm0=xx,   MMm0=xx,   N=xx)   ! YOUR REGIONAL CONFIG
# endif
```

**What:** this tells the model your grid is 79×121 (interior points) with 50
vertical levels. **Why:** the numbers come from Step 2 (`xi_rho=81 → LLm0=79`,
`eta_rho=123 → MMm0=121`), and `N=50` matches your `sigma_params`. The name
`CANARY_12` must be **identical** to the one you set in `cppdefs.h`.

!!! warning
    **The new `# elif` goes above `# else`, never below it.** An `# elif` after `# else` is a compile error. Put your two lines between the `GIBRALTAR_VHR5` block and the `# else`.

Save (`Ctrl-O`, Enter), exit (`Ctrl-X`), and verify the model will pick up your
numbers:

```bash
cpp -DREGIONAL -DCANARY_12 param.h 2>/dev/null | grep "parameter (LLm0" | head
```

!!! check
    It prints `parameter (LLm0=79, MMm0=121, N=50)` — your numbers. If it shows `xx` or a BENGUELA number, your branch name or placement is off; reopen and fix.