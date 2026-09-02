- **A boundary can be 11% ocean and still be the right one to open.** The rule of thumb
  ("mostly land → close") is a starting point, not a verdict. Ask what those cells
  carry.
- **The displacement loop's behaviour depends on coastline orientation.** A coast
  parallel to your edge is harmless; a diagonal one marches your box into the
  continent.
- **Resolution in km is latitude-dependent.** The same 1/36° grid is 3.06 km at the
  equator and 2.5 km here.
- **`rfact` is where you spend your stability budget** on a steep shelf. The parent's
  `rx1 = 14.84` at 1/12° is the warning, and the child was given 0.15 on the reasoning
  that refinement thins the layers over the same slope. It came out at 13.42 — *lower*
  than the parent. The lever works; the prediction did not.
- **Fast currents were not the problem.** `dt = 300` handled 2 m/s without complaint.
  The worry was misplaced — the bathymetry is the risk here, not the velocity.
- **Comparing a child to its parent means comparing over the same water.** The parent's
  RMSE across its whole domain is diluted by easy deep ocean the child never sees.
  Subset the parent to the child's footprint or the number means nothing — and it will
  flatter whichever grid has more open ocean in it.
- **RMSE against the forcing product has a ceiling built in.** Mercator is the same
  resolution as the parent, so structure the child resolves at 2.5 km is invisible to
  the reference and counts as error. The comparison is worth doing — it catches real
  breakage — but it cannot tell you the child is *good*, only that it isn't obviously
  broken.