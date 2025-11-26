# Refined Panda3D Integration Todo List

- [x] Remove all pygame window/screen initialization and rendering from main.py
- [x] Refactor main menu to use only Panda3D DirectGui
- [x] Refactor settings menu and all submenus to use only Panda3D DirectGui
- [x] Refactor game loop to use Panda3D tasks and DirectGui for all UI
- [x] Convert inventory, shop, and status displays to Panda3D DirectGui
- [x] Remove any remaining pygame event handling and replace with Panda3D input
- [x] Ensure all game state updates and transitions happen in the Panda3D window
- [x] Test and validate each menu and game state for seamless integration
- [x] Remove obsolete files (e.g., card.py) and unused pygame code
- [x] Final polish: window properties, icons, animations, and unified look

## Advanced UI Features
- [x] Animated Menu Backgrounds: Add subtle moving elements (e.g., chips, dice, cards) to menus for a lively feel.
- [x] Sound Effects for UI Actions: Play sounds on button clicks, menu transitions, and game events.
- [ ] Particle Effects: Use confetti or sparkles for win screens or special actions.
- [ ] Custom Fonts: Integrate a unique font for titles and buttons to enhance theme.
- [ ] Profile/Save System: Allow players to save progress, settings, and high scores.
- [ ] Accessibility Options: Add colorblind modes, adjustable text size, and audio cues.
- [ ] Tooltips and Help Popups: Provide quick help for new players on menus and game screens.
- [ ] Responsive Layouts: Ensure UI scales well on different screen sizes and resolutions.
- [ ] Achievements/Unlockables: Track and display achievements for replay value.
- [ ] Online/Local Multiplayer: Add support for playing with friends.

## Gameplay & Table UI
 - [x] Player Setup Screen: Let users select 1-4 players, enter names, and assign seats around the table.
 - [x] Table UI: Show all players/chips around a 3D table. Highlight the current player and animate camera transitions to their seat.
 - [x] Turn Flow:
    - [x] Player rolls dice (with physics and effects).
    - [x] Show result, allow shop/inventory actions.
    - [x] Pass turn (camera animates to next player).
    - [x] Shop/Inventory: After rolling, show a shop menu for buying/using items before ending turn.
    - [x] Game Logic: Handle all effects, chip updates, win/loss detection, and round transitions.
    - [x] Polish: Add sound, animations, and UI feedback for a complete experience.
    - [x] Local WiFi Play Button: Add a “Coming Soon” button for future multiplayer.

---
Use this file to track progress and add/remove steps as needed.
