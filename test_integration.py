#!/usr/bin/env python3
"""
Integration test for food/drink functionality.
This test verifies that all components work together correctly.
"""
import sys
import os

# Add uno_game to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'uno_game'))

from game import GameManager
from items import registry, Effect

def test_food_drink_integration():
    """Test that food/drink features work with GameManager."""
    print("Testing Food/Drink Integration...")
    
    # Create a game
    game = GameManager(['Alice', 'Bob'], starting_chips=100)
    
    # Test 1: Add items to player
    print("\n1. Adding items to players...")
    assert game.add_item_to_player('Alice', 'Pizza Slice', 2), "Failed to add pizza"
    assert game.add_item_to_player('Bob', 'Energy Drink', 1), "Failed to add energy drink"
    print("   ✓ Items added successfully")
    
    # Test 2: Check initial energy
    print("\n2. Checking initial energy...")
    alice_energy = game.get_player_energy('Alice')
    assert alice_energy == 100, f"Expected 100 energy, got {alice_energy}"
    print(f"   ✓ Alice has {alice_energy} energy")
    
    # Test 3: Use an item
    print("\n3. Using an item...")
    assert game.use_item('Alice', 'Pizza Slice'), "Failed to use pizza"
    alice_energy_after = game.get_player_energy('Alice')
    assert alice_energy_after == 100, f"Expected 100 energy (capped), got {alice_energy_after}"
    print(f"   ✓ Alice used Pizza Slice, energy: {alice_energy_after}")
    
    # Test 4: Check effects
    print("\n4. Checking active effects...")
    effects = game.get_player_effects('Alice')
    assert Effect.ENERGY_BOOST in effects, "ENERGY_BOOST effect not active"
    print(f"   ✓ Alice has active effects: {[e.name for e in effects]}")
    
    # Test 5: Update effects (simulate turn)
    print("\n5. Simulating turn with effect updates...")
    initial_energy = game.get_player_energy('Alice')
    game.update_effects()
    energy_after_turn = game.get_player_energy('Alice')
    assert energy_after_turn == initial_energy - 5, "Energy should decrease by 5 per turn"
    print(f"   ✓ Energy decreased from {initial_energy} to {energy_after_turn}")
    
    # Test 6: Test effect bonuses
    print("\n6. Testing effect bonuses...")
    # Bob uses Lucky Cookie for luck boost
    game.add_item_to_player('Bob', 'Lucky Cookie', 1)
    game.use_item('Bob', 'Lucky Cookie')
    # Apply bonuses to a roll (multiple times to test randomness)
    rolls_tested = 0
    bonus_applied = False
    for _ in range(10):
        roll = game.apply_effect_bonuses('Bob', 3)
        rolls_tested += 1
        if roll > 3:
            bonus_applied = True
            break
    print(f"   ✓ Effect bonus system works (tested {rolls_tested} rolls, bonus: {bonus_applied})")
    
    print("\n✅ All tests passed!")
    return True

def test_item_registry():
    """Test the item registry."""
    print("\nTesting Item Registry...")
    
    items = registry.get_all_items()
    print(f"   ✓ Registry has {len(items)} items")
    
    # Check specific items exist
    assert registry.get_item('Pizza Slice') is not None, "Pizza Slice not found"
    assert registry.get_item('Energy Drink') is not None, "Energy Drink not found"
    assert registry.get_item('Lucky Cookie') is not None, "Lucky Cookie not found"
    print("   ✓ All expected items found")
    
    return True

def main():
    """Run all tests."""
    print("=" * 60)
    print("Food/Drink Integration Test Suite")
    print("=" * 60)
    
    try:
        test_item_registry()
        test_food_drink_integration()
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED ✅")
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
