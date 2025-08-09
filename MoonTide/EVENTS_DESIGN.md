### MoonTide Event Design

“CROM does not guide your hand. He turns the sky, and the land answers. Learn the rhythm or be broken by it.”

This document explains the event concept and design behind MoonTide. It gives just enough to align operators and moderators, without spoiling the mystery for players.

#### Concept – Layers of a Living World
- Continuous scaling: The world shifts smoothly with the real moon’s light. New Moon is calm; Full Moon is merciless. Only a small set of core multipliers follow this curve so it feels organic, not chaotic.
- Phase presets: Eight lunar “moods” (new → waning crescent) add flavor and nudge systems. They don’t fight the curve; they complete the feeling of the night.
- Calendar/omens: Rare nights and seasonal happenings bend rules further (Blood Moon, Solstice, etc.). They stack additively and can carry their own Message of the Day.

Design goals
- Atmosphere and anticipation: players read the sky and plan.
- Fairness by predictability: big nights are signposted, not random.
- Low operator toil: JSON-configurable, testable, reversible.

#### Mechanics (operator view)
- Order of application
  1) Continuous scaling (from `moon_phase.mapping`) for keys like `HarvestAmountMultiplier`, `NPCDamageMultiplier`, `NPCDamageTakenMultiplier`.
  2) Phase preset for the current bucket (e.g., `waxing_gibbous`).
  3) All enabled `events.calendar`, then `events.weather`, then `events.custom`.
- Merging
  - Numeric values: add together.
  - Strings for listed keys (e.g., `ServerMessageOfTheDay`): append with ` <BR> `.
  - Everything else: last value wins.
- Caps: Per-key clamps guard extremes.
- Backups: One backup per run to a rotating backup dir.
- MOTD: Optional global header/footer; event MOTDs append.

---

### Phase Events (8 buckets)
Each phase lists a guiding theme, the mood, systems touched (keys already present in your INI), and the intended effect. Values shown are typical; exact numbers live in `events.json` and can be tuned.

- New Moon – The Calm
  - Mood: safer nights to explore and build; low pressure.
  - Systems: `MaxAggroRange↓`, `NPCMaxSpawnCapMultiplier↓`, `NPCRespawnMultiplier↑`, `PlayerHealthRegenSpeedScale↑`, `PlayerDamageTakenMultiplier↓`.
  - Intent: breathe, travel, craft; not a loot night.

- Waxing Crescent – The Stirring
  - Mood: threats rising, gains growing.
  - Systems: `MaxAggroRange↗`, `NPCMaxSpawnCapMultiplier↗`, `NPCRespawnMultiplier↘`, light stamina friction (`StaminaRegenerationTime↗`, `PlayerStaminaCostSprintMultiplier↗`).
  - Intent: gentle pressure; groups begin to form.

- First Quarter – The Ascent
  - Mood: adventure invites; returns improve.
  - Systems: Same vector as waxing crescent, slightly stronger.
  - Intent: parties roam; dungeons start feeling spicy.

- Waxing Gibbous – The Surge
  - Mood: stronger foes, richer rewards.
  - Systems: `MaxAggroRange↗↗`, `SpawnCap↗`, `Respawn↘`, more stamina tax.
  - Intent: prelude to Full; stock up and commit.

- Full Moon – The Hunt
  - Mood: apex challenge; the land hunts back.
  - Systems: `MaxAggroRange↑`, `SpawnCap↑`, `Respawn↓`, `PlayerDamageTakenMultiplier↑`, `ThrallDamageToNPCsMultiplier↓`.
  - Intent: real risk, real payoff. Duo+ recommended; thralls won’t carry you.

- Waning Gibbous – The Fade
  - Mood: intensity easing; treasure still good.
  - Systems: step values back from Full toward neutral.
  - Intent: decompress without becoming trivial.

- Last Quarter – The Ebb
  - Mood: fortunes balancing.
  - Systems: continue easing stamina/aggro toward New.
  - Intent: travel-heavy nights feel good again.

