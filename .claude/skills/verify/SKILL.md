---
name: verify
description: Verify traffic-collector end to end against the dev SCAN simulator and dev MongoDB
---

# Verify traffic-collector (cold-start recipe)

Prereqs: `make dev-up dev-sim-up`; `services/traffic-collector/config.yml` copied from `config.yml.example`.

1. Never use the real `scan_backup` DB. Seed `scan_backup_verify` (via host venv `services/traffic-collector/.venv`, `localhost:$MONGO_HOST_PORT`) with the `interfaces` docs copied from `scan_backup`; break some `scan_url` (append `.nope`) to probe failures and layer cuts.
2. Real CLI: `docker compose --env-file .env.development -f docker-compose.dev.yml run --rm -T -e MONGO_DATABASE=scan_backup_verify traffic-collector [--force]` (in zsh wrap in a function; a variable holding the command does not word-split).
3. Fixtures hold 1191 `.log` (one per active interface) with data up to the generation day. The CLI targets yesterday, so the real CLI succeeds (exit 0, 1191 stored) only if fixtures were generated today; otherwise run `traffic_collector.cli.execute(force, os.environ, date(...), Path("/logs/verify.log"), sys.stdout, sys.stderr)` in the container with `--entrypoint python ... -` (stdin) and an injected `today`.
4. Check results with pymongo on `traffic_daily` / `traffic_summary_daily`; count nginx lines with `docker logs scan-backup-scan-simulator-dev | wc -l` to prove a rerun makes no SCAN requests.
5. Cleanup: drop `scan_backup_verify` and delete `logs/traffic-collector/verify.log*`.
