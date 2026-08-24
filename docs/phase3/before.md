The initial ocean state comes from a global model at coarser resolution. Dropped
straight onto your fine grid it is slightly out of balance and would generate
spurious waves. Running the **2-day spin-up** first — from the **analysis** — lets
the fine model adjust, so the **5-day forecast** starts from a self-consistent
state. That's why the forecast is initialized from the spin-up's end, while its
boundaries switch to the **forecast** part of the product for the future window.