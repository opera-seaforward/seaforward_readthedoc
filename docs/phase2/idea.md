## The idea behind the whole thing

A regional ocean model **takes a global ocean and weather product and adds fine
detail over your region**. You build it in two phases:

**Phase A — prepare the data:** make a grid, decide its boundaries, download the
global ocean and weather, and turn them into the model's starting state, edge
values, and surface forcing.

**Phase B — set up and run the model:** tell CROCO about your grid and physics
(by editing four text files), compile it into a program, and run it.

Everything you edit by hand is *configuration* — text that describes your region
to the model. Understanding that configuration is the whole point.
