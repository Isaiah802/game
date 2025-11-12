# Status Effects System

## Overview
The game now has a fully functional status effects system that applies consumable item effects to players during gameplay.

## How It Works

### Available Effects
1. **Energy Boost** ⚡ (Gold color)
   - Provides energy boost
   - Items: Pizza Slice, Energy Drink

2. **Luck Boost** 🍀 (Green color)
   - 15% chance to get a perfect Zanzibar roll (4-5-6)
   - Items: Lucky Cookie

3. **Focus Boost** 🎯 (Blue color)
   - Better concentration and decision making
   - Items: Brain Snack, Energy Drink, Focus Tea

4. **Mood Boost** 😊 (Pink color)
   - Happy mood effects
   - Items: Happy Juice

### Using Items
1. **During Gameplay**: Press `I` to open your inventory
2. **Select an Item**: Use arrow keys to navigate
3. **Use Item**: Press `ENTER` to consume the selected item
4. **Effects Applied**: The item's effects will be active for the specified number of turns

### Visual Indicators
- **Compact Display**: Small colored circles next to player names showing active effects
- **Turn Counter**: Number inside each circle shows remaining turns
- **Color Coding**: Each effect has a unique color for easy identification

### Game Mechanics
- Effects are applied when you use an item from inventory
- Effects last for a specific number of turns (defined by the item)
- Effects automatically expire after their duration
- Multiple effects can be active simultaneously
- **Luck Boost** actively affects dice rolls during gameplay

### Shop Integration
- Buy items from the shop (Press `S` during gameplay)
- Buying items **ADDS** chips to your total (moves you away from winning)
- Items are added to your inventory after purchase
- Use items strategically: benefit vs. distance from goal

## Technical Implementation

### Files Modified
1. `game/game_engine.py`:
   - Added `use_item()` method
   - Added `update_effects()` method
   - Added `get_active_effects()` and `has_effect()` methods
   - Modified `_simulate_player_turn()` to apply luck effects
   - Players now have `active_effects` dictionary

2. `ui/status_display.py` (NEW):
   - `StatusDisplay` class for rendering effects
   - Compact and full display modes
   - Color-coded effect indicators

3. `main.py`:
   - Integrated StatusDisplay into game loop
   - Effects shown next to player names
   - Real-time effect tracking

4. `ui/shop_menu.py`:
   - Fixed to add chips instead of subtract
   - Removed affordability check
   - Added debug output

### Effect Duration System
- Effects are tracked per player in `active_effects` dictionary
- Format: `{Effect: turns_remaining}`
- Decremented after each round
- Automatically removed when turns reach 0

## Controls
- `SPACE`: Roll dice / Play round
- `I`: Open Inventory
- `S`: Open Shop
- `TAB`: Switch current player
- `ESC`: Return to menu

## Strategy Tips
- Use Luck Boost before important rounds
- Stack multiple effects for maximum benefit
- Remember: buying items costs chips (moves you further from winning at 0)
- Save powerful items for critical moments
