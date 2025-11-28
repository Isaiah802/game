"""
Module for managing player inventories and item usage.
"""
from typing import Dict, List, Optional
from .consumables import ConsumableItem, Effect

class Inventory:
    """Manages a player's inventory of food and drink items."""
    
    def __init__(self):
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
    
    def use_item(self, item: ConsumableItem, external_effects: Optional[Dict[Effect, int]] = None) -> bool:
        """Consume an item and apply effects.

        If `external_effects` is provided (e.g. a player's active_effects dict),
        durations stack into that mapping instead of the inventory's local
        `active_effects`. This keeps player effect state unified with game logic.
        """
        if not self.remove_item(item):
            return False

        target = external_effects if external_effects is not None else self.active_effects
        for effect in item.effects:
            current_duration = target.get(effect, 0)
            target[effect] = current_duration + item.duration
        return True

    # Convenience helpers
    def add_item_by_name(self, name: str, quantity: int = 1):
        from .consumables import registry
        itm = registry.get_item(name)
        if itm:
            self.add_item(itm, quantity)

    def remove_item_by_name(self, name: str, quantity: int = 1) -> bool:
        from .consumables import registry
        itm = registry.get_item(name)
        return self.remove_item(itm, quantity) if itm else False

    def apply_item_effects_to(self, item: ConsumableItem, dest_effects: Dict[Effect, int]):
        for effect in item.effects:
            dest_effects[effect] = dest_effects.get(effect, 0) + item.duration

    def summary(self) -> str:
        parts = [f"{name} x{qty}" for name, qty in sorted(self.items.items())]
        return ", ".join(parts) if parts else "(empty)"
    
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