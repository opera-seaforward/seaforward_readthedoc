# forecast/install_validation_crontab.sh (Schedule The Batch)

Installs (or updates) one cron entry that runs `validate_all_cycles.sh` on
a schedule, so new cycles get validated automatically without anyone
running the script by hand. Idempotent — re-running it replaces the
previous SEA-FORWARD-managed entry rather than adding a duplicate (a
marker comment tags the managed lines so any other cron jobs you have are
left untouched), and wraps the command in `flock` so a slow validation run
can never overlap with the next scheduled one.

```bash
cd forecast
./install_validation_crontab.sh                              # daily at 06:00 UTC
./install_validation_crontab.sh --schedule "0 */6 * * *"     # every 6 hours
./install_validation_crontab.sh --region Canary_12            # passed through to validate_all_cycles.sh
./install_validation_crontab.sh --remove                      # uninstall
crontab -l                                                     # verify
```
