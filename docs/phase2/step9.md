`jobcomp` is the build script; it needs to know where CROCO's source code is.
Open it:

```bash
nano jobcomp
```

`Ctrl-W`, type `SOURCE1=`, Enter. You'll find:

```
SOURCE1=../croco/OCEAN
```

Change it to your actual source path:

```
SOURCE1=/home/<you>/seaforward/code/croco/OCEAN
```

Replace `<you>` with your username, or write `${HOME}/seaforward/code/croco/OCEAN`.

**What:** tells the compiler where the model's `.F` source files are. **Why:** the
default `../croco/OCEAN` is a relative path that doesn't exist in your layout.
`jobcomp` finds the NetCDF library automatically via `nf-config` (which points at
`opt_seq` after you sourced `env.sh`), so there are **no NetCDF paths to
hand-edit**.

Save (`Ctrl-O`, Enter), exit (`Ctrl-X`), then confirm:

```bash
grep -n "^SOURCE1=" jobcomp
ls $(grep "^SOURCE1=" jobcomp | cut -d= -f2)/cppdefs.h
```

!!! check
    The path is absolute, and the `ls` finds `cppdefs.h` inside it — proof the path is real, not just plausible.