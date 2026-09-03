# Phase 10 — Tides

Everything so far — ini, boundaries, atmosphere — describes the *slow* ocean: the
circulation that Mercator resolves and that a daily snapshot captures. Tides are the
fast ocean. They rise and fall roughly twice a day, they are almost invisible in the
deep sea and dominant on the shelf, and no global reanalysis product carries them. If
your model touches a coast — sea level, currents, mixing, sediment — the tide is often
the largest signal there, and it is the one thing you have to add yourself.

This chapter adds tidal forcing from TPXO, proves it on a standalone parent, then folds
it into the operational driver as a runtime option. `--tides` composes with `--child`,
so a tidal nest is available from one command — each combination needing its own build.

## Where this fits in the build

Tides are **not a separate configuration** — they are additions to the forecast config
you already built in Phase 2. Following Phase 2 you turned tides *off* at three points.
This chapter turns them back on and adds the tide file. Nothing here replaces Phase 2;
it edits the same files.

Here is where each tide action lands relative to the Phase 2 steps:

| Phase 2 step | what you did there (tide-free) | what tides change |
|---|---|---|
| Step 4 — `crocotools_param.py` | wrote the Mercator ini/bry params | **add** a second param file, `crocotools_param_tides.py`, for TPXO (Step 2) |
| Step 5 — prepare data | ran make_ini and make_bry | **add** a `make_tides` run to build `croco_frc.nc` (Step 3) |
| Step 8 — `cppdefs.h` | left `TIDES` **undef** | **flip to** `# define TIDES` plus the SSH/UV/POT block (Step 4) |
| Step 10 — `croco.in` | set title, sponge | **point** `forcing:` at `croco_frc.nc` (Step 4) — often already correct |
| Step 12 — compile | built `croco` | **rebuild** — tides pull in extra source, so the binary is a different build |
| Step 13 — run | 6 h history and average | **retime** to hourly history, daily average (Step 5) |

So the reading order is: **build the config tide-free with Phase 2 first**, prove it
runs, then come here and add tides on top. That way, if the tidal run misbehaves you
already know the tide-free config was sound — the tide is the only new variable.

![Where this phase sits in the build chain](../img/tidal_forcing.png)

!!! note
    **The one Phase 2 check that changes.** Phase 2 Step 8's verification expects `TIDES` to be `undef`. Once you follow this chapter that same grep shows `TIDES` **defined**, which is correct now rather than a mistake. The `USE_CALENDAR` part of the check stays `undef` either way.

## What a tide file is

CROCO does not simulate the astronomy of the tide. It reads a small set of **harmonic
constituents** — for each tidal wave, a set of amplitudes and phases at every grid
point — and reconstructs the signal at run time by summing those waves. The harmonics
come from a global tidal atlas; we use **TPXO**, the OSU model derived from satellite
altimetry.

Each wave carries three things:

- **Elevation** — `tide_Eamp` and `tide_Ephase`, the rise and fall of the sea surface.
- **Currents** — `tide_Cmin`, `tide_Cmax`, `tide_Cangle` and `tide_Cphase`, the tidal
  current as an ellipse: how fast along each axis, which way it is oriented, and when
  it peaks.
- **Potential** — `tide_Pamp` and `tide_Pphase`, the astronomical forcing acting on the
  water column directly rather than through the boundaries.

The last two are there because Step 3 generates with `cur=True` and `pot=True`. Eight
variables in all, on the model grid, for each of the ten waves below.

The waves we request:

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

The four semidiurnals and four diurnals carry almost all the coastal tidal energy; Mf
and Mm are long-period and small, but cheap to include.

## The epoch problem — why the tide file is per-cycle

A harmonic constituent is an amplitude and a phase. **Phase relative to what?** To a
specific instant — the astronomical reference. If the model does not know the real
calendar date, that reference has to be baked into the tide file when it is built,
keyed to the run's start date.

This forecast setup runs with `USE_CALENDAR` **off**. So the tide file is **not** a
build-once asset like the grid. Every cycle starts on a different day and each needs
its own `croco_frc.nc`, generated at that cycle's start date — exactly parallel to
`make_ini` and `make_bry`, which also regenerate per cycle.

!!! important
    **The tide file carries a date.** Build it for the wrong day and every wave is out of phase. The driver handles this automatically, running the tide generation at each cycle's spin-up start date. If you generate a tide file by hand, the `--run_date` you pass *is* the phase reference.

!!! note
    **`TIDERAMP`.** The sub-options block also defines `TIDERAMP`, which ramps the tidal forcing up over the first day rather than switching it on at full strength. That avoids a shock at step zero, when the initial condition carries no tidal signal at all. Leave it defined.