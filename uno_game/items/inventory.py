"""
Module for managing player inventories and item usage.
"""
from typing import Dict, List, Optional
from .consumables import ConsumableItem, Effect

class Inventory:
    """Manages a player's inventory of food and drink items."""
    
    def __init__(self):
        """Initialize an empty inventory with no items or active effects."""
        self.items: Dict[str, int] = {}  # Item name -> quantity
        self.active_effects: Dict[Effect, int] = {}  # Effect -> turns remaining
    
    def add_item(self, item: ConsumableItem, quantity: int = 1):
        """Add an item to the inventory."""
        current = self.items.get(item.name, 0)
        self.items[item.name] = current + quantity
    
    def remove_item(self, item: ConsumableItem, quantity: int = 1) -> bool:
        """
        Remove an item from the inventory.
        Returns False if not enough items available.
        """
        current = self.items.get(item.name, 0)
        if current < quantity:
            return False
        
        self.items[item.name] = current - quantity
        if self.items[item.name] <= 0:
            del self.items[item.name]
        return True
    
    def get_item_quantity(self, item_name: str) -> int:
        """Get the quantity of a specific item."""
        return self.items.get(item_name, 0)
    
    def get_all_items(self) -> Dict[str, int]:
        """Get all items and their quantities."""
        return self.items.copy()
    
    def use_item(self, item: ConsumableItem) -> bool:
        """
        Use an item from the inventory.
        Returns True if the item was successfully used.
        """
        if not self.remove_item(item):
            return False
            
        # Apply effects
        for effect in item.effects:
            current_duration = self.active_effects.get(effect, 0)
            # Effects stack in duration
            self.active_effects[effect] = current_duration + item.duration
            
        return True
    
    def update_effects(self):
        """Update active effects (call each turn)."""
        expired = []
        for effect, turns in self.active_effects.items():
            self.active_effects[effect] = turns - 1
            if self.active_effects[effect] <= 0:
                expired.append(effect)
                
        for effect in expired:
            del self.active_effects[effect]
    
    def has_effect(self, effect: Effect) -> bool:
        """Check if a specific effect is active."""
        return effect in self.active_effects
    
    def get_effect_duration(self, effect: Effect) -> int:
        """Get remaining duration of an effect."""
        return self.active_effects.get(effect, 0)