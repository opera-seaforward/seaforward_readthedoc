### cppdefs.h

Tides are compile-time, and the switch lives in **two** places. First your config's own
block, where `TIDES` is currently `undef`:

```bash
grep -n "TIDES" cppdefs.h | head -4
```

```text
97:# undef  TIDES
295:# ifdef TIDES
296:#  define SSH_TIDES
297:#  define UV_TIDES
```

Line 97 is the one to change — `# define TIDES`. Lines 295 onward are the sub-options,
which are already set correctly and need no edit:

```text
# ifdef TIDES
#  define SSH_TIDES        /* tidal sea-surface elevation at the boundary */
#  define UV_TIDES         /* tidal currents at the boundary */
#  define POT_TIDES        /* tidal potential forcing in the interior */
#  undef  TIDES_MAS
#  define TIDERAMP
# endif
```

`SSH_TIDES` and `UV_TIDES` apply the tide at the open boundaries; `POT_TIDES` adds the
tide-generating force in the interior. `TIDES_MAS` — a different phase convention tied
to `Yorig=1900` — stays **off**.

`TIDERAMP` ramps the tidal forcing up over the first day rather than switching it on at
full strength. The initial condition carries no tidal signal at all, so without the ramp
the model gets a shock at step zero. Leave it defined.

Verify:

```bash
sed -n '96,101p' cppdefs.h
```

Leave `USE_CALENDAR` **undef**. That is the choice that makes the phase epoch live in
the tide file rather than in CROCO's calendar, which is exactly why the file is
regenerated per cycle.

### croco.in

Tides read entirely from the frc file plus the cppdefs switches — this CROCO version
needs **no** `Ntides` section. The only requirement is that the `forcing:` keyword
points at the tide file:

```bash
grep -n -A1 "^forcing:" croco.in
```

```text
24:forcing: filename
25-    CROCO_FILES/croco_frc.nc
```

If it already points there, from a previous forcing setup, there is nothing to change.
Stage the file you generated in Step 3:

```bash
cp $TGEN/croco_frc.nc ~/seaforward/forecast/scratch/Canary_12/CROCO_FILES/
```

### Recompile

Tides pull in extra source (`tides.F` and friends), so the link line grows;
`CROCO is OK` at the end means it built.

```bash
conda deactivate
source ~/seaforward/env.sh
which nf-config          # must be .../opt_seq/bin/nf-config
./jobcomp 2>&1 | tee compile_tides.log | tail -5
cp croco croco_plain_tides
```

The driver selects its binary by name — `croco_plain_tides` for a tidal run without a
nest, `croco_1way_tides` with one. Skip the rename and it reports `binary not found`.