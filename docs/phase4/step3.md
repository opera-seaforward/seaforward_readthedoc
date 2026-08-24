GFS comes from the **Copernicus Climate Data Store (CDS)** — a different service
from CMEMS, with its own free account and API key. This is a one-time setup.
Here's the whole thing, step by step.

### 3.1 Create a free CDS account

1. Go to [Copernicus](https://cds.climate.copernicus.eu) and click **Login / register**
   (top right). Create an account (email + password), then confirm via the email
   they send and log in.

### 3.2 Get your Personal Access Token

2. While logged in, open your [profile page](https://cds.climate.copernicus.eu/profile)
3. Find the section **"Personal Access Token"** (sometimes shown under an "API
   key" / "How to use the CDS API" heading). It shows two lines you'll need —
   something like:
   ```
   url: https://cds.climate.copernicus.eu/api
   key: 12345678-abcd-1234-efgh-1234567890ab
   ```
   The long string after `key:` is your token. **Treat it like a password** — keep
   it secret.

!!! note
    **The 2024–25 CDS change:** the CDS moved to a new system. The URL is now `https://cds.climate.copernicus.eu/api` (not the old `.../api/v2`), and the key is a single **token** (no `UID:APIKEY` colon form). If a tutorial shows the old two-part key with a colon, it's outdated — use the single-token form from your profile.

### 3.3 Create the `~/.cdsapirc` file

4. Create the credentials file in your home directory (the `cdsapi` library reads
   it automatically):

```bash
nano ~/.cdsapirc
```

Paste **exactly** the two lines from your profile (with *your* token):

```
url: https://cds.climate.copernicus.eu/api
key: 12345678-abcd-1234-efgh-1234567890ab
```

**What:** `url` is the CDS API endpoint; `key` is your personal token. **Why
here:** `cdsapi.Client()` looks for `~/.cdsapirc` by default, so every GFS
download finds your credentials with no extra flags.

Save (`Ctrl-O`, Enter), exit (`Ctrl-X`). Lock the permissions (it holds a secret):

```bash
chmod 600 ~/.cdsapirc
```

### 3.4 Install the client (if not already)

The `seaforward` conda env should already have `cdsapi`. If not:

```bash
pip install "cdsapi>=0.7.2"      # 0.7.2+ needed for the new CDS system
```

### 3.5 Accept the GFS licence (one-time, per dataset)

5. You **must** accept the dataset's terms once, from the website, or downloads
   fail with a licence error. Open the GFS single-levels dataset:
   **https://cds.climate.copernicus.eu/datasets/reanalysis-GFS-single-levels**
   → go to the **Download** tab → scroll to the bottom → under **Terms of use**,
   click **Accept**. (Do this once; it's remembered for your account.)

### 3.6 Verify it's all set

```bash
python -c "import cdsapi; print('cdsapi OK')"
ls -la ~/.cdsapirc && echo ".cdsapirc present"
python - << 'EOF'
import cdsapi
cdsapi.Client()          # reads ~/.cdsapirc; errors here mean bad url/key
print("CDS client initialised OK")
EOF
```

!!! check
    ✅ All three should succeed: `cdsapi OK`, the `.cdsapirc` listing, and `CDS client initialised OK`.

!!! warning
    ⚠️ **If `.cdsapirc` is missing or wrong** you'll get an *authentication* error when downloading — redo 3.2–3.3 (token copied correctly, new URL form). **If you get a *licence* error** for GFS despite the key working, you skipped 3.5 — accept the terms on the dataset page and retry.