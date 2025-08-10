# Discord Message Formatting Standard

> *"Consistency is the hallmark of quality. Both grim_observer and wrath_manager now share the same clean, card-like Discord message format."*

**Part of the Rando Server Management Suite**

---

## 🎯 **Standardization Goal**

Both `grim_observer` and `wrath_manager` now use the same Discord message formatting approach:
- **Clean, readable structure** with consistent emoji usage
- **Card-like presentation** that's easy to scan
- **Categorized information** for better organization
- **Visual indicators** for different types of data
- **No complex embeds** - simple text content that works everywhere

---

## 📊 **Before vs After Comparison**

### **Before (wrath_manager - Old Format)**
```
New Moon: safer world, lean harvest. Explore, build, and prepare.

Event Settings:
MaxAggroRange=7000
NPCMaxSpawnCapMultiplier=0.8
NPCRespawnMultiplier=1.2
PlayerHealthRegenSpeedScale=1.3
PlayerDamageTakenMultiplier=0.9
```

### **After (wrath_manager - New Standardized Format)**
```
New Moon: safer world, lean harvest. Explore, build, and prepare.

🌑 **New Moon - The Calm**
🌙 Illumination: 5.0%

**Event Settings:**

Combat:
• MaxAggroRange: 7000.0
• PlayerDamageTakenMultiplier: 0.9

Resources:
• HarvestAmountMultiplier: 1.0x ➖
• NPCMaxSpawnCapMultiplier: 0.8x 📉
• NPCRespawnMultiplier: 1.2x 📈

Player:
• PlayerHealthRegenSpeedScale: 1.3x 📈
```

---

## 🌙 **Moon Phase Formatting**

### **Phase Emojis & Names**
| Phase | Emoji | Display Name |
|-------|-------|--------------|
| New Moon | 🌑 | New Moon - The Calm |
| Waxing Crescent | 🌒 | Waxing Crescent - The Stirring |
| First Quarter | 🌓 | First Quarter - The Ascent |
| Waxing Gibbous | 🌔 | Waxing Gibbous - The Surge |
| Full Moon | 🌕 | Full Moon - The Hunt |
| Waning Gibbous | 🌖 | Waning Gibbous - The Fade |
| Last Quarter | 🌗 | Last Quarter - The Ebb |
| Waning Crescent | 🌘 | Waning Crescent - The Dusk |

### **Illumination Display**
```
🌙 Illumination: 95.0%
```

---

## ⚔️ **Event Status Formatting**

### **Single Event**
```
🎯 **Events Active:** Blood Moon - The Reckoning
```

### **Multiple Events**
```
⚔️ **Events Active:** Blood Moon - The Reckoning, Blue Moon - The Forgotten Prophecy
```

---

## 📊 **Settings Categorization**

### **Combat Settings**
- Damage multipliers
- Health settings
- Aggro ranges
- Purge levels
- Thrall settings

### **Resources Settings**
- Harvest amounts
- Spawn caps
- Respawn rates

### **Player Settings**
- Player stats
- Stamina settings
- Regeneration rates

### **World Settings**
- Storm settings
- Elder things
- Visibility distances

### **Other Settings**
- Any settings that don't fit the above categories

---

## 📈 **Value Formatting**

### **Multipliers**
- **Above 1.0:** `2.5x 📈` (increasing)
- **Below 1.0:** `0.8x 📉` (decreasing)
- **Equal to 1.0:** `1.0x ➖` (neutral)

### **Boolean Values**
- **True:** `✅`
- **False:** `❌`

### **Regular Numbers**
- **Integers:** `6`
- **Decimals:** `3.9`

---

## 🔄 **grim_observer Consistency**

### **Player Events (Already Standardized)**
```
🟢 **PlayerName** joined Server
⏰ 2024-01-15 14:30:25 • 👥 Player #5

🔴 **PlayerName** left Server  
⏰ 2024-01-15 16:45:12 • ⏱️ Session: 2h 15m
```

### **Empty Server Messages**
- Rich embeds with visual elements
- Map-specific theming
- Consistent emoji usage
- Clean, readable structure

---

## 🧪 **Testing the New Format**

### **Run the Test Script**
```bash
cd MoonTide/wrath_manager
python3 test_discord_formatting.py
```

### **Test Cases Included**
1. **Full Moon Event** - Complex event with multiple settings
2. **New Moon Calm** - Simple phase with basic settings  
3. **Waxing Crescent with Calendar Event** - Mixed settings and events

---

## ✅ **Benefits of Standardization**

### **For Users**
- **Consistent experience** across all Discord notifications
- **Easy to read** and understand at a glance
- **Professional appearance** that reflects server quality

### **For Developers**
- **Shared code patterns** between projects
- **Easier maintenance** with consistent formatting
- **Better testing** with standardized output

### **For Server Admins**
- **Clear information** about server state changes
- **Quick identification** of active events and phases
- **Professional communication** with players

---

## 🔧 **Implementation Details**

### **wrath_manager Changes**
- Updated `_post_discord_summary()` function
- Added helper functions for formatting
- Implemented categorization system
- Added visual indicators for values

### **grim_observer Consistency**
- Already follows the same principles
- Clean, simple text formatting
- Consistent emoji usage
- Map-specific theming

---

## 📝 **Future Enhancements**

### **Potential Additions**
- **Color coding** for different severity levels
- **Interactive elements** (if Discord supports them)
- **Rich media** integration (images, videos)
- **Custom themes** per server/map

### **Maintenance**
- **Regular testing** of formatting functions
- **User feedback** collection
- **Performance optimization** for large settings lists
- **Accessibility improvements** for screen readers

---

*This standardization ensures that all Discord messages from the Rando Server Management Suite maintain a consistent, professional appearance while providing clear, actionable information to server administrators and players.*
