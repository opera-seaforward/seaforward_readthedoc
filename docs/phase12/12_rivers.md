# River (Runoff) Forcing in SEA-FORWARD — A Complete Walkthrough

This chapter shows you, step by step, how to add **river freshwater forcing** to a
CROCO domain. It is written for someone new to CROCO and to Linux/WSL: every command
you need to type is shown, and we explain *when* to edit a file with `nano`, *when* to
run a Python script, and what each step produces.

!!! important
    **Before you start** — a few conventions:
    - Lines in grey boxes are **commands you type in the terminal**, then press Enter.
    - `~` means your home directory (e.g. `/home/yourname`).
    - When we say "activate the environment", we mean:
    ```bash
    conda activate seaforward
    ```
    This makes the right Python and libraries available. Do it once per terminal session.
    To **edit a text file**, we use `nano` (a simple terminal editor). Inside nano:
    save with **Ctrl+O** then **Enter**, and exit with **Ctrl+X**.

The figure below highlights where this phase sit on in the SEA-FORWARD entire build chain
![Phase 12](../img/river_discharges.png)