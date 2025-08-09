### MoonTide – Conan Exiles Moon-Driven Server Tuning

“Listen, exile. CROM does not coddle. The moon turns, the world hardens, and you either sharpen your blade or become bones under the sand.”

MoonTide bends the Exiled Lands to the turning of the sky. As the moon waxes and wanes, the land shifts: harvest swells, beasts grow cruel, stamina thins, and rewards tempt fools into the dark. There are nights of calm. There are nights of reckoning. CROM does not explain; he only judges.

#### Features
- Continuous scaling (New→Full) using min/max ranges per INI key with optional gamma curve
- Phase presets (8 buckets: new→waning crescent)
- Manual events with triggers (astronomical, seasonal/date windows; weather stub)
- Additive merging across events; per-key caps; configurable backups with rotation
- Windows pre-start wrapper; Linux systemd ExecStartPre compatible

#### Files
- `conan_moon_tuner.py`: main script
- `events.json`: configuration (edit this)
- `events.sample.json`: starter template
- `start_conan_with_moontide.bat`: Windows wrapper (runs tuner only)

#### Quick run
```bash
python3 /absolute/path/MoonTide/conan_moon_tuner.py \
  --ini-path /absolute/path/to/ConanSandbox/Saved/Config/LinuxServer/ServerSettings.ini \
  --event-file /absolute/path/MoonTide/events.json
```
Dry run:
```bash
python3 /absolute/path/MoonTide/conan_moon_tuner.py --ini-path /path/to/ServerSettings.ini --event-file /absolute/path/MoonTide/events.json --dry-run
```

#### Windows wrapper
Edit paths in `start_conan_with_moontide.bat`. Call it before starting the server:
```bat
start_conan_with_moontide.bat
REM then start your server in your own script
```

#### Linux systemd (ExecStartPre)
Add to your unit or an override:
```
[Service]
ExecStartPre=/usr/bin/python3 /absolute/path/MoonTide/conan_moon_tuner.py --ini-path /abs/path/ConanSandbox/Saved/Config/LinuxServer/ServerSettings.ini --event-file /absolute/path/MoonTide/events.json --no-restart
```

#### Config (`events.json`)
- Event concept (CROM will not repeat himself):
  - Phases: eight moon buckets. Their flavor alters the world—subtle at first, savage at full.
  - Calendar: rare omens and seasons. Some nights drag on, some storms bite harder.
  - Weather: when the sky howls, so does the land. (You’ll know when it’s time.)
  - Custom: if you insist on meddling, do it here. CROM will not save you from your own events.
- `moon_phase`: continuous scaling
  - `enabled`: true/false
  - `gamma`: curve shaping (1.0 linear; <1 early boost; >1 delayed)
  - `mapping`: `{ INI_KEY: {"min": x, "max": y } }` (e.g., `HarvestAmountMultiplier`, `NPCDamageMultiplier`, `NPCDamageTakenMultiplier`)
- `events.phases`: 8 day-bucket presets (leave keys empty to let continuous scaling drive them)
- `events.calendar[]`: calendar/date/astronomical events
- `events.weather[]`: weather-driven events (currently stubbed)
- `events.custom[]`: additional active events with no trigger
  - `trigger` types (for `calendar` and `weather`):
    - `astronomical`: `full_moon` (optional `nearest_weekend`, `window_hours`), `blue_moon` (with `activate_window`)
    - `seasonal_window`: `months: [..]`, optional `daily_window: [HH:MM, HH:MM]`
    - `date_window`: `start: MM-DD`, `end: MM-DD`, optional `night_window`
    - `weather`: stubbed (inactive)
  - `settings`: INI key/value pairs (numeric values add across events)
- `insert_missing_keys`: false to only change keys that already exist in INI
- `caps`: per-key `{min,max}` clamps applied after merging
- `backup`: `{ dir, keep, one_backup_per_run }` (defaults to `<ini_dir>/backups`, keep 10)
- `restart`: optional command (avoid when using ExecStartPre or wrapper)

#### Behavior and precedence
1) Continuous scaling applies first (if enabled)
2) Active phase preset is gathered (by detailed bucket or broad phase fallback)
3) All enabled manual events are gathered
4) Events are merged additively for numeric keys; non-numeric last-wins
5) Caps clamp results; only one backup per run
6) Writes only if values change; unknown keys skipped unless `insert_missing_keys=true`

#### Restore backup
Backups are saved as `ServerSettings.ini.bak.YYYYMMDD-HHMMSS` in the backup dir. To restore, stop server, copy a backup over `ServerSettings.ini`, start server.


