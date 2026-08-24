### cppdefs.h

Tides are compile-time. The block (somisana's, proven operationally):

```
# define  TIDES
# ifdef TIDES
#  define SSH_TIDES        /* tidal sea-surface elevation at the boundary */
#  define UV_TIDES         /* tidal currents at the boundary */
#  define POT_TIDES        /* tidal potential (self-attraction/loading) forcing */
#  undef  TIDES_MAS
# endif
```

`SSH_TIDES` and `UV_TIDES` apply the tide at the open boundaries; `POT_TIDES`
adds the tide-generating force in the interior. `TIDES_MAS` (a different phase
convention tied to `Yorig=1900`) stays **off**.

Leave `USE_CALENDAR` **undef**. That is the choice that makes the phase epoch
live in the tide file rather than in CROCO's calendar — which is exactly why the
file is regenerated per cycle.

### croco.in

Tides read entirely from the frc file plus the cppdefs switches — this CROCO
version needs **no** `Ntides` section. The only requirement is that the
`forcing:` keyword points at the tide file:

```
forcing: filename
    CROCO_FILES/croco_frc.nc
```

(If it already points there — from a previous forcing setup — nothing to change.)

Then recompile. Tides pull in extra source (`tides.F` and friends), so the link
line grows; `CROCO is OK` at the end means it built.