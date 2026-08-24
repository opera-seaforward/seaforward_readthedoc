There are two routes. They produce the identical result:

- **Route A (scripts)** — run the numbered `install/` scripts. Fast, and it's
  what most people use.
- **Route B (by hand)** — type each library's `configure` / `make` / `make
  install` yourself. Slower, but you see exactly what happens; use it to learn,
  or if a script fails and you want to debug a single library.

Both routes install into `${SEA_FORWARD_ROOT}/opt_seq`. Pick one.

#### Choose how many processors to compile with

Compiling is faster if `make` uses several CPU cores at once. That number is
passed to `make` as `-j <N>`, and we store it in a variable called **`NJOBS`**.
Choosing it well matters, so do it deliberately:

**First, see how many cores your machine has:**

```bash
nproc                      # prints the number of CPU cores available
```

**Then pick `NJOBS`.** The safe rule is the **smaller of your core count and
(RAM in GB ÷ 2)** — because each parallel compile job needs roughly 2 GB of RAM.
On a machine with many cores but modest RAM, RAM is the real limit:

- 8-core / 16 GB → `NJOBS=8`  (min(8, 8))
- 8-core / 8 GB  → `NJOBS=4`  (min(8, 4))
- 22-core / 15 GB → `NJOBS=7`  (min(22, 7) — RAM caps it, not cores)
- 2-core / low RAM → `NJOBS=2`

Check your RAM alongside cores:

```bash
nproc                                              # cores
awk '/MemTotal/{printf "%.0f GB\n",$2/1048576}' /proc/meminfo   # RAM
```

Set it (along with the root) — this stays in effect for the rest of this
section:

```bash
source ~/seaforward/env.sh
export SEA_FORWARD_ROOT=~/seaforward

# option 1 — pick a number by hand (see the rule above):
export NJOBS=7

# option 2 — let the rule choose for you: min(cores, RAM_GB/2), at least 1
# CORES=$(nproc); RAM_GB=$(awk '/MemTotal/{printf "%d",$2/1024/1024}' /proc/meminfo)
# export NJOBS=$(( RAM_GB/2 )); [ $NJOBS -gt $CORES ] && export NJOBS=$CORES; [ $NJOBS -lt 1 ] && export NJOBS=1

echo "will compile with NJOBS=${NJOBS} parallel jobs"
```

!!! note
    **The `install/` scripts do this for you.** If you run the numbered build scripts (Route A), they **auto-pick** `NJOBS = min(cores, RAM_GB/2)` when you haven't set it, and print what they chose — so you can skip setting it. Setting `NJOBS` by hand (above) still works and overrides the auto choice. The manual `make -j ${NJOBS}` commands in Route B need the variable set as shown.

!!! warning
    ⚠️ **`NJOBS` lives only in the current terminal.** If you open a new terminal partway through, re-run the two `export` lines above, or `make -j ${NJOBS}` becomes `make -j` (unbounded jobs) and can exhaust memory. Every build command below uses `-j ${NJOBS}`, so this one variable controls the processor count everywhere.