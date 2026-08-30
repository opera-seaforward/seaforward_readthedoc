ERA5 comes from the **Copernicus Climate Data Store (CDS)** — a different service
from CMEMS, with its own free account and API key. This is a one-time setup.

### 3.1 Create a free CDS account

Go to [the CDS](https://cds.climate.copernicus.eu) and click **Login / register**
(top right). Create an account, confirm via the email they send, and log in.

### 3.2 Get your Personal Access Token

While logged in, open your [profile page](https://cds.climate.copernicus.eu/profile)
and find the **Personal Access Token** section (sometimes under an "API key" or "How
to use the CDS API" heading). It shows two lines:

```
url: https://cds.climate.copernicus.eu/api
key: 12345678-abcd-1234-efgh-1234567890ab
```

The string after `key:` is your token. **Treat it like a password.**

!!! note
    **The 2024–25 CDS change.** The CDS moved to a new system: the URL is now `https://cds.climate.copernicus.eu/api` (not the old `.../api/v2`), and the key is a single **token** rather than the old `UID:APIKEY` colon form. A tutorial showing the two-part key is outdated — use the single token from your profile.

### 3.3 Create the `~/.cdsapirc` file

The `cdsapi` library reads this automatically, so no download needs extra flags:

```bash
nano ~/.cdsapirc
```

Paste **exactly** the two lines from your profile, with your own token:

```
url: https://cds.climate.copernicus.eu/api
key: 12345678-abcd-1234-efgh-1234567890ab
```

Save (`Ctrl-O`, Enter), exit (`Ctrl-X`), then lock the permissions — it holds a
secret:

```bash
chmod 600 ~/.cdsapirc
```

### 3.4 Check the client is installed

The `seaforward` environment already has `cdsapi`. If it's missing:

```bash
pip install "cdsapi>=0.7.2"      # 0.7.2+ is required by the new CDS system
```

### 3.5 Accept the ERA5 licence

You must accept the dataset's terms once from the website, or downloads fail with a
licence error. Open the ERA5 single-levels dataset:

**<https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels?tab=download>**

Scroll to the bottom, and under **Terms of use** click **Accept**. This is remembered
for your account.

### 3.6 Verify

```bash
python -c "import cdsapi; print('cdsapi OK')"
ls -la ~/.cdsapirc && echo ".cdsapirc present"
python - << 'EOF'
import cdsapi
cdsapi.Client()          # reads ~/.cdsapirc; errors here mean bad url or key
print("CDS client initialised OK")
EOF
```

!!! check
    All three succeed: `cdsapi OK`, the `.cdsapirc` listing, and `CDS client initialised OK`.

!!! warning
    **An *authentication* error when downloading** means `.cdsapirc` is missing or wrong — redo 3.2 and 3.3, checking the token copied cleanly and the URL has no `/v2`. **A *licence* error** despite a working key means you skipped 3.5.