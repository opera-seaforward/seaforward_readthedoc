# Phase 11 — River Forcing

This chapter shows you, step by step, how to add **river freshwater forcing** to a
CROCO domain. It is written for someone new to CROCO and to Linux, so every command you
need to type is shown, with a note on when to edit a file, when to run a script, and
what each step produces.

!!! note
    **Conventions.** Grey boxes are commands you type into the terminal, then press Enter. `~` is your home directory, for example `/home/yourname`. "Activate the environment" means running `conda activate seaforward` once per terminal session, which makes the right Python and libraries available. Text files are edited with `nano`: save with **Ctrl+O** then Enter, exit with **Ctrl+X**.

![Where this phase sits in the build chain](../img/river_discharges.png)

*The rivers boxes are highlighted: the discharge data comes in with the other forcing
downloads, and the runoff file is built alongside the surface, initial and boundary
conditions.*