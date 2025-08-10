
# MoonTide Event Design

> *"CROM does not hold your hand. He turns the heavens, and the earth answers in blood, frost, and shadow."*

**Part of the Rando Server Management Suite**

---

## 🗡️ Core Concept

This server runs **seasonal events synced to the real-world lunar cycle and calendar**.  
The moon you see outside shapes the dangers, resources, and atmosphere inside the game.  
Full moons bring lethal predators and rich rewards. New moons offer safety and breathing space.  
Rare celestial and seasonal events stack on top of the lunar phases to create moments of high stakes and unique opportunities.

---

![Build Status](https://img.shields.io/badge/status-active-green) ![Automation](https://img.shields.io/badge/automation-JSON__driven-blue) ![Spoilers](https://img.shields.io/badge/player%20spoilers-minimal-lightgrey) ![Integration](https://img.shields.io/badge/integration-Grim__Observer-orange)

---

## 🌙 Concept: Layers of a Living World

- **Continuous scaling**: The land breathes with the real moon. New Moon is calm. Full Moon is merciless. Core multipliers follow this curve.  
- **Phase presets**: Eight lunar moods from New to Waning Crescent add flavor and pressure.  
- **Calendar and Omens**: Rare nights and seasonal signs twist the rules. They stack with the phase to create bigger danger and better rewards.

**Design goals**
- **Atmosphere and anticipation**: the sky is your clock  
- **Fairness through inevitability**: big nights are signposted  
- **Low operator toil**: JSON driven, testable, reversible
- **Integration ready**: coordinates with Grim Observer for comprehensive server management

---

## ⚙️ Mechanics: Operator View

**Order of application**
1. **Continuous scaling**: `moon_phase.mapping` for harvest, damage dealt, damage taken  
2. **Phase preset** for the current bucket  
3. **All enabled events** in order: `calendar` → `weather` → `custom`

**Merging rules**
- **Numbers**: add  
- **Strings** like `ServerMessageOfTheDay`: append using `<BR>`  
- **Everything else**: last value wins

**Safety nets**
- **Caps per key**  
- **Rotating backups** per run  
- **Optional global MOTD** header and footer, event MOTDs append
- **Integration validation** with monitoring systems

---

## 📊 Quick Reference: Phases at a Glance

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

## 🌑 Phase Details

<details>
<summary>🌑 New Moon - The Calm</summary>
**Mood**: the land rests  
**Systems**: `MaxAggroRange↓`, `NPCMaxSpawnCapMultiplier↓`, `NPCRespawnMultiplier↑`, `PlayerHealthRegenSpeedScale↑`, `PlayerDamageTakenMultiplier↓`  
**Intent**: explore, build, breathe
**Integration**: Coordinates with Grim Observer for low-activity notifications
</details>

<details>
<summary>🌒 Waxing Crescent - The Stirring</summary>
**Mood**: distant drums  
**Systems**: `MaxAggroRange↗`, `NPCMaxSpawnCapMultiplier↗`, `NPCRespawnMultiplier↘`, `StaminaRegenerationTime↗`, `PlayerStaminaCostSprintMultiplier↗`  
**Intent**: pressure builds
**Integration**: Player activity monitoring detects increased engagement
</details>

<details>
<summary>🌓 First Quarter - The Ascent</summary>
**Mood**: the hunt begins  
**Systems**: same vector as waxing crescent, slightly stronger  
**Intent**: adventure invites and rewards
**Integration**: Discord notifications highlight increased rewards
</details>

<details>
<summary>🌔 Waxing Gibbous - The Surge</summary>
**Mood**: the land sharpens its teeth  
**Systems**: `MaxAggroRange↗↗`, `NPCMaxSpawnCapMultiplier↗↗`, `NPCRespawnMultiplier↘`, `StaminaRegenerationTime↑`, `PlayerStaminaCostSprintMultiplier↑`  
**Intent**: stock up, commit
**Integration**: Player tracking shows preparation behavior
</details>

<details>
<summary>🌕 Full Moon - The Hunt</summary>
**Mood**: apex predators rule the night  
**Systems**: `MaxAggroRange↑`, `NPCMaxSpawnCapMultiplier↑`, `NPCRespawnMultiplier↓`, `PlayerDamageTakenMultiplier↑`, `ThrallDamageToNPCsMultiplier↓`  
**Intent**: risk everything, gain everything
**Integration**: High-activity monitoring and special event coordination
</details>

<details>
<summary>🌖 Waning Gibbous - The Fade</summary>
**Mood**: the storm passes  
**Systems**: step values back from Full toward neutral  
**Intent**: keep rewards high, lower the grind
**Integration**: Player retention monitoring during transition
</details>

<details>
<summary>🌗 Last Quarter - The Ebb</summary>
**Mood**: the tide falls  
**Systems**: ease stamina and aggro toward New  
**Intent**: travel and trade flourish
**Integration**: Social activity tracking and community building
</details>

<details>
<summary>🌘 Waning Crescent - The Dusk</summary>
**Mood**: quiet returns  
**Systems**: near-New calm with slight movement  
**Intent**: reset the board
**Integration**: Preparation for next cycle and player onboarding
</details>

---

## 🗓️ Calendar and Omen Events

### Quick Reference: Calendar/Omen at a Glance

| Event | Theme | Trigger | Systems snapshot | Integration | Status |
|---|---|---|---|---|---|
| 🩸 Blood Moon | Elite danger, high reward | Near full moon (weekend bias, ~24h window) | `NPCHealth↑`, `PurgeLevel↑`, `Aggro↑`, `SpawnCap↑`, `Respawn↓`, `PlayerDmgTaken↑`, `HealthbarDist↑`, `ThrallDmgToNPCs↓` | **Grim Observer**: High-activity alerts, player tracking | **DISABLED** |
| 🔥 Solar Flare | Heat and fatigue | Summer months, daily 12:00–14:00 | `ActiveThirst↑`, `IdleThirst↓`, `StaminaRegenTime↑`, `SprintCost↑`, `MoveSpeed↓` | **Grim Observer**: Player behavior monitoring, resource alerts | **NOT CONFIGURED** |
| ❄️ Winter Solstice | Long, cold nights | Dec 20–23, nights 18:00–06:00 | `NightSpeed↓`, `DaySpeed↑`, `StaminaCost↑`, `ActiveHunger↑`, `ActiveThirst↑`, `StaminaRegenTime↑`, `PlayerDmgTaken↑`, `HealthbarDist↑` | **Grim Observer**: Night activity tracking, seasonal notifications | **NOT CONFIGURED** |
| 🌪️ Storm Season | Environmental hazard | Weather trigger (stub) or Sep–Nov seasonal window | `BuildingDmg↑`, `SprintSpeed↓`, `ConsumeRegenPause↑`, `ExhaustRegenPause↑`, `MoveSpeed↓` | **Grim Observer**: Building damage alerts, movement monitoring | **NOT CONFIGURED** |
| 🔵 Blue Moon | Progression surge | Second full moon in month; Fri 18:00–Sun 23:59 | `XPTimeOnline↑(PlayerXPTime↑)`, `XPRate↑`, `XPKill↑`, `XPHarvest↑`, `XPCraft↑` | **Grim Observer**: XP event coordination, player onboarding | **DISABLED** |

---

<details>
<summary>🩸 Blood Moon - The Reckoning</summary>
**Theme**: the strong hunt the strong  
**Systems**: `NPCHealthMultiplier↑`, `PurgeLevel↑`, `MaxAggroRange↑`, `NPCMaxSpawnCapMultiplier↑`, `NPCRespawnMultiplier↓`, `PlayerDamageTakenMultiplier↑`, `HealthbarVisibilityDistance↑`, `ThrallDamageToNPCsMultiplier↓`  
**Intent**: glory or death; raids feel alive, elites are dangerous, loot is juicy  
**Trigger**: near full moon with weekend bias  
**MOTD cue**: "Blood Moon Event: Elite monsters prowl! High risk, high reward."  
**Operator tips**: announce timing; consider purge pacing; expect higher death rates
**Integration**: **Grim Observer** coordinates high-activity notifications and player tracking
**Status**: Currently **DISABLED** in events.json
</details>

<details>
<summary>🔥 Solar Flare - The Burning Sky</summary>
**Theme**: heat punishes the unprepared  
**Systems**: `PlayerActiveThirstMultiplier↑`, `PlayerIdleThirstMultiplier↓`, `StaminaRegenerationTime↑` (e.g., ~4.0 during peak), `PlayerStaminaCostSprintMultiplier↑`, `PlayerMovementSpeedScale↓`  
**Intent**: travel and combat become resource games; the sun is the enemy  
**Trigger**: seasonal midday windows in summer  
**MOTD cue**: "Solar Flare: brutal heat and thirst—seek shade and water."  
**Operator tips**: remind players about water/ice; nudge caravan/supply play; movement/sprint speed merge multiplicatively to avoid additive speed-ups
**Integration**: **Grim Observer** monitors player behavior changes and resource consumption patterns
**Status**: **NOT CONFIGURED** in events.json
</details>

<details>
<summary>❄️ Winter Solstice - The Long Night</summary>
**Theme**: cold and darkness close in  
**Systems**: `NightTimeSpeedScale↓`, `DayTimeSpeedScale↑`, `StaminaCostMultiplier↑`, `PlayerActiveHungerMultiplier↑`, `PlayerActiveThirstMultiplier↑`, `StaminaRegenerationTime↑`, `PlayerDamageTakenMultiplier↑`, `HealthbarVisibilityDistance↑`  
**Intent**: test discipline and preparation; lights and teamwork matter  
**Trigger**: solstice date window  
**MOTD cue**: "Winter Solstice: longer nights and chill winds—bundle up."  
**Operator tips**: consider themed rewards; advise torches, fur gear, campfires
**Integration**: **Grim Observer** tracks night activity patterns and seasonal player behavior
**Status**: **NOT CONFIGURED** in events.json
</details>

<details>
<summary>🌪️ Storm Season - The Howling Winds</summary>
**Theme**: the sky strikes  
**Systems**: `BuildingDamageMultiplier↑`, `PlayerSprintSpeedScale↓`, `StaminaOnConsumeRegenPause↑`, `StaminaOnExhaustionRegenPause↑`, `PlayerMovementSpeedScale↓`  
**Intent**: traversal and sieges are messy and slow; storms punish overextension  
**Trigger**: weather system (stub) or seasonal schedule  
**MOTD cue**: "Storm Season: howling winds batter builds; move carefully."  
**Operator tips**: set clear window; warn builders; expect more rescues
**Integration**: **Grim Observer** monitors building damage events and movement restrictions
**Status**: **NOT CONFIGURED** in events.json
</details>

<details>
<summary>🔵 Blue Moon - The Forgotten Prophecy</summary>
**Theme**: a rare surge in power  
**Systems**: `PlayerXPTimeMultiplier↑`, `PlayerXPRateMultiplier↑`, `PlayerXPKillMultiplier↑`, `PlayerXPHarvestMultiplier↑`, `PlayerXPCraftMultiplier↑`  
**Intent**: a few nights a year where progression pops; bring new blood up to speed  
**Trigger**: true blue moon with weekend window  
**MOTD cue**: "Blue Moon: rare augury—unique loot and power await."  
**Operator tips**: advertise ahead; great for onboarding and catch‑up
**Integration**: **Grim Observer** coordinates XP event notifications and player onboarding tracking
**Status**: Currently **DISABLED** in events.json
</details>

---

## 📝 MOTD Configuration

### Current MOTD System
The MOTD system now includes:
- **Global header/footer**: Always displayed with language support (EN/JP)
- **Event-specific MOTDs**: Appended to the global message during active events
- **Language support**: English and Japanese versions for all messages
- **String joining**: Uses `<BR>` tags for line breaks (Discord-compatible)

### MOTD Structure
```json
"motd": {
  "languages": ["en", "ja"],
  "header": {
    "en": "Crom cares not for your fate.<BR>This is MoonTide. Endure or perish.<BR>Join the warband: discord.gg/g7D3GzVrDt",
    "ja": "クロムはお前の運命に興味はない。<BR>これはムーンタイドだ。耐えよ、さもなくば滅べ。<BR>戦団に参加: discord.gg/g7D3GzVrDt"
  },
  "footer": {
    "en": "Fight. Build. Bleed. Survive the night.",
    "ja": "戦え。築け。血を流せ。夜を生き延びろ。"
  },
  "always_include": true
}
```

---

#### Trigger Reference (events.json)
- **Astronomical**
  - `{"type":"astronomical","event":"full_moon","nearest_weekend":true,"window_hours":24}`
  - `{"type":"astronomical","event":"blue_moon","activate_window":["Fri 18:00","Sun 23:59"],"window_hours":24}`
- **Seasonal window**
  - `{"type":"seasonal_window","months":[6,7,8],"daily_window":["12:00","14:00"]}`
- **Date window**
  - `{"type":"date_window","start":"12-20","end":"12-23","night_window":["18:00","06:00"]}`
- **Weather (stub)**
  - `{"type":"weather","provider":"stub"}`

---

## 🛡️ Operator Cheatsheet

- **Thralls**: reduce follower damage on hard nights so they do not trivialize  
- **New players**: crescents should feel safe as training wheels  
- **Purges**: only stack the harshest purge levels with Full during announced weekends  
- **Economy**: save 6x harvest for Full and rare omens, keep most nights between 3x and 4.5x
- **Integration**: coordinate event announcements with Grim Observer Discord notifications
- **Monitoring**: use player activity data to validate event effectiveness

---

## 🧪 Testing and Safety

```bash
tests/run_cycle_test.sh       # preview daily scalers
tests/test_motd.sh            # verify MOTD append behavior
tests/run_verify_example.sh   # confirm only intended keys change
tests/run_all_tests.sh        # full battery, single command
```

**Backups**: one per run, rotating  
**Caps**: tune per audience in `events.json`  
**MOTD**: optional global header and footer, events append  
**CLI**: `wrath_manager.py` is the entry point
**Integration**: coordinates with Grim Observer for comprehensive server management

---

## 🔗 System Integration

### With Grim Observer
- **Event synchronization**: Moon phase changes trigger monitoring alerts
- **Player tracking**: Activity patterns validate event effectiveness
- **Discord coordination**: Unified notification system for both systems
- **Configuration sharing**: Map-specific settings and secrets

### With External Systems
- **Webhook endpoints**: For custom integrations and monitoring
- **JSON output**: For data processing and analytics
- **Log file monitoring**: For external analysis and validation
- **API endpoints**: For status queries and health checks

---

## 📊 Analytics and Monitoring

### Event Effectiveness
- **Player retention** during different moon phases
- **Activity patterns** correlation with lunar cycles
- **Resource consumption** during special events
- **Community engagement** with seasonal content

### Performance Metrics
- **Configuration change frequency** and impact
- **Event trigger accuracy** and timing
- **Backup rotation efficiency** and storage usage
- **System resource consumption** during peak events

---

## 🔒 Security and Privacy

- **No sensitive data** stored in configuration files
- **Secure backup handling** with proper permissions
- **Input validation** to prevent injection attacks
- **Audit logging** for configuration changes and event triggers
- **Integration security** with monitoring systems

---

## 📚 Documentation and Support

- **Event System**: This file - Comprehensive event design guide
- **Configuration**: Wrath Manager README - Configuration options and examples
- **Integration**: Main project README - System integration guide
- **Monitoring**: Grim Observer README - Real-time monitoring capabilities
- **Testing**: Test suite documentation in each component

---

## 🆘 Support and Troubleshooting

For issues and questions:
1. Check the troubleshooting sections in each component README
2. Review test outputs for validation and debugging
3. Check integration status between Wrath Manager and Grim Observer
4. Ensure all dependencies and configurations are properly set up
5. Review the main project README for comprehensive guidance

---

**Note**: synced precision in example configurations

**"CROM does not hold your hand. He turns the heavens, and the earth answers in blood, frost, and shadow."**
