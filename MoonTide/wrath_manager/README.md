### MoonTide – Conan Exiles Moon-Driven Server Tuning

“Listen, exile. CROM does not coddle. The moon turns, the world hardens, and you either sharpen your blade or become bones under the sand.”

MoonTide bends the Exiled Lands to the turning of the sky. As the moon waxes and wanes, the land shifts: harvest swells, beasts grow cruel, stamina thins, and rewards tempt fools into the dark. There are nights of calm. There are nights of reckoning. CROM does not explain; he only judges.

See the event concept and detailed breakdown in `MoonTide/EVENTS_DESIGN.md`.

#### Features
- Continuous scaling (New→Full) with per-key min/max and optional gamma
- Phase presets (8 buckets) layered on top of scaling
- Calendar/omen events with triggers (astronomical, seasonal/date windows; weather stub)
- Additive merge (numbers add; configured strings append) with per‑key caps
- Global MOTD header/footer and per‑event MOTDs (appended with `<BR>`)
- One‑backup‑per‑run with rotation; idempotent writes
- Test suite (cycle, MOTD, delta‑verify); Windows wrapper; Linux ExecStartPre

#### Files
- `wrath_manager.py`: main script
- `events.json`: configuration (edit this)
- `events.sample.json`: starter template
- `EVENTS_DESIGN.md`: event concept and detailed breakdown
- `start_wrath_manager.bat`: Windows wrapper (runs tuner only)
- `tests/`: cycle, MOTD, and verification runners

#### Quick run
```bash
python3 /absolute/path/MoonTide/wrath_manager/wrath_manager.py \
  --ini-path /absolute/path/to/ConanSandbox/Saved/Config/LinuxServer/ServerSettings.ini \
  --event-file /absolute/path/MoonTide/wrath_manager/events.json
```
Dry run:
```bash
python3 /absolute/path/MoonTide/wrath_manager/wrath_manager.py --ini-path /path/to/ServerSettings.ini --event-file /absolute/path/MoonTide/wrath_manager/events.json --dry-run
```

Discord posting (no secret in source):
```bash
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."  # do NOT commit
python3 /absolute/path/MoonTide/wrath_manager/wrath_manager.py \
  --ini-path /path/to/ServerSettings.ini \
  --event-file /absolute/path/MoonTide/wrath_manager/events.json \
  --discord-post
```

#### Windows wrapper
Legacy‑style args supported. Call it before starting the server (wrapper does not start the server):
```bat
REM legacy‑compatible example (MOTD arg ignored)
start_wrath_manager.bat -f "C:\ExiledLands\DedicatedServerLauncher\ConanExilesDedicatedServer\ConanSandbox\Saved\Config\WindowsServer\ServerSettings.ini" -m "C:\path\MOTD.txt"

REM specify events file and pass flags through
start_wrath_manager.bat -f "C:\path\ServerSettings.ini" -e "C:\path\events.json"
```

#### Linux systemd (ExecStartPre)
Add to your unit or an override:
```
[Service]
ExecStartPre=/usr/bin/python3 /absolute/path/MoonTide/wrath_manager/wrath_manager.py --ini-path /abs/path/ConanSandbox/Saved/Config/LinuxServer/ServerSettings.ini --event-file /absolute/path/MoonTide/wrath_manager/events.json
```

#### Config (`events.json`)
- `moon_phase`: continuous scaling
  - `enabled`: true/false
  - `gamma`: curve shaping (1.0 linear; <1 early boost; >1 delayed)
  - `mapping`: `{ INI_KEY: {"min": x, "max": y } }` (explicit INI keys supported)
- `events.phases`: 8 day‑bucket presets (leave keys empty to let scaling drive them)
- `events.calendar[]`, `events.weather[]`, `events.custom[]`: additional events and triggers
  - triggers: `astronomical` (full_moon/blue_moon), `seasonal_window`, `date_window`, `weather` (stub)
  - `settings`: INI key/value pairs (numbers add; strings append if configured)
- `string_append_keys`: e.g., `["ServerMessageOfTheDay"]`
- `string_append_joiner`: default ` <BR> `
- `motd`: optional `{ header, footer, always_include }`
- `insert_missing_keys`: default false (only update existing INI keys)
- `caps`: per‑key `{min,max}` clamps after merging
- `backup`: `{ dir, keep, one_backup_per_run }` (defaults to `<ini_dir>/backups`, keep 10)
- `restart`: optional command (avoid when using ExecStartPre or wrapper)

#### Behavior and precedence
1) Continuous scaling applies first (if enabled)
2) Active phase preset is gathered (by detailed bucket or broad phase fallback)
3) All enabled events: `calendar` → `weather` → `custom`
4) Merge: numbers add; strings append (if configured); otherwise last‑wins
5) Caps clamp results; one backup per run; idempotent writes
6) Unknown keys skipped unless `insert_missing_keys=true`

#### Restore backup
Backups are saved as `ServerSettings.ini.bak.YYYYMMDD-HHMMSS` in the backup dir. To restore, stop server, copy a backup over `ServerSettings.ini`, start server.

#### Tests (local)
- One‑shot: `tests/run_all_tests.sh [INI] [events.json]`
- Cycle preview: `tests/run_cycle_test.sh [INI] [events.json]`
- MOTD checks: `tests/test_motd.sh [INI] [events.json]`
- Delta verify example: `tests/run_verify_example.sh`

#### Maintainer tip
- When you update `events.json`, update `EVENTS_DESIGN.md` in the same commit. A guard script exists at `scripts/guard_events_doc_sync.sh` you can run in CI to enforce this.


