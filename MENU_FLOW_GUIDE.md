# Game Menu Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      GAME LAUNCHER                          │
│                    (Intro Screen)                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    START MENU                               │
│  ┌────────────────────────────────────────────────────┐    │
│  │  [Play]                                             │    │
│  │  [Audio Settings]                                   │    │
│  │  [Change Song]                                      │    │
│  │  [Keybindings] ◄─── NEW: Opens keybindings menu    │    │
│  │  [Quit]                                             │    │
│  └────────────────────────────────────────────────────┘    │
└───────┬──────────────────────┬──────────────────────────────┘
        │                      │
        │ [Play]               │ [Keybindings]
        │                      │
        ▼                      ▼
┌─────────────────────   ┌─────────────────────────────────┐
│   PRE-GAME SETUP   │   │   KEYBINDINGS MENU              │
│  - Add players     │   │  - View current bindings        │
│  - Set chips       │   │  - Change any binding           │
│  - Start game      │   │  - Reset to defaults            │
└─────┬──────────────┘   │  - Press R to reset all         │
      │                  └─────────────────────────────────┘
      │ [Start]
      ▼
┌─────────────────────────────────────────────────────────────┐
│                    GAMEPLAY SCREEN                          │
│                                                             │
│  Controls: Space=roll | I=inventory | S=shop | Tab=switch  │
│           player | Esc=menu                                │
│                                                             │
│  Player Display:                                            │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ Alice: 200 chips   [Dice: 4 5 6] Zanzibar!         │  │
│  │ Bob:   150 chips   [Dice: 3 3 3] Three of a Kind   │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
│  Current player (for menus): Alice                         │
│                                                             │
└────┬──────────────┬──────────────┬────────────────────────┘
     │              │              │
     │ Press 'I'    │ Press 'S'    │ Press Tab
     ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐
│ CONSUMABLES  │ │  SHOP MENU   │ │ Switch Active Player │
│    MENU      │ │              │ │ Alice → Bob → ...    │
│              │ │              │ └──────────────────────┘
│ Your Items:  │ │ Your chips:  │
│ - Pizza x2   │ │ 200 chips    │
│ - Energy x1  │ │              │
│              │ │ Food Items:  │
│ [Use Item]   │ │ - Pizza      │
│              │ │   (100 chips)│
│              │ │ - Cookie     │
│              │ │   (150 chips)│
│              │ │              │
│              │ │ [Buy Item]   │
└──────────────┘ └──────────────┘
      │                │
      │ [Use]          │ [Buy]
      ▼                ▼
   Update            Deduct chips
   Player            Add to inventory
   Effects           Show message
```

## Menu Integration Details

### 1. Keybindings Menu (Main Menu)
**Access**: Click "Keybindings" button in start menu
**Features**:
- View all current keybindings
- Select any binding to change
- Press Enter to rebind selected action
- Press R to reset all to defaults
- Press Esc to return to menu

### 2. Shop Menu (In-Game)
**Access**: Press 'S' during gameplay
**Features**:
- Browse available food/drink items
- See item descriptions and costs
- Purchase items with chips
- Items automatically added to inventory
- Chips automatically deducted
- Visual confirmation of purchase

**Flow**:
1. Player presses 'S'
2. Shop menu appears over game
3. Use arrow keys to navigate items
4. Press Enter to purchase selected item
5. If enough chips: purchase completes
6. If not enough chips: error message shown
7. Press Esc to close shop

### 3. Consumables/Inventory Menu (In-Game)
**Access**: Press 'I' during gameplay
**Features**:
- View all items in player's inventory
- See item quantities
- See item descriptions and effects
- Use items to gain bonuses
- Items removed from inventory when used

**Flow**:
1. Player presses 'I'
2. Consumables menu appears over game
3. Shows only items player owns (quantity > 0)
4. Use arrow keys to navigate items
5. Press Enter to use selected item
6. Item effect applied to player
7. Quantity decremented
8. Visual confirmation shown
9. Press Esc to close menu

### 4. Player Switching (In-Game)
**Access**: Press Tab during gameplay
**Features**:
- Cycles through all players
- Shows current player at bottom of screen
- Determines which player's inventory/chips used for menus
- Essential for multiplayer games

**Flow**:
1. Player presses Tab
2. Active player switches to next in order
3. Display updates to show new active player
4. Next menu action (I or S) uses new player's data

## Code Integration Points

### Main Menu Loop (main.py: ~464-515)
```python
while True:
    choice = menu.run()
    if choice == 'keybindings':
        keybindings_menu = KeybindingsMenu(screen, settings)
        # Run keybindings menu loop
```

### Game Loop (main.py: ~331-436)
```python
while running:
    for event in pygame.event.get():
        if event.key == pygame.K_i:
            # Open consumables menu for current player
            # Show inventory items
            # Handle item usage
            
        elif event.key == pygame.K_s:
            # Open shop menu for current player
            # Handle purchases
            # Update chips and inventory
            
        elif event.key == pygame.K_TAB:
            # Switch to next player
            # Update display
```

## UI Assets Used

All UI assets mentioned in the requirements are present:
- `assets/ui/casino_background.jpg` - Used in intro screen
- `assets/ui/custom_background.jpg` - Available for future use
- `assets/ui/versus.png` - Available for future use

## Implementation Notes

1. **Settings Persistence**: Keybindings are saved to `keybindings.json` and persist between game sessions

2. **Player Context**: Tab key determines which player's data is used for shop/inventory actions in multiplayer

3. **Visual Feedback**: All menu actions show temporary messages confirming success/failure

4. **Menu Overlay**: Menus render over the game screen, allowing players to see game state while browsing

5. **Inventory Integration**: Seamless integration with existing FoodDrinkMixin from previous work
