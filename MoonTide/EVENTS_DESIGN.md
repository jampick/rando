
# MoonTide Event Design

> *“CROM does not hold your hand. He turns the heavens, and the earth answers in blood, frost, and shadow.”*

---

## 🗡️ Core Concept

This server runs **seasonal events synced to the real-world lunar cycle and calendar**.  
The moon you see outside shapes the dangers, resources, and atmosphere inside the game.  
Full moons bring lethal predators and rich rewards. New moons offer safety and breathing space.  
Rare celestial and seasonal events stack on top of the lunar phases to create moments of high stakes and unique opportunities.

---

![Build Status](https://img.shields.io/badge/status-active-green) ![Automation](https://img.shields.io/badge/automation-JSON__driven-blue) ![Spoilers](https://img.shields.io/badge/player%20spoilers-minimal-lightgrey)

---

## Concept: Layers of a Living World

- **Continuous scaling**: The land breathes with the real moon. New Moon is calm. Full Moon is merciless. Core multipliers follow this curve.  
- **Phase presets**: Eight lunar moods from New to Waning Crescent add flavor and pressure.  
- **Calendar and Omens**: Rare nights and seasonal signs twist the rules. They stack with the phase to create bigger danger and better rewards.

**Design goals**
- Atmosphere and anticipation: the sky is your clock  
- Fairness through inevitability: big nights are signposted  
- Low operator toil: JSON driven, testable, reversible

---

## Mechanics: Operator View

**Order of application**
1. Continuous scaling: `moon_phase.mapping` for harvest, damage dealt, damage taken  
2. Phase preset for the current bucket  
3. All enabled events in order: `calendar` → `weather` → `custom`

**Merging rules**
- Numbers: add  
- Strings like `ServerMessageOfTheDay`: append using `<BR>`  
- Everything else: last value wins

**Safety nets**
- Caps per key  
- Rotating backups per run  
- Optional global MOTD header and footer, event MOTDs append

---

## Quick Reference: Phases at a Glance

> Use this strip for planning and moderation

| Phase | Mood | Systems snapshot |
|---|---|---|
| 🌑 New Moon | The land rests | `MaxAggroRange↓`, `NPCMaxSpawnCapMultiplier↓`, `NPCRespawnMultiplier↑`, `PlayerHealthRegenSpeedScale↑`, `PlayerDamageTakenMultiplier↓` |
| 🌒 Waxing Crescent | Distant drums | `MaxAggroRange↗`, `NPCMaxSpawnCapMultiplier↗`, `NPCRespawnMultiplier↘`, `StaminaRegenerationTime↗`, `PlayerStaminaCostSprintMultiplier↗` |
| 🌓 First Quarter | The hunt begins | Same vector as waxing crescent, slightly stronger |
| 🌔 Waxing Gibbous | The land sharpens its teeth | `MaxAggroRange↗↗`, `NPCMaxSpawnCapMultiplier↗↗`, `NPCRespawnMultiplier↘`, `StaminaRegenerationTime↑`, `PlayerStaminaCostSprintMultiplier↑` |
| 🌕 Full Moon | Apex predators rule | `MaxAggroRange↑`, `NPCMaxSpawnCapMultiplier↑`, `NPCRespawnMultiplier↓`, `PlayerDamageTakenMultiplier↑`, `ThrallDamageToNPCsMultiplier↓` |
| 🌖 Waning Gibbous | The storm passes | Step values back from Full toward neutral |
| 🌗 Last Quarter | The tide falls | Ease stamina and aggro toward New |
| 🌘 Waning Crescent | Quiet returns | Near-New calm with slight movement |

---

## Phase Details

<details>
<summary>🌑 New Moon - The Calm</summary>
**Mood**: the land rests  
**Systems**: `MaxAggroRange↓`, `NPCMaxSpawnCapMultiplier↓`, `NPCRespawnMultiplier↑`, `PlayerHealthRegenSpeedScale↑`, `PlayerDamageTakenMultiplier↓`  
**Intent**: explore, build, breathe
</details>

<details>
<summary>🌒 Waxing Crescent - The Stirring</summary>
**Mood**: distant drums  
**Systems**: `MaxAggroRange↗`, `NPCMaxSpawnCapMultiplier↗`, `NPCRespawnMultiplier↘`, `StaminaRegenerationTime↗`, `PlayerStaminaCostSprintMultiplier↗`  
**Intent**: pressure builds
</details>

<details>
<summary>🌓 First Quarter - The Ascent</summary>
**Mood**: the hunt begins  
**Systems**: same vector as waxing crescent, slightly stronger  
**Intent**: adventure invites and rewards
</details>

<details>
<summary>🌔 Waxing Gibbous - The Surge</summary>
**Mood**: the land sharpens its teeth  
**Systems**: `MaxAggroRange↗↗`, `NPCMaxSpawnCapMultiplier↗↗`, `NPCRespawnMultiplier↘`, `StaminaRegenerationTime↑`, `PlayerStaminaCostSprintMultiplier↑`  
**Intent**: stock up, commit
</details>

<details>
<summary>🌕 Full Moon - The Hunt</summary>
**Mood**: apex predators rule the night  
**Systems**: `MaxAggroRange↑`, `NPCMaxSpawnCapMultiplier↑`, `NPCRespawnMultiplier↓`, `PlayerDamageTakenMultiplier↑`, `ThrallDamageToNPCsMultiplier↓`  
**Intent**: risk everything, gain everything
</details>

<details>
<summary>🌖 Waning Gibbous - The Fade</summary>
**Mood**: the storm passes  
**Systems**: step values back from Full toward neutral  
**Intent**: keep rewards high, lower the grind
</details>

<details>
<summary>🌗 Last Quarter - The Ebb</summary>
**Mood**: the tide falls  
**Systems**: ease stamina and aggro toward New  
**Intent**: travel and trade flourish
</details>

<details>
<summary>🌘 Waning Crescent - The Dusk</summary>
**Mood**: quiet returns  
**Systems**: near-New calm with slight movement  
**Intent**: reset the board
</details>

---

## Calendar and Omen Events

<details>
<summary>🩸 Blood Moon - The Reckoning</summary>
**Theme**: the strong hunt the strong  
**Systems**: `NPCHealthMultiplier↑`, `LootDropMultiplier↑`, `PurgeLevel↑`, `MaxAggroRange↑`, `NPCMaxSpawnCapMultiplier↑`, `NPCRespawnMultiplier↓`, `PlayerDamageTakenMultiplier↑`, `HealthbarVisibilityDistance↑`, `ThrallDamageToNPCsMultiplier↓`  
**Intent**: glory or death  
**Trigger**: near full moon with weekend bias
</details>

<details>
<summary>🔥 Solar Flare - The Burning Sky</summary>
**Theme**: heat punishes the unprepared  
**Systems**: `PlayerActiveThirstMultiplier↑`, `PlayerIdleThirstMultiplier↓`, `StaminaRegenerationTime↑`, `PlayerStaminaCostSprintMultiplier↑`, `PlayerMovementSpeedScale↓`  
**Intent**: the sun itself is the enemy  
**Trigger**: seasonal midday windows in summer
</details>

<details>
<summary>❄️ Winter Solstice - The Long Night</summary>
**Theme**: cold and darkness close in  
**Systems**: `NightTimeSpeedScale↓`, `DayTimeSpeedScale↑`, `StaminaCostMultiplier↑`, `PlayerActiveHungerMultiplier↑`, `PlayerActiveThirstMultiplier↑`, `StaminaRegenerationTime↑`, `PlayerDamageTakenMultiplier↑`, `HealthbarVisibilityDistance↑`  
**Intent**: test discipline and preparation  
**Trigger**: solstice date window
</details>

<details>
<summary>🌪️ Storm Season - The Howling Winds</summary>
**Theme**: the sky strikes  
**Systems**: `BuildingDamageMultiplier↑`, `PlayerSprintSpeedScale↓`, `StaminaOnConsumeRegenPause↑`, `StaminaOnExhaustionRegenPause↑`, `PlayerMovementSpeedScale↓`  
**Intent**: turn the map into a siege  
**Trigger**: weather system or seasonal schedule
</details>

<details>
<summary>🔵 Blue Moon - The Forgotten Prophecy</summary>
**Theme**: a rare surge in power  
**Systems**: `XPTimeOnlineMultiplier↑`, `PlayerXPRateMultiplier↑`, `PlayerXPKillMultiplier↑`, `PlayerXPHarvestMultiplier↑`, `PlayerXPCraftMultiplier↑`  
**Intent**: let new blood rise  
**Trigger**: true blue moon with weekend window
</details>

---

## 🛡️ Operator Cheatsheet

- Thralls: reduce follower damage on hard nights so they do not trivialize  
- New players: crescents should feel safe as training wheels  
- Purges: only stack the harshest purge levels with Full during announced weekends  
- Economy: save 6x harvest for Full and rare omens, keep most nights between 3x and 4.5x

---

## 🧪 Testing and Safety

~~~bash
tests/run_cycle_test.sh       # preview daily scalers
tests/test_motd.sh            # verify MOTD append behavior
tests/run_verify_example.sh   # confirm only intended keys change
tests/run_all_tests.sh        # full battery, single command
~~~

**Backups**: one per run, rotating  
**Caps**: tune per audience in `events.json`  
**MOTD**: optional global header and footer, events append

---
