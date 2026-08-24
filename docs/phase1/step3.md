**Conda** installs and isolates Python libraries so they don't clash with your
system. We use it for the download/pre-processing tools.

Download and install Miniconda:

```bash
cd ~
wget -c https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
```

Accept the licence, keep the default location (`~/miniconda3`), and when it asks
whether to initialise, answer **yes**. Then close and reopen the terminal (or
`source ~/.bashrc`). Your prompt should now start with `(base)`.

Confirm:

```bash
conda --version
```