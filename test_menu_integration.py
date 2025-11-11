#!/usr/bin/env python3
"""
Test script to verify menu integrations work correctly.
"""
import sys
import os

# Add uno_game to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'uno_game'))

import pygame
from game import GameManager
from items import registry, Inventory
from settings import Settings
from ui.keybindings_menu import KeybindingsMenu
from ui.shop_menu import ShopMenu
from ui.consumables_menu import ConsumablesMenu

def test_menu_instantiation():
    """Test that all menus can be instantiated."""
    print("Testing menu instantiation...")
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    
    # Test Settings
    print("\n1. Testing Settings...")
    settings = Settings()
    assert settings is not None
    assert 'inventory' in settings.keybindings
    print("   ✓ Settings initialized")
    
    # Test KeybindingsMenu
    print("\n2. Testing KeybindingsMenu...")
    keybindings_menu = KeybindingsMenu(screen, settings)
    assert keybindings_menu is not None
    assert keybindings_menu.selected_action is not None
    print("   ✓ KeybindingsMenu initialized")
    
    # Test ShopMenu
    print("\n3. Testing ShopMenu...")
    shop_menu = ShopMenu(screen, 100, settings)
    assert shop_menu is not None
    assert shop_menu.player_chips == 100
    print("   ✓ ShopMenu initialized")
    
    # Test ConsumablesMenu
    print("\n4. Testing ConsumablesMenu...")
    inventory = Inventory()
    consumables_menu = ConsumablesMenu(screen, inventory)
    assert consumables_menu is not None
    print("   ✓ ConsumablesMenu initialized")
    
    print("\n✅ All menus instantiated successfully!")
    return True

def test_shop_menu_integration():
    """Test shop menu integration with GameManager."""
    print("\nTesting shop menu integration...")
    
    # Create a game
    game = GameManager(['Alice', 'Bob'], starting_chips=200)
    
    # Test buying items through shop workflow
    print("\n1. Simulating shop purchase...")
    # Simulate buying an item
    item = registry.get_item('Pizza Slice')
    assert item is not None
    
    alice_chips = game.players['Alice']['chips']
    if alice_chips >= item.cost:
        # Deduct chips
        game.players['Alice']['chips'] -= item.cost
        # Add item to inventory
        assert game.add_item_to_player('Alice', item.name, 1)
        print(f"   ✓ Alice bought {item.name} for {item.cost} chips")
    
    # Verify chips were deducted
    assert game.players['Alice']['chips'] == alice_chips - item.cost
    print(f"   ✓ Chips deducted correctly: {alice_chips} -> {game.players['Alice']['chips']}")
    
    print("\n✅ Shop integration works correctly!")
    return True

def test_consumables_menu_integration():
    """Test consumables menu integration with GameManager."""
    print("\nTesting consumables menu integration...")
    
    # Create a game
    game = GameManager(['Alice', 'Bob'], starting_chips=100)
    
    # Add items to player
    print("\n1. Adding items to player...")
    assert game.add_item_to_player('Alice', 'Pizza Slice', 2)
    assert game.add_item_to_player('Alice', 'Energy Drink', 1)
    print("   ✓ Items added to Alice's inventory")
    
    # Verify inventory
    player_data = game.players['Alice']
    assert 'inventory' in player_data
    inventory = player_data['inventory']
    
    print("\n2. Checking inventory contents...")
    pizza_qty = inventory.get_item_quantity('Pizza Slice')
    drink_qty = inventory.get_item_quantity('Energy Drink')
    assert pizza_qty == 2, f"Expected 2 pizzas, got {pizza_qty}"
    assert drink_qty == 1, f"Expected 1 drink, got {drink_qty}"
    print(f"   ✓ Inventory correct: {pizza_qty} pizzas, {drink_qty} drinks")
    
    # Test using an item
    print("\n3. Testing item usage...")
    assert game.use_item('Alice', 'Pizza Slice')
    pizza_qty_after = inventory.get_item_quantity('Pizza Slice')
    assert pizza_qty_after == 1, f"Expected 1 pizza after use, got {pizza_qty_after}"
    print("   ✓ Item used successfully, quantity updated")
    
    print("\n✅ Consumables integration works correctly!")
    return True

def test_keybindings_menu():
    """Test keybindings menu functionality."""
    print("\nTesting keybindings menu...")
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    
    settings = Settings()
    
    print("\n1. Testing default keybindings...")
    assert settings.get_key('inventory') == pygame.K_i
    assert settings.get_key('roll_dice') == pygame.K_SPACE
    assert settings.get_key('menu') == pygame.K_ESCAPE
    print("   ✓ Default keybindings loaded")
    
    print("\n2. Testing keybinding modification...")
    settings.set_key('inventory', pygame.K_TAB)
    assert settings.get_key('inventory') == pygame.K_TAB
    print("   ✓ Keybinding modified successfully")
    
    print("\n3. Testing keybinding reset...")
    settings.reset_keybindings()
    assert settings.get_key('inventory') == pygame.K_i
    print("   ✓ Keybindings reset to defaults")
    
    print("\n✅ Keybindings menu works correctly!")
    return True

def main():
    """Run all menu integration tests."""
    print("=" * 60)
    print("Menu Integration Test Suite")
    print("=" * 60)
    
    try:
        test_menu_instantiation()
        test_shop_menu_integration()
        test_consumables_menu_integration()
        test_keybindings_menu()
        
        print("\n" + "=" * 60)
        print("ALL MENU INTEGRATION TESTS PASSED ✅")
        print("=" * 60)
        return 0
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
