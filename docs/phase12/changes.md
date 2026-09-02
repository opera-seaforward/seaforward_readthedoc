The chapters so far build and prove the system with a **cold start**: each run's initial
condition is interpolated fresh from the global ocean model by `make_ini`. That is
correct for a first build and for isolated experiments. Moving to an **operational**
service changes one thing at the heart of the architecture:

!!! note
    When the forecast runs operationally, the initial condition must come from the **previous run's restart** (`croco_rst.nc`), not from a fresh interpolation of the global model.

That is the **restart loop** — in the architecture diagram, the arrow running from
*history and restart* back to *model configuration*. It matters for a physical reason.
A restart carries the model's own dynamically adjusted state: its eddies, its fronts,
its spun-up boundary layers. A fresh interpolation from the global product discards all
of that and resets the interior to the coarser global state every cycle. Operationally,
continuity is the point — yesterday's forecast becomes today's starting point, and the
global products enter only at the boundaries while the regional interior evolves under
its own dynamics.

SEA-FORWARD already implements this pattern **within** a cycle. The driver runs a short
**spin-up** initialised from the global analysis, then hands the spin-up's
`croco_rst.nc` to the **forecast** as its initial condition; the forecast never
cold-starts. Full operational cycling extends the same handoff **across** cycles —
today's restart seeds tomorrow's run — which is a change to *which restart the driver
picks up*, not to any of the machinery. The restart loop is already the backbone of the
system.

In the guide's terms this is the operational pattern: a **service** on the owner's
facility, cycling continuously, producing NetCDF output that downstream tools can read,
with the global products entering only at the boundaries. Moving from the hand-built run
to this cycling service is also a step up the **Operational Readiness Level** — from a
demonstrated capability toward a dependable, scheduled operation.