- Waning Crescent – The Dusk
  - Mood: quiet returns; prepare for the next cycle.
  - Systems: near-New values with a touch of movement.
  - Intent: reset the board; rebuild and plan.

---

### Calendar/Omen Events
These are rarer overlays with clear themes and stronger identity. They stack on top of phase effects.

- Blood Moon – The Reckoning
  - Theme: elite monsters prowl; high reward for the fearless.
  - Systems: `NPCHealthMultiplier↑`, `LootDropMultiplier↑`, `PurgeLevel↑`, `MaxAggroRange↑`, `NPCMaxSpawnCapMultiplier↑`, `NPCRespawnMultiplier↓`, `PlayerDamageTakenMultiplier↑`, `HealthbarVisibilityDistance↑`, `ThrallDamageToNPCsMultiplier↓`.
  - Intent: raids feel alive, elites are dangerous, loot is juicy; not for solo casuals.
  - Trigger: near full moon (weekend bias).

- Solar Flare – The Burning Sky
  - Theme: brutal heat and fatigue.
  - Systems: `PlayerActiveThirstMultiplier↑`, `PlayerIdleThirstMultiplier↓`, `StaminaRegenerationTime↑`, `PlayerStaminaCostSprintMultiplier↑`, `PlayerMovementSpeedScale↓`.
  - Intent: travel and combat become resource games; heat is the enemy.
  - Trigger: seasonal midday windows (summer months).

- Winter Solstice – The Long Night
  - Theme: long, cold nights with lurking danger.
  - Systems: `NightTimeSpeedScale↓`, `DayTimeSpeedScale↑`, `StaminaCostMultiplier↑`, `PlayerActiveHungerMultiplier↑`, `PlayerActiveThirstMultiplier↑`, `StaminaRegenerationTime↑`, `PlayerDamageTakenMultiplier↑`, `HealthbarVisibilityDistance↑`.
  - Intent: push survival kit discipline; lights and teamwork matter.
  - Trigger: date window around solstice nights.

- Storm Season – The Howling Winds
  - Theme: the environment itself fights you.
  - Systems: `BuildingDamageMultiplier↑`, `PlayerSprintSpeedScale↓`, `StaminaOnConsumeRegenPause↑`, `StaminaOnExhaustionRegenPause↑`, `PlayerMovementSpeedScale↓`.
  - Intent: traversal and sieges are messy and slow; storms punish overextension.
  - Trigger: weather stub (placeholder), or seasonal windows.

- Blue Moon – The Forgotten Prophecy
  - Theme: rare augury; progression surges.
  - Systems: `XPTimeOnlineMultiplier↑`, `PlayerXPRateMultiplier↑`, `PlayerXPKillMultiplier↑`, `PlayerXPHarvestMultiplier↑`, `PlayerXPCraftMultiplier↑`.
  - Intent: a few nights a year where progression pops; bring new blood up to speed.
  - Trigger: true blue moon (second full moon in a month) with weekend window.

---

### Balancing Notes (operator cheatsheet)
- Thralls: nerf follower damage on hard nights so they don’t trivialize.
- New players: keep early-phase multipliers gentle; let Crescents be training wheels.
- Purges: don’t stack the harshest purge levels with Full unless it’s an announced challenge weekend.
- Economy: reserve 6x harvest for Full/rare omens; 3–4.5x feels good otherwise.
- Caps: adjust `caps` in `events.json` to fit your audience; leave headroom for special events.

### Testing and Safety
- Dry-run all days: `tests/run_cycle_test.sh` – confirms scaler output each day.
- MOTD test: `tests/test_motd.sh` – ensures event MOTDs exist and append.
- Delta verify: `tests/run_verify_example.sh` – ensures only intended keys change.
- One-shot runner: `tests/run_all_tests.sh` – all of the above with summary.

Operate with a light touch. Nudge, don’t jerk. Let players feel the sky turning—and let them tell the stories. CROM will be listening.


