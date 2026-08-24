# Phase 10 — Tides

Everything so far — ini, boundaries, atmosphere — describes the *slow* ocean:
the circulation that Mercator resolves and that a daily snapshot captures. Tides
are the fast ocean. They rise and fall roughly twice a day, they are almost
invisible in the deep sea and dominant on the shelf, and no global reanalysis
product carries them. If your model touches a coast — sea level, currents,
mixing, sediment — the tide is often the largest signal there, and it is the one
thing you have to add yourself.

This chapter adds tidal forcing from TPXO, proves it on a standalone parent,
then folds it into the operational driver as a runtime option that composes with
the AGRIF nest — so any of the six combinations (no-child / one-way / two-way,
each with or without tides) runs from one command.

## Where this fits in the build

Tides are **not a separate configuration** — they are additions to the forecast
config you already built in Phase 2. If you built Canary_12 (or any region)
following Phase 2, you turned tides *off* at three points. This chapter turns
them back on and adds the tide file. Nothing here replaces Phase 2; it edits the
same files.

Here is exactly where each tide action lands relative to the Phase 2 steps:

| Phase 2 step | what you did there (tide-free) | what tides change |
|---|---|---|
| Step 4 — `crocotools_param.py` | wrote the mercator ini/bry params | **add** a *second* param file, `crocotools_param_tides.py`, for TPXO (Step 2 below) |
| Step 5 — prepare data | ran make_ini / make_bry | **add** a `make_tides` run to build `croco_frc.nc` (Step 3 below) |
| Step 8.3 — `cppdefs.h` | left `TIDES` **undef** | **flip to** `# define TIDES` + the SSH/UV/POT block (Step 4 below) |
| Step 10 — `croco.in` | set title, sponge | **point** `forcing:` at `croco_frc.nc` (Step 4 below) — often already correct |
| Step 12 — compile | built `croco` | **rebuild** — tides pull in extra source; the binary is a *different* build |
| Step 13 — run | 6 h history / 6 h average | **retime** to hourly history / daily average (Step 5 below) |

So the reading order is: **build the config tide-free with Phase 2 first**, prove
it runs, *then* come here and add tides on top. Doing it that way means if the
tidal run misbehaves, you already know the tide-free config was sound — the tide
is the only new variable.

The figure below highlights where this phase sit on in the SEA-FORWARD entire build chain
![Phase 10](../img/surface_forcing.png)

!!! note
    **The one Phase 2 check that changes.** Phase 2 Step 8's verification expects `TIDES` to be `undef`. Once you follow this chapter, that same grep will show `TIDES` **defined** — which is correct now, not a mistake. The `USE_CALENDAR` part of that check stays `undef` either way.


## What a tide file is

CROCO does not simulate the astronomy of the tide. It reads a small set of
**harmonic constituents** — for each tidal wave (M2, S2, K1, …) an amplitude and
a phase at every grid point — and reconstructs the tidal signal at run time by
summing those waves. The harmonics come from a global tidal atlas; we use
**TPXO** (the OSU TPXO model, derived from satellite altimetry).

The waves we request, and what they are:

| wave | period | what it is |
|---|---|---|
| M2 | 12.42 h | principal lunar semidiurnal — the big one |
| S2 | 12.00 h | principal solar semidiurnal |
| N2 | 12.66 h | larger lunar elliptic |
| K2 | 11.97 h | lunisolar semidiurnal |
| K1 | 23.93 h | lunisolar diurnal |
| O1 | 25.82 h | principal lunar diurnal |
| P1 | 24.07 h | principal solar diurnal |
| Q1 | 26.87 h | larger lunar elliptic diurnal |
| Mf | 13.66 d | lunar fortnightly |
| Mm | 27.55 d | lunar monthly |

The four semidiurnals plus four diurnals carry almost all the coastal tidal
energy; Mf and Mm are long-period and small but cheap to include.


## The epoch problem — why the tide file is per-cycle

A harmonic constituent is an amplitude and a phase. **Phase relative to what?**
To a specific instant in time — the astronomical reference. If the model does
not know the real calendar date, the phase reference has to be baked into the
tide file when it is built, keyed to the run's start date.

Our forecast setup runs with `USE_CALENDAR` **off** (the same choice the somisana
operational configs make). So the tide file is **not** a build-once asset like
the grid. Every forecast cycle starts on a different day, and each needs its own
`croco_frc.nc` generated at that cycle's start date. This is exactly parallel to
`make_ini`/`make_bry`, which also regenerate per cycle — and unlike the grid,
which is built once and reused forever.

!!! important
    **The one thing to remember about tides:** the tide file carries a date. Build it for the wrong day and every wave is out of phase. In the driver this is handled automatically — the tide gen runs at the spin-up start date each cycle but if you generate a tide file by hand, the `--run_date` you pass *is* the phase reference.
